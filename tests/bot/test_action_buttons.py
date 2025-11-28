"""
Tests for Discord action buttons.

Note: Discord UI components require a running event loop and are complex to test.
These tests focus on the helper functions and basic structure validation.
Full integration tests should be performed manually or in a Discord bot environment.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch


class TestActionButtonsStructure:
    """ActionButtons の基本構造テスト"""

    def test_import_action_buttons_view(self):
        """ActionButtonsView がインポートできることを確認"""
        from src.bot.action_buttons import ActionButtonsView
        assert ActionButtonsView is not None

    def test_import_confirm_buttons_view(self):
        """ConfirmButtonsView がインポートできることを確認"""
        from src.bot.action_buttons import ConfirmButtonsView
        assert ConfirmButtonsView is not None

    def test_import_helper_functions(self):
        """ヘルパー関数がインポートできることを確認"""
        from src.bot.action_buttons import send_with_action_buttons, confirm_dialog
        assert send_with_action_buttons is not None
        assert confirm_dialog is not None


class TestHelperFunctions:
    """ヘルパー関数のテスト"""

    @pytest.mark.asyncio
    async def test_send_with_action_buttons(self):
        """send_with_action_buttons 関数のテスト"""
        from src.bot.action_buttons import send_with_action_buttons

        # モックチャンネル
        mock_channel = AsyncMock()
        mock_message = AsyncMock()
        mock_channel.send = AsyncMock(return_value=mock_message)

        memo_data = {"text": "テストメモ"}

        # Viewのwaitとeditをモック
        with patch('src.bot.action_buttons.ActionButtonsView') as mock_view_class:
            mock_view = Mock()
            mock_view.result = "deep_dive"
            mock_view.children = []
            mock_view.wait = AsyncMock()
            mock_view_class.return_value = mock_view

            # 関数実行
            result = await send_with_action_buttons(
                channel=mock_channel,
                content="メモを保存しました",
                memo_data=memo_data,
                timeout=60.0
            )

            # 検証
            assert result == "deep_dive"
            mock_channel.send.assert_called_once()
            mock_view.wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_with_action_buttons_timeout(self):
        """タイムアウト時の動作"""
        from src.bot.action_buttons import send_with_action_buttons

        # モックチャンネル
        mock_channel = AsyncMock()
        mock_message = AsyncMock()
        mock_channel.send = AsyncMock(return_value=mock_message)

        memo_data = {"text": "テストメモ"}

        # Viewのwaitとeditをモック（タイムアウト）
        with patch('src.bot.action_buttons.ActionButtonsView') as mock_view_class:
            mock_view = Mock()
            mock_view.result = None  # タイムアウト時は None
            mock_view.children = []
            mock_view.wait = AsyncMock()
            mock_view_class.return_value = mock_view

            # 関数実行
            result = await send_with_action_buttons(
                channel=mock_channel,
                content="メモを保存しました",
                memo_data=memo_data,
                timeout=60.0
            )

            # 検証: result が None の場合は "timeout" が返される
            assert result == "timeout"

    @pytest.mark.asyncio
    async def test_confirm_dialog(self):
        """confirm_dialog 関数のテスト"""
        from src.bot.action_buttons import confirm_dialog

        # モックチャンネル
        mock_channel = AsyncMock()
        mock_message = AsyncMock()
        mock_channel.send = AsyncMock(return_value=mock_message)

        # Viewのwaitとeditをモック
        with patch('src.bot.action_buttons.ConfirmButtonsView') as mock_view_class:
            mock_view = Mock()
            mock_view.result = True
            mock_view.children = []
            mock_view.wait = AsyncMock()
            mock_view_class.return_value = mock_view

            # 関数実行
            result = await confirm_dialog(
                channel=mock_channel,
                question="続けますか？",
                timeout=30.0
            )

            # 検証
            assert result is True
            mock_channel.send.assert_called_once()
            mock_view.wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_dialog_no(self):
        """confirm_dialog で「いいえ」を選択"""
        from src.bot.action_buttons import confirm_dialog

        # モックチャンネル
        mock_channel = AsyncMock()
        mock_message = AsyncMock()
        mock_channel.send = AsyncMock(return_value=mock_message)

        # Viewのwaitとeditをモック
        with patch('src.bot.action_buttons.ConfirmButtonsView') as mock_view_class:
            mock_view = Mock()
            mock_view.result = False
            mock_view.children = []
            mock_view.wait = AsyncMock()
            mock_view_class.return_value = mock_view

            # 関数実行
            result = await confirm_dialog(
                channel=mock_channel,
                question="続けますか？",
                timeout=30.0
            )

            # 検証
            assert result is False
