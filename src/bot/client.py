"""
Discord bot client for Tennis Discovery Agent.
"""
import os
import re
import tempfile
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.ai.gemini_client import GeminiClient
from src.storage.github_sync import GitHubSync
from src.storage.markdown_builder import MarkdownBuilder
from src.storage.obsidian_manager import ObsidianManager
from src.bot.channel_handler import detect_scene_from_channel, get_scene_emoji

# Load environment variables
load_dotenv()


class TennisDiscoveryBot(commands.Bot):
    """Discord bot for tennis practice session recording."""

    def __init__(self):
        """Initialize the bot with necessary intents."""
        # Setup intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(command_prefix="!", intents=intents)

        # Initialize clients
        self.gemini_client = GeminiClient()
        self.github_sync = GitHubSync()
        self.markdown_builder = MarkdownBuilder()
        self.obsidian_manager = ObsidianManager()

        # Debug mode
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        print("🎾 Tennis Discovery Agent initialized")

    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"✅ Bot is ready! Logged in as {self.user}")
        print(f"📊 Connected to {len(self.guilds)} guild(s)")

        # Check GitHub connection
        self.github_sync.check_connection()

    async def on_message(self, message: discord.Message):
        """
        Handle incoming messages.

        Args:
            message: Discord message object
        """
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Process attachments (audio, images, videos)
        if message.attachments:
            for attachment in message.attachments:
                # Check if it's an audio file (Discord voice messages are usually .ogg)
                if self._is_audio_file(attachment.filename):
                    await self._process_voice_message(message, attachment)
                    return
                # Check if it's an image file
                elif self._is_image_file(attachment.filename):
                    await self._process_image_message(message, attachment)
                    return
                # Check if it's a video file
                elif self._is_video_file(attachment.filename):
                    await self._process_video_message(message, attachment)
                    return

        # Process text messages (if there's content and not a command)
        if message.content and not message.content.startswith('!'):
            # Skip very short messages (probably not practice notes)
            if len(message.content.strip()) > 10:
                await self._process_text_message(message)
                return

        # Process commands
        await self.process_commands(message)

    def _is_audio_file(self, filename: str) -> bool:
        """
        Check if file is an audio file.

        Args:
            filename: File name

        Returns:
            True if it's an audio file
        """
        audio_extensions = [".ogg", ".mp3", ".wav", ".m4a", ".opus", ".webm"]
        return any(filename.lower().endswith(ext) for ext in audio_extensions)

    def _is_image_file(self, filename: str) -> bool:
        """
        Check if file is an image file.

        Args:
            filename: File name

        Returns:
            True if it's an image file
        """
        image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
        return any(filename.lower().endswith(ext) for ext in image_extensions)

    def _is_video_file(self, filename: str) -> bool:
        """
        Check if file is a video file.

        Args:
            filename: File name

        Returns:
            True if it's a video file
        """
        video_extensions = [".mp4", ".mov", ".avi", ".webm"]
        return any(filename.lower().endswith(ext) for ext in video_extensions)

    def _extract_urls(self, text: str) -> list[str]:
        """
        Extract URLs from text.

        Args:
            text: Text content

        Returns:
            List of URLs found in the text
        """
        url_pattern = r'https?://[^\s<>"\']+'
        return re.findall(url_pattern, text)

    async def _process_voice_message(
        self,
        message: discord.Message,
        attachment: discord.Attachment
    ):
        """
        Process a voice message attachment.

        Args:
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

            if self.debug:
                print(f"📥 Downloaded audio file: {attachment.filename} ({attachment.size} bytes)")
                print(f"🎬 Detected scene: {scene_name} ({scene_type})")

            # Process with Gemini (scene-aware)
            await thinking_msg.edit(content=f"🧠 Geminiで分析中... (シーン: {scene_name})")
            session, scene_data = await self.gemini_client.process_voice_message(tmp_path, scene_type)

            if self.debug:
                print(f"✅ Session processed: {session.condition}, {len(session.success_patterns)} successes")

            # Build and save markdown locally (optional, for debugging)
            if self.debug:
                local_path = self.markdown_builder.save(session,
                                                       self.markdown_builder.get_filename_for_session(session, scene_name))
                print(f"💾 Saved locally: {local_path}")

            # Push to GitHub (with scene name)
            await thinking_msg.edit(content="📤 GitHubにアップロード中...")
            file_url = self.github_sync.push_session(session, scene_name=scene_name)

            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)

            # Get previous log summary
            previous_log = self._get_previous_log_summary(scene_name)

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
                followup = await self.gemini_client.generate_followup_question(session)
                if followup:
                    await message.reply(f"💭 {followup}")

        except Exception as e:
            error_msg = f"❌ エラーが発生しました: {str(e)}"
            print(f"Error processing voice message: {e}")

            if self.debug:
                import traceback
                traceback.print_exc()

            await message.reply(error_msg)

        finally:
            # Clean up temporary file if it still exists
            if 'tmp_path' in locals():
                Path(tmp_path).unlink(missing_ok=True)

    async def _process_text_message(self, message: discord.Message):
        """
        Process a text message.

        Args:
            message: Discord message object
        """
        try:
            # Detect scene from channel name
            channel_name = message.channel.name
            scene_type, scene_name = detect_scene_from_channel(channel_name)
            scene_emoji = get_scene_emoji(scene_type)

            # Extract URLs
            urls = self._extract_urls(message.content)

            # Send "thinking" message
            thinking_msg = await message.reply(f"📝 テキストを処理中... (シーン: {scene_name})")

            if self.debug:
                print(f"📄 Processing text message in channel: {channel_name}")
                print(f"🎬 Detected scene: {scene_name} ({scene_type})")
                if urls:
                    print(f"🔗 Found URLs: {urls}")

            # Process with Gemini (scene-aware)
            await thinking_msg.edit(content=f"🧠 Geminiで分析中... (シーン: {scene_name})")
            session, scene_data = await self.gemini_client.process_text_message(
                message.content,
                scene_type,
                urls
            )

            if self.debug:
                print(f"✅ Text processed: {len(scene_data.get('tags', []))} tags")

            # Push to GitHub (with scene name)
            await thinking_msg.edit(content="📤 GitHubにアップロード中...")
            file_url = self.github_sync.push_session(session, scene_name=scene_name)

            # Get previous log summary
            previous_log = self._get_previous_log_summary(scene_name)

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

            if self.debug:
                import traceback
                traceback.print_exc()

            await message.reply(error_msg)

    async def _process_image_message(
        self,
        message: discord.Message,
        attachment: discord.Attachment
    ):
        """
        Process an image message attachment.

        Args:
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

            if self.debug:
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
            markdown_content = self._build_image_markdown(memo_data, scene_name)

            # Create PracticeSession object for GitHub push
            from src.models.session import PracticeSession
            session = PracticeSession(
                raw_transcript=f"画像メモ: {message.content if message.content else '(コメントなし)'}",
                summary=f"画像メモ ({scene_name})",
                tags=memo_data['tags']
            )
            session.date = now

            # Override markdown builder to use our custom markdown
            await thinking_msg.edit(content="📤 GitHubにアップロード中...")
            file_url = self._push_image_memo_to_github(session, markdown_content, scene_name)

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

            if self.debug:
                import traceback
                traceback.print_exc()

            await message.reply(error_msg)

    async def _process_video_message(
        self,
        message: discord.Message,
        attachment: discord.Attachment
    ):
        """
        Process a video message attachment.

        Args:
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

            if self.debug:
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
            markdown_content = self._build_video_markdown(memo_data, scene_name)

            # Create PracticeSession object for GitHub push
            from src.models.session import PracticeSession
            session = PracticeSession(
                raw_transcript=f"動画メモ: {message.content if message.content else '(コメントなし)'}",
                summary=f"動画メモ ({scene_name})",
                tags=memo_data['tags']
            )
            session.date = now

            # Override markdown builder to use our custom markdown
            await thinking_msg.edit(content="📤 GitHubにアップロード中...")
            file_url = self._push_video_memo_to_github(session, markdown_content, scene_name)

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

            if self.debug:
                import traceback
                traceback.print_exc()

            await message.reply(error_msg)

    def _build_image_markdown(self, memo_data: dict, scene_name: str) -> str:
        """
        Build markdown content for image memo.

        Args:
            memo_data: Memo data dictionary
            scene_name: Scene display name

        Returns:
            Markdown content as string
        """
        import yaml
        from datetime import datetime

        # Frontmatter
        frontmatter_data = {
            "date": memo_data['date'],
            "scene": scene_name,
            "input_type": "image",
            "tags": memo_data.get('tags', ['tennis', 'image']),
        }
        frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

        markdown = f"""---
{frontmatter}---

# 画像メモ - {scene_name} - {memo_data['date']}

## 📸 画像

![[{memo_data['file_path']}]]

"""

        # User comment
        if memo_data.get('user_comment'):
            markdown += f"""## 💭 メモ

{memo_data['user_comment']}

"""

        return markdown

    def _build_video_markdown(self, memo_data: dict, scene_name: str) -> str:
        """
        Build markdown content for video memo.

        Args:
            memo_data: Memo data dictionary
            scene_name: Scene display name

        Returns:
            Markdown content as string
        """
        import yaml
        from datetime import datetime

        # Frontmatter
        frontmatter_data = {
            "date": memo_data['date'],
            "scene": scene_name,
            "input_type": "video",
            "tags": memo_data.get('tags', ['tennis', 'video']),
        }
        frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

        markdown = f"""---
{frontmatter}---

# 動画メモ - {scene_name} - {memo_data['date']}

## 🎥 動画

![[{memo_data['file_path']}]]

"""

        # User comment
        if memo_data.get('user_comment'):
            markdown += f"""## 💭 メモ

{memo_data['user_comment']}

"""

        return markdown

    def _push_image_memo_to_github(
        self,
        session,
        markdown_content: str,
        scene_name: str
    ) -> str:
        """
        Push image memo to GitHub repository.

        Args:
            session: PracticeSession object
            markdown_content: Markdown content to push
            scene_name: Scene name for the filename

        Returns:
            URL of the created/updated file
        """
        from src.storage.markdown_builder import MarkdownBuilder

        builder = MarkdownBuilder()
        year = session.date.strftime("%Y")
        month = session.date.strftime("%m")
        filename = builder.get_filename_for_session(session, f"{scene_name}-画像")
        file_path = f"{self.github_sync.base_path}/{year}/{month}/{filename}"

        date_str = session.date.strftime("%Y-%m-%d")
        commit_message = f"Add image memo: {date_str} ({scene_name})"

        file_url = self.github_sync._push_file(
            file_path=file_path,
            content=markdown_content,
            commit_message=commit_message
        )

        return file_url

    def _push_video_memo_to_github(
        self,
        session,
        markdown_content: str,
        scene_name: str
    ) -> str:
        """
        Push video memo to GitHub repository.

        Args:
            session: PracticeSession object
            markdown_content: Markdown content to push
            scene_name: Scene name for the filename

        Returns:
            URL of the created/updated file
        """
        from src.storage.markdown_builder import MarkdownBuilder

        builder = MarkdownBuilder()
        year = session.date.strftime("%Y")
        month = session.date.strftime("%m")
        filename = builder.get_filename_for_session(session, f"{scene_name}-動画")
        file_path = f"{self.github_sync.base_path}/{year}/{month}/{filename}"

        date_str = session.date.strftime("%Y-%m-%d")
        commit_message = f"Add video memo: {date_str} ({scene_name})"

        file_url = self.github_sync._push_file(
            file_path=file_path,
            content=markdown_content,
            commit_message=commit_message
        )

        return file_url

    def _get_previous_log_summary(self, scene_name: str) -> Optional[str]:
        """
        Get previous log summary for the same scene.

        Args:
            scene_name: Scene display name

        Returns:
            Formatted summary string or None
        """
        try:
            previous_memo = self.obsidian_manager.get_latest_memo(scene_name=scene_name)

            if not previous_memo:
                return None

            # Extract key information
            date = previous_memo.get('date', '不明')
            next_action = None
            somatic_marker = previous_memo.get('somatic_marker', '')

            # Try to extract next_action from body (various formats)
            body = previous_memo.get('body', '')

            # Look for next_action patterns in body
            if '## 次回' in body or '## Next Action' in body:
                # Extract text after "次回" header
                import re
                pattern = r'## (?:次回|Next Action)[^\n]*\n(.+?)(?=\n##|\Z)'
                match = re.search(pattern, body, re.DOTALL)
                if match:
                    next_action = match.group(1).strip()

            # Build summary
            summary_parts = [f"📅 前回: {date}"]

            if somatic_marker:
                summary_parts.append(f"🎯 前回の身体感覚: {somatic_marker[:50]}...")

            if next_action:
                # Limit length
                next_action_short = next_action[:100] + "..." if len(next_action) > 100 else next_action
                summary_parts.append(f"📝 前回の課題:\n{next_action_short}")

            return "\n".join(summary_parts)

        except Exception as e:
            if self.debug:
                print(f"Error getting previous log: {e}")
            return None

    async def setup_hook(self):
        """Setup hook called before the bot starts."""
        print("🔧 Setting up bot...")


def create_bot() -> TennisDiscoveryBot:
    """
    Create and return a configured bot instance.

    Returns:
        TennisDiscoveryBot instance
    """
    return TennisDiscoveryBot()


def run_bot():
    """Run the Discord bot."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN not found in environment variables")

    bot = create_bot()
    bot.run(token)
