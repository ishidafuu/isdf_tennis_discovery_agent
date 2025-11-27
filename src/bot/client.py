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

        # Process voice messages
        if message.attachments:
            for attachment in message.attachments:
                # Check if it's an audio file (Discord voice messages are usually .ogg)
                if self._is_audio_file(attachment.filename):
                    await self._process_voice_message(message, attachment)
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

            # Create success embed
            embed = discord.Embed(
                title=f"{scene_emoji} {scene_name}の記録を保存しました",
                description=session.summary or "音声メッセージを記録しました",
                color=discord.Color.green()
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

            # Create success embed
            embed = discord.Embed(
                title=f"{scene_emoji} {scene_name}のテキストメモを保存しました",
                description=session.summary or "テキストメッセージを記録しました",
                color=discord.Color.blue()
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
