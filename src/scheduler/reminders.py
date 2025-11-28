"""
Practice reminder system for Tennis Discovery Agent.

Sends reminders before practice sessions with previous themes and goals.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from dotenv import load_dotenv

from src.storage.obsidian_manager import ObsidianManager

# Load environment variables
load_dotenv()


class ReminderManager:
    """Manage practice reminders."""

    def __init__(self, bot=None):
        """
        Initialize reminder manager.

        Args:
            bot: Discord bot instance (for sending DMs)
        """
        self.bot = bot
        self.obsidian_manager = ObsidianManager()

        # Debug mode
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

    async def send_practice_reminder(
        self,
        scene_type: Optional[str] = None,
        scene_name: Optional[str] = None
    ):
        """
        Send practice reminder to admin user.

        Args:
            scene_type: Scene type (wall_practice, school, etc.)
            scene_name: Scene display name (壁打ち, スクール, etc.)
        """
        try:
            if not self.bot:
                print("⚠️ Bot not available, skipping reminder")
                return

            # Get admin user
            admin_user_id = os.getenv("ADMIN_USER_ID")
            if not admin_user_id:
                if self.debug:
                    print("⚠️ ADMIN_USER_ID not set, skipping reminder")
                return

            admin_user_id = int(admin_user_id)
            admin_user = await self.bot.fetch_user(admin_user_id)
            dm_channel = await admin_user.create_dm()

            # Get previous memo
            previous_memo = self.obsidian_manager.get_latest_memo(scene_name=scene_name)

            # Build reminder message
            message = self._build_reminder_message(previous_memo, scene_name)

            # Send reminder
            await dm_channel.send(message)

            print(f"✅ Practice reminder sent for {scene_name or 'general practice'}")

        except Exception as e:
            print(f"❌ Error sending practice reminder: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()

    async def check_inactive_days(self, days_threshold: int = 3):
        """
        Check if user hasn't practiced for N days and send reminder.

        Args:
            days_threshold: Number of days without practice before sending reminder
        """
        try:
            if not self.bot:
                print("⚠️ Bot not available, skipping inactive check")
                return

            # Get admin user
            admin_user_id = os.getenv("ADMIN_USER_ID")
            if not admin_user_id:
                if self.debug:
                    print("⚠️ ADMIN_USER_ID not set, skipping inactive check")
                return

            admin_user_id = int(admin_user_id)

            # Get latest memo
            latest_memo = self.obsidian_manager.get_latest_memo()

            if not latest_memo:
                # No memos at all
                return

            # Check last practice date
            last_date_str = latest_memo.get('date')
            if not last_date_str:
                return

            try:
                last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
                days_since = (datetime.now() - last_date).days

                if days_since >= days_threshold:
                    # Send inactive reminder
                    admin_user = await self.bot.fetch_user(admin_user_id)
                    dm_channel = await admin_user.create_dm()

                    message = f"""🎾 **練習リマインド**

{days_since}日間、練習記録がありません。

前回の練習: {last_date_str}
前回のシーン: {latest_memo.get('scene', '不明')}

体を動かしてリフレッシュしましょう！
"""

                    await dm_channel.send(message)
                    print(f"✅ Inactive reminder sent ({days_since} days)")

            except ValueError:
                if self.debug:
                    print(f"⚠️ Could not parse date: {last_date_str}")

        except Exception as e:
            print(f"❌ Error checking inactive days: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()

    def _build_reminder_message(
        self,
        previous_memo: Optional[Dict[str, Any]],
        scene_name: Optional[str]
    ) -> str:
        """
        Build reminder message from previous memo.

        Args:
            previous_memo: Previous memo dictionary
            scene_name: Scene display name

        Returns:
            Formatted reminder message
        """
        scene_text = scene_name or "練習"

        if not previous_memo:
            # No previous memo
            return f"""🎾 **{scene_text}リマインド**

今日も楽しく練習しましょう！

練習後は音声メモで振り返りを記録してくださいね。
"""

        # Extract key information
        date = previous_memo.get('date', '不明')
        body = previous_memo.get('body', '')

        # Try to extract next actions from body
        next_action = None
        if '次回' in body or 'Next Action' in body or '課題' in body:
            import re
            # Extract text after "次回" or "課題" header
            patterns = [
                r'## (?:次回|Next Action|課題)[^\n]*\n(.+?)(?=\n##|\Z)',
                r'次回.*?[:：]\s*(.+?)(?=\n|$)',
                r'課題.*?[:：]\s*(.+?)(?=\n|$)',
            ]

            for pattern in patterns:
                match = re.search(pattern, body, re.DOTALL)
                if match:
                    next_action = match.group(1).strip()
                    # Limit length
                    if len(next_action) > 200:
                        next_action = next_action[:200] + "..."
                    break

        # Build message
        message = f"""🎾 **{scene_text}リマインド**

前回の練習: {date}
"""

        if next_action:
            message += f"""
📝 **前回の課題・テーマ:**
{next_action}
"""

        message += """
今日も意識して取り組みましょう！

練習後は音声メモで振り返りを記録してくださいね。
"""

        return message


async def send_reminder_for_scene(bot, scene_name: str):
    """
    Send reminder for specific scene (convenience function).

    Args:
        bot: Discord bot instance
        scene_name: Scene name (壁打ち, スクール, etc.)
    """
    reminder_manager = ReminderManager(bot=bot)
    await reminder_manager.send_practice_reminder(scene_name=scene_name)


async def check_inactive_users(bot, days: int = 3):
    """
    Check for inactive users (convenience function).

    Args:
        bot: Discord bot instance
        days: Days threshold for inactivity
    """
    reminder_manager = ReminderManager(bot=bot)
    await reminder_manager.check_inactive_days(days_threshold=days)
