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

    async def check_issue_progress(self, days_back: int = 14, max_issues: int = 3):
        """
        Check unresolved issues from recent memos and send progress reminder.

        Args:
            days_back: Number of days to look back for issues
            max_issues: Maximum number of issues to include in reminder
        """
        try:
            if not self.bot:
                print("⚠️ Bot not available, skipping issue progress check")
                return

            # Get admin user
            admin_user_id = os.getenv("ADMIN_USER_ID")
            if not admin_user_id:
                if self.debug:
                    print("⚠️ ADMIN_USER_ID not set, skipping issue progress check")
                return

            admin_user_id = int(admin_user_id)

            # Get recent memos (last N days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            recent_memos = self.obsidian_manager.get_memos_in_range(
                start_date=start_date,
                end_date=end_date
            )

            if not recent_memos:
                return

            # Extract unresolved issues
            unresolved_issues = []

            for memo in recent_memos:
                # Check for "issue", "next_action", or "課題" fields in body
                date = memo.get('date', '不明')
                body = memo.get('body', '')
                scene = memo.get('scene', '不明')

                # Extract issues from body
                import re
                patterns = [
                    r'## (?:課題|Issue|次回)[^\n]*\n(.+?)(?=\n##|\Z)',
                    r'課題.*?[:：]\s*(.+?)(?=\n|$)',
                    r'次回.*?[:：]\s*(.+?)(?=\n|$)',
                ]

                for pattern in patterns:
                    match = re.search(pattern, body, re.DOTALL)
                    if match:
                        issue_text = match.group(1).strip()

                        # Check if this issue has been resolved in later memos
                        is_resolved = await self._is_issue_resolved(
                            issue_text,
                            date,
                            recent_memos
                        )

                        if not is_resolved:
                            unresolved_issues.append({
                                "date": date,
                                "scene": scene,
                                "issue": issue_text[:150]  # Limit length
                            })
                        break

            # Remove duplicates (same issue text)
            unique_issues = []
            seen_texts = set()
            for issue in unresolved_issues:
                issue_text = issue['issue'].lower()
                if issue_text not in seen_texts:
                    unique_issues.append(issue)
                    seen_texts.add(issue_text)

            # Limit to max_issues
            unique_issues = unique_issues[:max_issues]

            if unique_issues:
                # Send progress reminder
                admin_user = await self.bot.fetch_user(admin_user_id)
                dm_channel = await admin_user.create_dm()

                message = """📊 **課題の進捗確認**

以下の課題はまだ取り組み中ですか？

"""
                for issue in unique_issues:
                    message += f"**{issue['date']}** ({issue['scene']})\n"
                    message += f"  {issue['issue']}\n\n"

                message += "取り組んだら、メモで報告してください！"

                await dm_channel.send(message)
                print(f"✅ Issue progress reminder sent ({len(unique_issues)} issues)")

        except Exception as e:
            print(f"❌ Error checking issue progress: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()

    async def _is_issue_resolved(
        self,
        issue_text: str,
        issue_date: str,
        all_memos: list
    ) -> bool:
        """
        Check if an issue has been resolved in later memos.

        Args:
            issue_text: The issue text to check
            issue_date: Date of the memo with the issue
            all_memos: All memos to search

        Returns:
            True if resolved, False otherwise
        """
        try:
            # Get memos after the issue date
            issue_datetime = datetime.strptime(issue_date, '%Y-%m-%d')
            later_memos = [
                m for m in all_memos
                if datetime.strptime(m.get('date', '2000-01-01'), '%Y-%m-%d') > issue_datetime
            ]

            # Extract keywords from issue (simple approach)
            import re
            # Split by common particles and extract meaningful words
            # Replace particles with spaces first
            text_normalized = re.sub(r'[をのにはがとでからまでへやも]', ' ', issue_text)
            # Extract Japanese words (including long vowel mark)
            keywords = re.findall(r'[ぁ-んァ-ヴー一-龯a-zA-Z]{2,}', text_normalized)
            # Remove common words and filter empty
            keywords = [k for k in keywords if k and k not in ['できる', 'する', 'いる', 'ある', 'なる', 'させる', 'こと', 'もの', 'ため']]

            # Need at least one keyword
            if not keywords:
                return False

            # Check if any later memo mentions improvement or resolution
            for memo in later_memos:
                body = memo.get('body', '').lower()

                # Check for resolution keywords
                if any(keyword in body for keyword in ['改善', '解決', 'できた', 'うまくいった']):
                    # Check if it's related to this issue
                    matching_keywords = sum(1 for k in keywords if k.lower() in body)
                    # Need at least half of keywords to match AND at least 1 keyword
                    if matching_keywords > 0 and matching_keywords >= max(1, len(keywords) // 2):
                        return True

            return False

        except Exception:
            return False

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


async def check_issue_progress(bot, days_back: int = 14, max_issues: int = 3):
    """
    Check unresolved issues and send progress reminder (convenience function).

    Args:
        bot: Discord bot instance
        days_back: Number of days to look back for issues
        max_issues: Maximum number of issues to include in reminder
    """
    reminder_manager = ReminderManager(bot=bot)
    await reminder_manager.check_issue_progress(
        days_back=days_back,
        max_issues=max_issues
    )
