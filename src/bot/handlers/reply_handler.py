"""
Reply handler for Discord bot.

Handles replies to memo messages for appending deepening information.
"""
from typing import TYPE_CHECKING

import discord

from src.ai.deepening_analysis import analyze_and_format_reply
from src.bot.helpers.message_utils import update_thinking_message

if TYPE_CHECKING:
    from src.bot.client import TennisDiscoveryBot


async def handle_reply_to_memo(bot: "TennisDiscoveryBot", message: discord.Message) -> None:
    """
    Handle a reply to a memo message.

    Analyzes the reply content, determines if it's deepening information,
    and appends it to the original memo file.

    Args:
        bot: TennisDiscoveryBot instance
        message: Discord message object (reply)
    """
    try:
        # Get the original message ID
        if not message.reference or not message.reference.message_id:
            return

        original_message_id = message.reference.message_id

        if bot.debug:
            print(f"📝 Processing reply to message ID: {original_message_id}")
            print(f"Reply content: {message.content[:100]}")

        # Find the memo file associated with this message ID
        memo_path = bot.obsidian_manager.find_memo_by_discord_id(original_message_id)

        if not memo_path:
            # Not a reply to a memo message, ignore
            if bot.debug:
                print("ℹ️ Reply is not to a memo message, ignoring")
            return

        if bot.debug:
            print(f"✅ Found memo: {memo_path}")

        # Analyze the reply content
        deepening_info = await analyze_and_format_reply(bot.gemini_client, message.content)

        if not deepening_info:
            # Not deepening information (e.g., "了解", "ありがとう")
            await message.add_reaction("👍")
            if bot.debug:
                print("ℹ️ Reply is not deepening information, added 👍 reaction")
            return

        if bot.debug:
            print(f"🧠 Analyzed as: {deepening_info['pattern']}")

        # Append to memo file
        success = bot.obsidian_manager.append_to_memo(
            file_path=memo_path,
            append_text=deepening_info['formatted'],
            section_title=None  # Already formatted with section title
        )

        if not success:
            await message.reply("❌ 追記の保存に失敗しました。")
            return

        # Push to GitHub
        try:
            with open(memo_path, 'r', encoding='utf-8') as f:
                updated_content = f.read()

            commit_message = f"Append deepening info: {deepening_info['pattern']}"
            bot.github_sync._push_file(
                file_path=memo_path.replace(str(bot.obsidian_manager.vault_path) + "/", ""),
                content=updated_content,
                commit_message=commit_message
            )
        except Exception as e:
            if bot.debug:
                print(f"⚠️ Failed to push to GitHub: {e}")

        # Confirm with user
        await message.add_reaction("✅")
        await message.reply(f"追記しました！\n\n{deepening_info['summary']}")

        if bot.debug:
            print("✅ Deepening information appended successfully")

    except Exception as e:
        print(f"❌ Error handling reply: {e}")
        if bot.debug:
            import traceback
            traceback.print_exc()
