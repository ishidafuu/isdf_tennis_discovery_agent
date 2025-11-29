"""
Tests for enhanced reminder functionality (Phase 3).
"""
import pytest
from datetime import datetime, timedelta
from src.scheduler.reminders import ReminderManager


@pytest.mark.asyncio
async def test_is_issue_resolved_true():
    """課題が解決されていることを検出"""
    reminder = ReminderManager()

    issue_text = "フォアハンドのフォロースルーを大きく"
    issue_date = "2025-11-20"

    # 後日のメモで「フォアハンド」と「できた」が含まれている
    all_memos = [
        {
            'date': '2025-11-20',
            'body': '## 課題\nフォアハンドのフォロースルーを大きく',
        },
        {
            'date': '2025-11-22',
            'body': '今日はフォアハンドが改善できた！フォロースルーが大きくなった。',
        }
    ]

    is_resolved = await reminder._is_issue_resolved(
        issue_text,
        issue_date,
        all_memos
    )

    assert is_resolved is True


@pytest.mark.asyncio
async def test_is_issue_resolved_false():
    """課題が解決されていないことを検出"""
    reminder = ReminderManager()

    issue_text = "サーブのトスを安定させる"
    issue_date = "2025-11-20"

    # 後日のメモでサーブについて触れていない
    all_memos = [
        {
            'date': '2025-11-20',
            'body': '## 課題\nサーブのトスを安定させる',
        },
        {
            'date': '2025-11-22',
            'body': '今日はフォアハンドが改善できた！',
        }
    ]

    is_resolved = await reminder._is_issue_resolved(
        issue_text,
        issue_date,
        all_memos
    )

    assert is_resolved is False


@pytest.mark.asyncio
async def test_is_issue_resolved_no_later_memos():
    """後日のメモがない場合"""
    reminder = ReminderManager()

    issue_text = "バックハンドの改善"
    issue_date = "2025-11-25"

    # 後日のメモがない
    all_memos = [
        {
            'date': '2025-11-20',
            'body': '何か',
        },
        {
            'date': '2025-11-25',
            'body': '## 課題\nバックハンドの改善',
        }
    ]

    is_resolved = await reminder._is_issue_resolved(
        issue_text,
        issue_date,
        all_memos
    )

    assert is_resolved is False


def test_build_reminder_message_with_next_action():
    """前回の課題がある場合のリマインドメッセージ"""
    reminder = ReminderManager()

    previous_memo = {
        'date': '2025-11-20',
        'body': """## 記録

練習がうまくいった。

## 次回

フォアハンドのフォロースルーを大きく取る
"""
    }

    message = reminder._build_reminder_message(previous_memo, "壁打ち")

    assert "壁打ちリマインド" in message
    assert "2025-11-20" in message
    assert "フォロースルーを大きく取る" in message or "フォアハンド" in message


def test_build_reminder_message_without_previous():
    """前回のメモがない場合のリマインドメッセージ"""
    reminder = ReminderManager()

    message = reminder._build_reminder_message(None, "スクール")

    assert "スクールリマインド" in message
    assert "楽しく練習しましょう" in message
