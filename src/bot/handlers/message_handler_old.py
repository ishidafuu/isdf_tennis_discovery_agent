"""
Message processing handlers for Discord bot.

Contains the 5 main message processing functions:
- process_voice_message: Handle audio attachments
- process_text_message: Handle text messages
- process_reflection_message: Handle reflection/review channel messages
- process_image_message: Handle image attachments
- process_video_message: Handle video attachments
"""
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import discord

from src.bot.channel_handler import detect_scene_from_channel, get_scene_emoji, is_reflection_channel
from src.bot.helpers.media_utils import extract_urls
from src.bot.helpers.previous_log import get_previous_log_summary
from src.bot.helpers.markdown_helpers import (
    build_image_markdown,
    build_video_markdown,
    push_image_memo_to_github,
    push_video_memo_to_github,
)
from src.models.session import PracticeSession

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
    try:
        # Detect scene from channel name
        channel_name = message.channel.name
        scene_type, scene_name = detect_scene_from_channel(channel_name)
        scene_emoji = get_scene_emoji(scene_type)

        # Send "thinking" message
        thinking_msg = await message.reply(f"{scene_emoji} 音声を処理中... (シーン: {scene_name})")

        # Download audio file to temporary location
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(attachment.filename).suffix
        ) as tmp_file:
            tmp_path = tmp_file.name
            await attachment.save(tmp_path)

        if bot.debug:
            print(f"📥 Downloaded audio file: {attachment.filename} ({attachment.size} bytes)")
            print(f"🎬 Detected scene: {scene_name} ({scene_type})")

        # Process with Gemini (scene-aware)
        await thinking_msg.edit(content=f"🧠 Geminiで分析中... (シーン: {scene_name})")
        session, scene_data = await bot.gemini_client.process_voice_message(tmp_path, scene_type)

        if bot.debug:
            print(f"✅ Session processed: {session.condition}, {len(session.success_patterns)} successes")

        # Build and save markdown locally (optional, for debugging)
        if bot.debug:
            local_path = bot.markdown_builder.save(session,
                                                   bot.markdown_builder.get_filename_for_session(session, scene_name))
            print(f"💾 Saved locally: {local_path}")

        # Push to GitHub (with scene name)
        await thinking_msg.edit(content="📤 GitHubにアップロード中...")
        file_url = bot.github_sync.push_session(session, scene_name=scene_name)

        # Clean up temporary file
        Path(tmp_path).unlink(missing_ok=True)

        # Get previous log summary
        previous_log = get_previous_log_summary(bot.obsidian_manager, scene_name, bot.debug)

        # Create success embed
        embed = discord.Embed(
            title=f"{scene_emoji} {scene_name}の記録を保存しました",
            description=session.summary or "音声メッセージを記録しました",
            color=discord.Color.green()
        )

        # Add previous log if available
        if previous_log:
            embed.add_field(
                name="🔄 サイクル",
                value=previous_log,
                inline=False
            )

        # Add fields
        if session.somatic_marker:
            embed.add_field(
                name="🎯 身体感覚",
                value=session.somatic_marker,
                inline=False
            )

        if session.success_patterns:
            success_text = "\n".join([
                f"• {p.description}" for p in session.success_patterns[:3]
            ])
            embed.add_field(
                name="🟩 成功パターン",
                value=success_text,
                inline=False
            )

        if session.next_actions:
            next_text = "\n".join([
                f"• {a.theme}" for a in session.next_actions[:3]
            ])
            embed.add_field(
                name="🟦 次回のテーマ",
                value=next_text,
                inline=False
            )

        embed.add_field(
            name="📁 GitHub",
            value=f"[ファイルを見る]({file_url})",
            inline=False
        )

        embed.set_footer(text=f"📅 {session.date.strftime('%Y年%m月%d日')}")

        await thinking_msg.edit(content=None, embed=embed)

        # Generate and send follow-up question (optional, for deepening reflection)
        if session.success_patterns or session.failure_patterns:
            followup = await bot.gemini_client.generate_followup_question(session)
            if followup:
                await message.reply(f"💭 {followup}")

    except Exception as e:
        error_msg = f"❌ エラーが発生しました: {str(e)}"
        print(f"Error processing voice message: {e}")

        if bot.debug:
            import traceback
            traceback.print_exc()

        await message.reply(error_msg)

    finally:
        # Clean up temporary file if it still exists
        if 'tmp_path' in locals():
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
        # Detect scene from channel name
        channel_name = message.channel.name
        scene_type, scene_name = detect_scene_from_channel(channel_name)
        scene_emoji = get_scene_emoji(scene_type)

        # Extract URLs
        urls = extract_urls(message.content)

        # Send "thinking" message
        thinking_msg = await message.reply(f"📝 テキストを処理中... (シーン: {scene_name})")

        if bot.debug:
            print(f"📄 Processing text message in channel: {channel_name}")
            print(f"🎬 Detected scene: {scene_name} ({scene_type})")
            if urls:
                print(f"🔗 Found URLs: {urls}")

        # Process with Gemini (scene-aware)
        await thinking_msg.edit(content=f"🧠 Geminiで分析中... (シーン: {scene_name})")
        session, scene_data = await bot.gemini_client.process_text_message(
            message.content,
            scene_type,
            urls
        )

        if bot.debug:
            print(f"✅ Text processed: {len(scene_data.get('tags', []))} tags")

        # Push to GitHub (with scene name)
        await thinking_msg.edit(content="📤 GitHubにアップロード中...")
        file_url = bot.github_sync.push_session(session, scene_name=scene_name)

        # Get previous log summary
        previous_log = get_previous_log_summary(bot.obsidian_manager, scene_name, bot.debug)

        # Create success embed
        embed = discord.Embed(
            title=f"{scene_emoji} {scene_name}のテキストメモを保存しました",
            description=session.summary or "テキストメッセージを記録しました",
            color=discord.Color.blue()
        )

        # Add previous log if available
        if previous_log:
            embed.add_field(
                name="🔄 サイクル",
                value=previous_log,
                inline=False
            )

        # Add URLs if present
        if urls:
            url_text = "\n".join([f"• {url}" for url in urls[:3]])
            embed.add_field(
                name="🔗 参考URL",
                value=url_text,
                inline=False
            )

        # Add fields from session
        if session.somatic_marker:
            embed.add_field(
                name="🎯 身体感覚",
                value=session.somatic_marker,
                inline=False
            )

        if session.success_patterns:
            success_text = "\n".join([
                f"• {p.description}" for p in session.success_patterns[:3]
            ])
            embed.add_field(
                name="🟩 成功パターン",
                value=success_text,
                inline=False
            )

        if session.next_actions:
            next_text = "\n".join([
                f"• {a.theme}" for a in session.next_actions[:3]
            ])
            embed.add_field(
                name="🟦 次回のテーマ",
                value=next_text,
                inline=False
            )

        embed.add_field(
            name="📁 GitHub",
            value=f"[ファイルを見る]({file_url})",
            inline=False
        )

        embed.set_footer(text=f"📅 {session.date.strftime('%Y年%m月%d日')}")

        await thinking_msg.edit(content=None, embed=embed)

    except Exception as e:
        error_msg = f"❌ エラーが発生しました: {str(e)}"
        print(f"Error processing text message: {e}")

        if bot.debug:
            import traceback
            traceback.print_exc()

        await message.reply(error_msg)


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
        # Send "thinking" message
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
        await thinking_msg.edit(content="🔍 関連するメモを探しています...")
        candidates = bot.obsidian_manager.find_memo_by_fuzzy_criteria(
            date_text=message.content,  # Let ObsidianManager extract date
            keywords=keywords[:5],  # Limit to top 5 keywords
            scene_name=None  # Search across all scenes
        )

        if not candidates:
            await thinking_msg.edit(content="❌ 該当するメモが見つかりませんでした。\n日付やキーワードを含めてもう一度お試しください。")
            return

        # Use the most recent match
        target_memo = candidates[0]

        if bot.debug:
            print(f"✅ Found target memo: {target_memo.get('file_name')}")

        # Append reflection to the memo
        await thinking_msg.edit(content="📝 追記を保存中...")
        success = bot.obsidian_manager.append_to_memo(
            file_path=target_memo['file_path'],
            append_text=message.content,
            section_title="振り返り・追記"
        )

        if not success:
            await thinking_msg.edit(content="❌ 追記の保存に失敗しました。")
            return

        # Push updated memo to GitHub
        await thinking_msg.edit(content="📤 GitHubにアップロード中...")
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
            file_url = None

        # Create success embed
        embed = discord.Embed(
            title="📝 振り返りメモを追記しました",
            description=f"**{target_date}** の **{target_scene}** メモに追記",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="📄 追記したメモ",
            value=f"`{target_memo.get('file_name')}`",
            inline=False
        )

        embed.add_field(
            name="💭 追記内容",
            value=message.content[:200] + ("..." if len(message.content) > 200 else ""),
            inline=False
        )

        if file_url:
            embed.add_field(
                name="📁 GitHub",
                value=f"[ファイルを見る]({file_url})",
                inline=False
            )

        # Show other candidates if there were multiple matches
        if len(candidates) > 1:
            other_memos = "\n".join([
                f"• {m.get('date')} - {m.get('scene', '不明')}"
                for m in candidates[1:3]  # Show up to 2 more
            ])
            embed.add_field(
                name="ℹ️ 他の候補",
                value=f"次のメモも見つかりました:\n{other_memos}",
                inline=False
            )

        await thinking_msg.edit(content=None, embed=embed)

    except Exception as e:
        error_msg = f"❌ エラーが発生しました: {str(e)}"
        print(f"Error processing reflection message: {e}")

        if bot.debug:
            import traceback
            traceback.print_exc()

        await message.reply(error_msg)


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
        # File size check (20MB limit)
        max_size = 20 * 1024 * 1024  # 20MB
        if attachment.size > max_size:
            await message.reply("❌ ファイルサイズが大きすぎます（上限20MB）")
            return

        # Detect scene from channel name
        channel_name = message.channel.name
        scene_type, scene_name = detect_scene_from_channel(channel_name)
        scene_emoji = get_scene_emoji(scene_type)

        # Send "thinking" message
        thinking_msg = await message.reply(f"📸 画像を保存中... (シーン: {scene_name})")

        # Get vault path from environment
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault")
        attachments_dir = Path(vault_path) / "attachments"

        # Generate filename: YYYY-MM-DD_シーン名_HHMMSS.ext
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        ext = Path(attachment.filename).suffix
        filename = f"{date_str}_{scene_name}_{time_str}{ext}"

        # Create date-based subdirectory
        date_dir = attachments_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Download and save image
        image_path = date_dir / filename
        await attachment.save(image_path)

        if bot.debug:
            print(f"📥 Downloaded image: {attachment.filename} ({attachment.size} bytes)")
            print(f"💾 Saved to: {image_path}")
            print(f"🎬 Detected scene: {scene_name} ({scene_type})")

        # Create memo data
        memo_data = {
            'date': date_str,
            'scene': scene_name,
            'input_type': 'image',
            'file_path': f"attachments/{date_str}/{filename}",
            'user_comment': message.content if message.content else "",
            'tags': ['tennis', scene_type, 'image']
        }

        # Build markdown for image memo
        await thinking_msg.edit(content=f"📝 Markdownを生成中... (シーン: {scene_name})")
        markdown_content = build_image_markdown(memo_data, scene_name)

        # Create PracticeSession object for GitHub push
        session = PracticeSession(
            raw_transcript=f"画像メモ: {message.content if message.content else '(コメントなし)'}",
            summary=f"画像メモ ({scene_name})",
            tags=memo_data['tags']
        )
        session.date = now

        # Override markdown builder to use our custom markdown
        await thinking_msg.edit(content="📤 GitHubにアップロード中...")
        file_url = push_image_memo_to_github(bot.github_sync, session, markdown_content, scene_name)

        # Create success embed
        embed = discord.Embed(
            title=f"{scene_emoji} {scene_name}の画像メモを保存しました",
            description=memo_data['user_comment'] or "画像を記録しました",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="📸 画像ファイル",
            value=f"`{filename}`",
            inline=False
        )

        if memo_data['user_comment']:
            embed.add_field(
                name="💭 コメント",
                value=memo_data['user_comment'],
                inline=False
            )

        embed.add_field(
            name="📁 GitHub",
            value=f"[ファイルを見る]({file_url})",
            inline=False
        )

        embed.set_footer(text=f"📅 {date_str}")

        await thinking_msg.edit(content=None, embed=embed)

    except Exception as e:
        error_msg = f"❌ エラーが発生しました: {str(e)}"
        print(f"Error processing image message: {e}")

        if bot.debug:
            import traceback
            traceback.print_exc()

        await message.reply(error_msg)


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
        # File size check (20MB limit)
        max_size = 20 * 1024 * 1024  # 20MB
        if attachment.size > max_size:
            await message.reply("❌ ファイルサイズが大きすぎます（上限20MB）")
            return

        # Detect scene from channel name
        channel_name = message.channel.name
        scene_type, scene_name = detect_scene_from_channel(channel_name)
        scene_emoji = get_scene_emoji(scene_type)

        # Send "thinking" message
        thinking_msg = await message.reply(f"🎥 動画を保存中... (シーン: {scene_name})")

        # Get vault path from environment
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault")
        attachments_dir = Path(vault_path) / "attachments"

        # Generate filename: YYYY-MM-DD_シーン名_HHMMSS.ext
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        ext = Path(attachment.filename).suffix
        filename = f"{date_str}_{scene_name}_{time_str}{ext}"

        # Create date-based subdirectory
        date_dir = attachments_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Download and save video
        video_path = date_dir / filename
        await attachment.save(video_path)

        if bot.debug:
            print(f"📥 Downloaded video: {attachment.filename} ({attachment.size} bytes)")
            print(f"💾 Saved to: {video_path}")
            print(f"🎬 Detected scene: {scene_name} ({scene_type})")

        # Create memo data
        memo_data = {
            'date': date_str,
            'scene': scene_name,
            'input_type': 'video',
            'file_path': f"attachments/{date_str}/{filename}",
            'user_comment': message.content if message.content else "",
            'tags': ['tennis', scene_type, 'video']
        }

        # Build markdown for video memo
        await thinking_msg.edit(content=f"📝 Markdownを生成中... (シーン: {scene_name})")
        markdown_content = build_video_markdown(memo_data, scene_name)

        # Create PracticeSession object for GitHub push
        session = PracticeSession(
            raw_transcript=f"動画メモ: {message.content if message.content else '(コメントなし)'}",
            summary=f"動画メモ ({scene_name})",
            tags=memo_data['tags']
        )
        session.date = now

        # Override markdown builder to use our custom markdown
        await thinking_msg.edit(content="📤 GitHubにアップロード中...")
        file_url = push_video_memo_to_github(bot.github_sync, session, markdown_content, scene_name)

        # Create success embed
        embed = discord.Embed(
            title=f"{scene_emoji} {scene_name}の動画メモを保存しました",
            description=memo_data['user_comment'] or "動画を記録しました",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="🎥 動画ファイル",
            value=f"`{filename}`",
            inline=False
        )

        if memo_data['user_comment']:
            embed.add_field(
                name="💭 コメント",
                value=memo_data['user_comment'],
                inline=False
            )

        embed.add_field(
            name="📁 GitHub",
            value=f"[ファイルを見る]({file_url})",
            inline=False
        )

        embed.set_footer(text=f"📅 {date_str}")

        await thinking_msg.edit(content=None, embed=embed)

    except Exception as e:
        error_msg = f"❌ エラーが発生しました: {str(e)}"
        print(f"Error processing video message: {e}")

        if bot.debug:
            import traceback
            traceback.print_exc()

        await message.reply(error_msg)
