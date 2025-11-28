"""
Scheduler manager for Tennis Discovery Agent.

Manages periodic tasks like weekly reviews and reminders.
"""
import os
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from src.scheduler.weekly_review import WeeklyReviewGenerator
from src.scheduler.reminders import ReminderManager

# Load environment variables
load_dotenv()


class SchedulerManager:
    """Manage scheduled tasks for Tennis Discovery Agent."""

    def __init__(self, bot=None):
        """
        Initialize scheduler manager.

        Args:
            bot: Discord bot instance (optional, for sending notifications)
        """
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.weekly_review_generator = WeeklyReviewGenerator()
        self.reminder_manager = ReminderManager(bot=bot)

        # Debug mode
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

    def start(self):
        """Start the scheduler."""
        # Add weekly review job
        # Runs every Sunday at 21:00 (9:00 PM)
        self.scheduler.add_job(
            self._generate_weekly_review,
            trigger=CronTrigger(day_of_week='sun', hour=21, minute=0),
            id='weekly_review',
            name='Weekly Practice Review',
            replace_existing=True
        )

        # Add inactive check job
        # Runs every day at 20:00 (8:00 PM)
        self.scheduler.add_job(
            self._check_inactive_users,
            trigger=CronTrigger(hour=20, minute=0),
            id='inactive_check',
            name='Inactive User Check',
            replace_existing=True
        )

        # Start scheduler
        self.scheduler.start()
        print("📅 Scheduler started")
        print("   - Weekly review: Sundays at 21:00")
        print("   - Inactive check: Daily at 20:00")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("📅 Scheduler stopped")

    async def _generate_weekly_review(self):
        """Generate weekly review (scheduled task)."""
        try:
            print(f"📊 Starting weekly review generation at {datetime.now()}")

            # Generate review
            file_path = self.weekly_review_generator.generate_weekly_review(week_offset=0)

            if file_path and self.bot:
                # Send notification to admin (if bot is available)
                await self._send_review_notification(file_path)

        except Exception as e:
            print(f"❌ Error generating weekly review: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()

    async def _send_review_notification(self, file_path: str):
        """
        Send notification about generated review to admin.

        Args:
            file_path: Path to generated review file
        """
        try:
            admin_user_id = os.getenv("ADMIN_USER_ID")
            if not admin_user_id or not self.bot:
                return

            admin_user_id = int(admin_user_id)
            admin_user = await self.bot.fetch_user(admin_user_id)
            dm_channel = await admin_user.create_dm()

            # Send notification
            await dm_channel.send(
                f"📊 **週次レビューを生成しました**\n\n"
                f"今週の練習記録を分析して、週次レビューを作成しました。\n"
                f"ファイル: `{file_path}`"
            )

            print(f"✅ Review notification sent to admin")

        except Exception as e:
            print(f"⚠️ Failed to send review notification: {e}")

    async def _check_inactive_users(self):
        """Check for inactive users (scheduled task)."""
        try:
            print(f"📅 Checking for inactive users at {datetime.now()}")

            # Check if user hasn't practiced for 3 days
            await self.reminder_manager.check_inactive_days(days_threshold=3)

        except Exception as e:
            print(f"❌ Error checking inactive users: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()

    def trigger_weekly_review_now(self):
        """Trigger weekly review immediately (for testing)."""
        self.scheduler.add_job(
            self._generate_weekly_review,
            trigger='date',
            id='manual_weekly_review',
            name='Manual Weekly Review',
            replace_existing=True
        )
        print("📊 Weekly review triggered manually")

    def trigger_inactive_check_now(self):
        """Trigger inactive check immediately (for testing)."""
        self.scheduler.add_job(
            self._check_inactive_users,
            trigger='date',
            id='manual_inactive_check',
            name='Manual Inactive Check',
            replace_existing=True
        )
        print("📅 Inactive check triggered manually")
