"""
DM (Direct Message) handler for processing messages sent while bot was offline.
"""
import os
import tempfile
from pathlib import Path

import discord

from src.bot.channel_handler import get_scene_emoji
from src.bot.helpers.media_utils import (
    is_audio_file,
    is_image_file,
    is_video_file,
    extract_scene_from_dm_text
)


async def process_pending_dms(bot):
    """
    Process pending DMs sent while bot was offline.

    This method checks the admin user's DMs for unprocessed messages
    and processes them automatically.

    Args:
        bot: TennisDiscoveryBot instance
    """
    try:
        # Get admin user ID from environment
        admin_user_id = os.getenv("ADMIN_USER_ID")
        if not admin_user_id:
            if bot.debug:
                print("⚠️ ADMIN_USER_ID not set, skipping DM processing")
            return

        admin_user_id = int(admin_user_id)

        if bot.debug:
            print(f"🔍 Checking pending DMs for user: {admin_user_id}")

        # Fetch admin user
        admin_user = await bot.fetch_user(admin_user_id)
        dm_channel = await admin_user.create_dm()

        pending_count = 0

        # Check last 50 messages
        async for message in dm_channel.history(limit=50):
            # Skip messages from bot itself
            if message.author == bot.user:
                continue

            # Skip messages that already have ✅ reaction
            if any(r.emoji == '✅' for r in message.reactions):
                continue

            # Process attachments
            if message.attachments:
                for attachment in message.attachments:
                    # Extract scene from message content
                    scene_type, scene_name = extract_scene_from_dm_text(message.content)

                    # Process based on file type
                    if is_audio_file(attachment.filename):
                        await process_voice_message_from_dm(
                            bot, message, attachment, scene_type, scene_name
                        )
                        pending_count += 1
                    elif is_image_file(attachment.filename):
                        # Import here to avoid circular dependency
                        from src.bot.handlers.message_handler import process_image_message
                        await process_image_message(bot, message, attachment)
                        pending_count += 1
                    elif is_video_file(attachment.filename):
                        # Import here to avoid circular dependency
                        from src.bot.handlers.message_handler import process_video_message
                        await process_video_message(bot, message, attachment)
                        pending_count += 1

                    # Mark as processed
                    await message.add_reaction('✅')

        # Send completion notification
        if pending_count > 0:
            await dm_channel.send(f"✅ Bot復旧後、未処理メモを {pending_count} 件処理しました")
            print(f"✅ Processed {pending_count} pending DM(s)")
        elif bot.debug:
            print("📭 No pending DMs to process")

    except Exception as e:
        print(f"❌ Error processing pending DMs: {e}")
        if bot.debug:
            import traceback
            traceback.print_exc()


async def process_voice_message_from_dm(
    bot,
    message: discord.Message,
    attachment: discord.Attachment,
    scene_type: str,
    scene_name: str
):
    """
    Process a voice message from DM.

    Args:
        bot: TennisDiscoveryBot instance
        message: Discord message object
        attachment: Audio attachment
        scene_type: Scene type (wall_practice, school, etc.)
        scene_name: Scene display name
    """
    try:
        scene_emoji = get_scene_emoji(scene_type)

        # Download audio file to temporary location
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(attachment.filename).suffix
        ) as tmp_file:
            tmp_path = tmp_file.name
            await attachment.save(tmp_path)

        if bot.debug:
            print(f"📥 Processing DM voice: {attachment.filename} ({scene_name})")

        # Process with Gemini (scene-aware)
        session, scene_data = await bot.gemini_client.process_voice_message(tmp_path, scene_type)

        # Push to GitHub (with scene name)
        file_url = bot.github_sync.push_session(session, scene_name=scene_name)

        # Clean up temporary file
        Path(tmp_path).unlink(missing_ok=True)

        # Send confirmation
        await message.reply(f"{scene_emoji} {scene_name}の記録を保存しました\n📁 {file_url}")

    except Exception as e:
        error_msg = f"❌ エラーが発生しました: {str(e)}"
        print(f"Error processing DM voice message: {e}")
        await message.reply(error_msg)
    finally:
        # Clean up temporary file if it still exists
        if 'tmp_path' in locals():
            Path(tmp_path).unlink(missing_ok=True)
