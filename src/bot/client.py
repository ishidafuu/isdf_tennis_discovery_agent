"""
Discord bot client for Tennis Discovery Agent.

This module contains the main bot class and event handlers.
Message processing logic has been refactored into separate handler modules.
"""
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.ai.gemini_client import GeminiClient
from src.storage.github_sync import GitHubSync
from src.storage.markdown_builder import MarkdownBuilder
from src.storage.obsidian_manager import ObsidianManager
from src.bot.channel_handler import detect_scene_from_channel, is_reflection_channel
from src.scheduler.scheduler_manager import SchedulerManager

# Import handlers and helpers
from src.bot.helpers.media_utils import is_audio_file, is_image_file, is_video_file
from src.bot.handlers.message_handler import (
    process_voice_message,
    process_text_message,
    process_reflection_message,
    process_image_message,
    process_video_message,
)
from src.bot.handlers.dm_handler import process_pending_dms

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
        self.scheduler_manager = SchedulerManager(bot=self)

        # Debug mode
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        print("🎾 Tennis Discovery Agent initialized")

    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"✅ Bot is ready! Logged in as {self.user}")
        print(f"📊 Connected to {len(self.guilds)} guild(s)")

        # Check GitHub connection
        self.github_sync.check_connection()

        # Process pending DMs (sent while bot was offline)
        await process_pending_dms(self)

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
                if is_audio_file(attachment.filename):
                    await process_voice_message(self, message, attachment)
                    return
                # Check if it's an image file
                elif is_image_file(attachment.filename):
                    await process_image_message(self, message, attachment)
                    return
                # Check if it's a video file
                elif is_video_file(attachment.filename):
                    await process_video_message(self, message, attachment)
                    return

        # Process text messages (if there's content and not a command)
        if message.content and not message.content.startswith('!'):
            # Skip very short messages (probably not practice notes)
            if len(message.content.strip()) > 10:
                # Check if this is a reflection/review channel
                if is_reflection_channel(message.channel.name):
                    await process_reflection_message(self, message)
                else:
                    await process_text_message(self, message)
                return

        # Process commands
        await self.process_commands(message)

    async def setup_hook(self):
        """Setup hook called before the bot starts."""
        print("🔧 Setting up bot...")

        # Start scheduler for weekly reviews and reminders
        self.scheduler_manager.start()


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
