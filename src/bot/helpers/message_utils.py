"""
Common utilities for message processing.

Extracts common patterns from message handlers to reduce duplication.
"""
from typing import TYPE_CHECKING, Optional, Callable, Any
import traceback

import discord

from src.bot.channel_handler import get_scene_info
from src.bot.helpers.previous_log import get_previous_log_summary
from src.bot.helpers.embed_builder import SessionEmbedBuilder
from src.models.session import PracticeSession
from src.models.scene_data import SceneInfo

if TYPE_CHECKING:
    from src.bot.client import TennisDiscoveryBot


async def send_thinking_message(
    message: discord.Message,
    scene_info: SceneInfo,
    status: str = "処理中"
) -> discord.Message:
    """
    Send a "thinking" message to indicate processing.

    Args:
        message: Original Discord message
        scene_info: Scene information
        status: Status text (e.g., "音声を処理中", "テキストを処理中")

    Returns:
        The sent thinking message
    """
    content = f"{scene_info.emoji} {status}... (シーン: {scene_info.name})"
    return await message.reply(content)


async def update_thinking_message(
    thinking_msg: discord.Message,
    status: str
) -> None:
    """
    Update the thinking message with new status.

    Args:
        thinking_msg: Thinking message to update
        status: New status text
    """
    await thinking_msg.edit(content=status)


async def send_session_embed(
    thinking_msg: discord.Message,
    session: PracticeSession,
    scene_info: SceneInfo,
    file_url: str,
    bot: "TennisDiscoveryBot",
    extra_fields: Optional[list[dict]] = None,
    custom_title: Optional[str] = None,
    custom_description: Optional[str] = None,
) -> discord.Message:
    """
    Build and send session result embed.

    Args:
        thinking_msg: Thinking message to replace
        session: Practice session data
        scene_info: Scene information
        file_url: GitHub file URL
        bot: Bot instance
        extra_fields: Optional extra fields
        custom_title: Optional custom title
        custom_description: Optional custom description

    Returns:
        The edited Discord message
    """
    # Get previous log summary
    previous_log = get_previous_log_summary(
        bot.obsidian_manager,
        scene_info.name,
        bot.debug
    )

    # Build embed
    embed = SessionEmbedBuilder.build(
        session=session,
        scene_info=scene_info,
        file_url=file_url,
        previous_log=previous_log,
        extra_fields=extra_fields,
        custom_title=custom_title,
        custom_description=custom_description,
    )

    # Send embed and return the message
    return await thinking_msg.edit(content=None, embed=embed)


async def handle_message_error(
    message: discord.Message,
    error: Exception,
    debug: bool = False,
    context: str = "processing message"
) -> None:
    """
    Handle errors in message processing.

    Args:
        message: Original Discord message
        error: Exception that occurred
        debug: Whether debug mode is enabled
        context: Context description for logging
    """
    error_msg = f"❌ エラーが発生しました: {str(error)}"
    print(f"Error {context}: {error}")

    if debug:
        traceback.print_exc()

    await message.reply(error_msg)


async def process_with_common_flow(
    bot: "TennisDiscoveryBot",
    message: discord.Message,
    processor: Callable,
    processor_args: dict,
    thinking_status: str = "処理中",
) -> None:
    """
    Process a message with common flow pattern.

    Common pattern:
    1. Detect scene
    2. Send thinking message
    3. Process content (via processor callback)
    4. Push to GitHub
    5. Send result embed
    6. Handle errors

    Args:
        bot: Bot instance
        message: Discord message
        processor: Async callback function that processes the content
                  Should return (session, file_url, extra_fields)
        processor_args: Arguments to pass to processor
        thinking_status: Initial status text
    """
    try:
        # 1. Detect scene
        scene_info = get_scene_info(message.channel.name)

        # 2. Send thinking message
        thinking_msg = await send_thinking_message(
            message, scene_info, thinking_status
        )

        # 3. Process content (callback)
        result = await processor(
            bot=bot,
            message=message,
            scene_info=scene_info,
            thinking_msg=thinking_msg,
            **processor_args
        )

        # Unpack result
        session, file_url = result[:2]
        extra_fields = result[2] if len(result) > 2 else None

        # 4. Send result embed
        await send_session_embed(
            thinking_msg=thinking_msg,
            session=session,
            scene_info=scene_info,
            file_url=file_url,
            bot=bot,
            extra_fields=extra_fields,
        )

        # 5. Generate follow-up question (optional)
        if session.success_patterns or session.failure_patterns:
            followup = await bot.gemini_client.generate_followup_question(session)
            if followup:
                await message.reply(f"💭 {followup}")

    except Exception as e:
        await handle_message_error(
            message, e, bot.debug, f"in {thinking_status}"
        )
