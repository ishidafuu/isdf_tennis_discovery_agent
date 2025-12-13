"""
Message processing handlers for Discord bot (REFACTORED).

Significantly reduced code duplication using:
- Centralized embed builder (SessionEmbedBuilder)
- Unified media helpers (build_media_markdown, push_media_memo_to_github)
- Common message utilities (message_utils)
- Type-safe scene detection (get_scene_info)
"""
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from datetime import datetime

import discord

from src.bot.channel_handler import get_scene_info, is_reflection_channel
from src.bot.helpers.media_utils import extract_urls
from src.bot.helpers.message_utils import (
    send_thinking_message,
    update_thinking_message,
    send_session_embed,
    handle_message_error,
)
from src.bot.helpers.markdown_helpers import (
    build_media_markdown,
    push_media_memo_to_github,
)
from src.bot.helpers.embed_builder import SessionEmbedBuilder
from src.bot.helpers.output_channel import post_detailed_analysis, post_followup_question
from src.models.session import PracticeSession
from src.constants import MAX_FILE_SIZE_BYTES

if TYPE_CHECKING:
    from src.bot.client import TennisDiscoveryBot


async def process_voice_message(
    bot: "TennisDiscoveryBot",
    message: discord.Message,
    attachment: discord.Attachment
) -> None:
    """
    Process a voice message attachment.

    Transcribes audio using Gemini, extracts practice session data,
    and saves to GitHub.

    Args:
        bot: TennisDiscoveryBot instance
        message: Discord message object
        attachment: Audio attachment
    """
    tmp_path = None
    try:
        # Detect scene
        scene_info = get_scene_info(message.channel.name)

        # Send thinking message
        thinking_msg = await send_thinking_message(message, scene_info, "音声を処理中")

        # Download audio file to temporary location
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(attachment.filename).suffix
        ) as tmp_file:
            tmp_path = tmp_file.name
            await attachment.save(tmp_path)

        if bot.debug:
            print(f"📥 Downloaded audio file: {attachment.filename} ({attachment.size} bytes)")
            print(f"🎬 Detected scene: {scene_info.name} ({scene_info.type})")

        # Transcribe audio first to check tennis relevance
        await update_thinking_message(thinking_msg, "🎙️ 音声を文字起こし中...")

        # Upload audio file and transcribe
        import google.generativeai as genai
        audio_file = genai.upload_file(path=tmp_path)
        transcribe_response = bot.gemini_client.model.generate_content([
            bot.gemini_client.SYSTEM_PROMPT,
            "以下の音声を文字起こししてください。話者の言葉をそのまま記録してください。",
            audio_file
        ])
        transcript = transcribe_response.text.strip()

        # Check if content is tennis-related
        await update_thinking_message(thinking_msg, "🔍 テニス関連の内容か確認中...")
        is_tennis = await bot.gemini_client.is_tennis_related(transcript)

        if not is_tennis:
            # Delete thinking message
            await thinking_msg.delete()
            # React with ❓ to indicate non-tennis content
            await message.add_reaction("❓")
            # Clean up temporary file
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)
            return

        # Process with Gemini (scene-aware) - using already transcribed text
        await update_thinking_message(thinking_msg, f"🧠 Geminiで分析中... (シーン: {scene_info.name})")
        session, scene_data = await bot.gemini_client.process_voice_message(tmp_path, scene_info.type)

        if bot.debug:
            print(f"✅ Session processed: {session.condition}, {len(session.success_patterns)} successes")

        # Build and save markdown locally (optional, for debugging)
        if bot.debug:
            local_path = bot.markdown_builder.save(
                session,
                bot.markdown_builder.get_filename_for_session(session, scene_info.name)
            )
            print(f"💾 Saved locally: {local_path}")

        # Push to GitHub (without scene name, as scenes are no longer used)
        await update_thinking_message(thinking_msg, "📤 GitHubにアップロード中...")
        try:
            file_url = bot.github_sync.push_session(session, scene_name="practice")
        except Exception as e:
            # Delete thinking message and react with error
            await thinking_msg.delete()
            await message.add_reaction("❌")
            if bot.debug:
                print(f"❌ Failed to push to GitHub: {e}")
            # Clean up temporary file
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)
            return

        # Clean up temporary file
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
            tmp_path = None

        # Delete thinking message
        await thinking_msg.delete()

        # Reply with summary only
        summary_text = session.summary if session.summary else "メモを記録しました"
        await message.reply(f"📝 {summary_text}")

        # Post detailed analysis to output channel
        await post_detailed_analysis(
            bot=bot,
            session=session,
            user_name=message.author.display_name,
            timestamp=session.date
        )

        # Generate and post follow-up question to output channel
        if session.success_patterns or session.failure_patterns:
            followup = await bot.gemini_client.generate_followup_question(session)
            if followup:
                await post_followup_question(
                    bot=bot,
                    question=followup,
                    user_mention=message.author.mention
                )

    except Exception as e:
        await handle_message_error(message, e, bot.debug, "voice message processing")

    finally:
        # Clean up temporary file if it still exists
        if tmp_path and Path(tmp_path).exists():
            Path(tmp_path).unlink(missing_ok=True)


async def process_text_message(
    bot: "TennisDiscoveryBot",
    message: discord.Message
) -> None:
    """
    Process a text message.

    Extracts URLs, analyzes text content with Gemini,
    and saves to GitHub.

    Args:
        bot: TennisDiscoveryBot instance
        message: Discord message object
    """
    try:
        # Detect scene
        scene_info = get_scene_info(message.channel.name)

        # Extract URLs
        urls = extract_urls(message.content)

        # Send thinking message
        thinking_msg = await send_thinking_message(message, scene_info, "テキストを処理中")

        if bot.debug:
            print(f"📄 Processing text message in channel: {message.channel.name}")
            print(f"🎬 Detected scene: {scene_info.name} ({scene_info.type})")
            if urls:
                print(f"🔗 Found URLs: {urls}")

        # Check if content is tennis-related
        await update_thinking_message(thinking_msg, "🔍 テニス関連の内容か確認中...")
        is_tennis = await bot.gemini_client.is_tennis_related(message.content)

        if not is_tennis:
            # Delete thinking message
            await thinking_msg.delete()
            # React with ❓ to indicate non-tennis content
            await message.add_reaction("❓")
            return

        # Process with Gemini (scene-aware)
        await update_thinking_message(thinking_msg, f"🧠 Geminiで分析中... (シーン: {scene_info.name})")
        session, scene_data = await bot.gemini_client.process_text_message(
            message.content,
            scene_info.type,
            urls
        )

        if bot.debug:
            print(f"✅ Text processed: {len(scene_data.get('tags', []))} tags")

        # Push to GitHub (without scene name, as scenes are no longer used)
        await update_thinking_message(thinking_msg, "📤 GitHubにアップロード中...")
        try:
            file_url = bot.github_sync.push_session(session, scene_name="practice")
        except Exception as e:
            # Delete thinking message and react with error
            await thinking_msg.delete()
            await message.add_reaction("❌")
            if bot.debug:
                print(f"❌ Failed to push to GitHub: {e}")
            return

        # Delete thinking message
        await thinking_msg.delete()

        # React with ✅ to indicate success
        await message.add_reaction("✅")

        # Post detailed analysis to output channel
        await post_detailed_analysis(
            bot=bot,
            session=session,
            user_name=message.author.display_name,
            timestamp=session.date
        )

        # Generate and post follow-up question to output channel
        if session.success_patterns or session.failure_patterns:
            followup = await bot.gemini_client.generate_followup_question(session)
            if followup:
                await post_followup_question(
                    bot=bot,
                    question=followup,
                    user_mention=message.author.mention
                )

    except Exception as e:
        await handle_message_error(message, e, bot.debug, "text message processing")


async def process_image_message(
    bot: "TennisDiscoveryBot",
    message: discord.Message,
    attachment: discord.Attachment
) -> None:
    """
    Process an image message attachment.

    Saves image to vault, generates markdown memo,
    and pushes to GitHub.

    Args:
        bot: TennisDiscoveryBot instance
        message: Discord message object
        attachment: Image attachment
    """
    try:
        # File size check
        if attachment.size > MAX_FILE_SIZE_BYTES:
            await message.reply("❌ ファイルサイズが大きすぎます（上限20MB）")
            return

        # Detect scene
        scene_info = get_scene_info(message.channel.name)

        # Send thinking message
        thinking_msg = await send_thinking_message(message, scene_info, "画像を保存中")

        # Get vault path from environment
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault")
        attachments_dir = Path(vault_path) / "attachments"

        # Generate filename: YYYY-MM-DD_シーン名_HHMMSS.ext
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        ext = Path(attachment.filename).suffix
        filename = f"{date_str}_{scene_info.name}_{time_str}{ext}"

        # Create date-based subdirectory
        date_dir = attachments_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Download and save image
        image_path = date_dir / filename
        await attachment.save(image_path)

        if bot.debug:
            print(f"📥 Downloaded image: {attachment.filename} ({attachment.size} bytes)")
            print(f"💾 Saved to: {image_path}")
            print(f"🎬 Detected scene: {scene_info.name} ({scene_info.type})")

        # Create memo data
        memo_data = {
            'date': date_str,
            'scene': scene_info.name,
            'input_type': 'image',
            'file_path': f"attachments/{date_str}/{filename}",
            'user_comment': message.content if message.content else "",
            'tags': ['tennis', scene_info.type, 'image']
        }

        # Build markdown for image memo
        await update_thinking_message(thinking_msg, f"📝 Markdownを生成中... (シーン: {scene_info.name})")
        markdown_content = build_media_markdown(memo_data, scene_info.name, "image")

        # Create PracticeSession object for GitHub push
        session = PracticeSession(
            raw_transcript=f"画像メモ: {message.content if message.content else '(コメントなし)'}",
            summary=f"画像メモ ({scene_info.name})",
            tags=memo_data['tags']
        )
        session.date = now

        # Push to GitHub
        await update_thinking_message(thinking_msg, "📤 GitHubにアップロード中...")
        file_url = push_media_memo_to_github(
            bot.github_sync, session, markdown_content, scene_info.name, "image"
        )

        # Create success embed
        embed = SessionEmbedBuilder.build_image_embed(
            scene_info=scene_info,
            date=now,
            filename=filename,
            user_comment=memo_data['user_comment'] or "画像を記録しました",
            file_url=file_url,
        )

        sent_message = await thinking_msg.edit(content=None, embed=embed)

    except Exception as e:
        await handle_message_error(message, e, bot.debug, "image message processing")


async def process_video_message(
    bot: "TennisDiscoveryBot",
    message: discord.Message,
    attachment: discord.Attachment
) -> None:
    """
    Process a video message attachment.

    Saves video to vault, generates markdown memo,
    and pushes to GitHub.

    Args:
        bot: TennisDiscoveryBot instance
        message: Discord message object
        attachment: Video attachment
    """
    try:
        # File size check
        if attachment.size > MAX_FILE_SIZE_BYTES:
            await message.reply("❌ ファイルサイズが大きすぎます（上限20MB）")
            return

        # Detect scene
        scene_info = get_scene_info(message.channel.name)

        # Send thinking message
        thinking_msg = await send_thinking_message(message, scene_info, "動画を保存中")

        # Get vault path from environment
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault")
        attachments_dir = Path(vault_path) / "attachments"

        # Generate filename: YYYY-MM-DD_シーン名_HHMMSS.ext
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        ext = Path(attachment.filename).suffix
        filename = f"{date_str}_{scene_info.name}_{time_str}{ext}"

        # Create date-based subdirectory
        date_dir = attachments_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Download and save video
        video_path = date_dir / filename
        await attachment.save(video_path)

        if bot.debug:
            print(f"📥 Downloaded video: {attachment.filename} ({attachment.size} bytes)")
            print(f"💾 Saved to: {video_path}")
            print(f"🎬 Detected scene: {scene_info.name} ({scene_info.type})")

        # Create memo data
        memo_data = {
            'date': date_str,
            'scene': scene_info.name,
            'input_type': 'video',
            'file_path': f"attachments/{date_str}/{filename}",
            'user_comment': message.content if message.content else "",
            'tags': ['tennis', scene_info.type, 'video']
        }

        # Build markdown for video memo
        await update_thinking_message(thinking_msg, f"📝 Markdownを生成中... (シーン: {scene_info.name})")
        markdown_content = build_media_markdown(memo_data, scene_info.name, "video")

        # Create PracticeSession object for GitHub push
        session = PracticeSession(
            raw_transcript=f"動画メモ: {message.content if message.content else '(コメントなし)'}",
            summary=f"動画メモ ({scene_info.name})",
            tags=memo_data['tags']
        )
        session.date = now

        # Push to GitHub
        await update_thinking_message(thinking_msg, "📤 GitHubにアップロード中...")
        file_url = push_media_memo_to_github(
            bot.github_sync, session, markdown_content, scene_info.name, "video"
        )

        # Create success embed
        embed = SessionEmbedBuilder.build_video_embed(
            scene_info=scene_info,
            date=now,
            filename=filename,
            user_comment=memo_data['user_comment'] or "動画を記録しました",
            file_url=file_url,
        )

        sent_message = await thinking_msg.edit(content=None, embed=embed)

    except Exception as e:
        await handle_message_error(message, e, bot.debug, "video message processing")


async def process_reflection_message(
    bot: "TennisDiscoveryBot",
    message: discord.Message
) -> None:
    """
    Process a reflection/review message for appending to previous memos.

    Uses fuzzy search to find matching previous memos and appends
    the reflection content to them.

    Args:
        bot: TennisDiscoveryBot instance
        message: Discord message object
    """
    try:
        # Send thinking message
        thinking_msg = await message.reply("🔍 過去のメモを検索中...")

        if bot.debug:
            print(f"📝 Processing reflection message: {message.content[:100]}")

        # Extract date and keywords from message
        date_text = None
        keywords = []

        # Simple keyword extraction (words longer than 2 characters)
        words = message.content.split()
        for word in words:
            # Skip common Japanese particles and connectors
            if word not in ["です", "ます", "した", "でした", "から", "ので", "けど", "が", "は", "を", "に", "で", "と"]:
                if len(word) > 2:
                    keywords.append(word)

        # Use fuzzy search to find matching memos
        await update_thinking_message(thinking_msg, "🔍 関連するメモを探しています...")
        candidates = bot.obsidian_manager.find_memo_by_fuzzy_criteria(
            date_text=message.content,  # Let ObsidianManager extract date
            keywords=keywords[:5],  # Limit to top 5 keywords
            scene_name=None  # Search across all scenes
        )

        if not candidates:
            await thinking_msg.edit(
                content="❌ 該当するメモが見つかりませんでした。\n日付やキーワードを含めてもう一度お試しください。"
            )
            return

        # Use the most recent match
        target_memo = candidates[0]

        if bot.debug:
            print(f"✅ Found target memo: {target_memo.get('file_name')}")

        # Append reflection to the memo
        await update_thinking_message(thinking_msg, "📝 追記を保存中...")
        success = bot.obsidian_manager.append_to_memo(
            file_path=target_memo['file_path'],
            append_text=message.content,
            section_title="振り返り・追記"
        )

        if not success:
            await thinking_msg.edit(content="❌ 追記の保存に失敗しました。")
            return

        # Push updated memo to GitHub
        await update_thinking_message(thinking_msg, "📤 GitHubにアップロード中...")
        file_url = None
        try:
            with open(target_memo['file_path'], 'r', encoding='utf-8') as f:
                updated_content = f.read()

            # Extract date from target memo for commit message
            target_date = target_memo.get('date', 'unknown')
            target_scene = target_memo.get('scene', '不明')

            # Push to GitHub
            commit_message = f"Append reflection: {target_date} ({target_scene})"
            file_url = bot.github_sync._push_file(
                file_path=target_memo['file_path'].replace(str(bot.obsidian_manager.vault_path) + "/", ""),
                content=updated_content,
                commit_message=commit_message
            )
        except Exception as e:
            if bot.debug:
                print(f"Error pushing to GitHub: {e}")

        # Create success embed
        embed = SessionEmbedBuilder.build_reflection_embed(
            target_date=target_memo.get('date', 'unknown'),
            target_scene=target_memo.get('scene', '不明'),
            target_filename=target_memo.get('file_name', ''),
            append_content=message.content,
            file_url=file_url,
            other_candidates=candidates[1:] if len(candidates) > 1 else None,
        )

        await thinking_msg.edit(content=None, embed=embed)

    except Exception as e:
        await handle_message_error(message, e, bot.debug, "reflection message processing")
