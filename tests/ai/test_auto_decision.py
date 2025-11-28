"""
Tests for AI auto decision logic.
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from src.ai.auto_decision import AutoDecision, ActionType


@pytest.fixture
def mock_model():
    """モックGeminiモデル"""
    model = Mock()
    model.generate_content = Mock()  # 同期関数
    return model


@pytest.fixture
def auto_decision(mock_model):
    """AutoDecisionインスタンス"""
    return AutoDecision(model=mock_model)


class TestAutoDecision:
    """AutoDecision クラスのテスト"""

    @pytest.mark.asyncio
    async def test_decide_action_save_only(self, auto_decision, mock_model):
        """日常的なメモは「保存のみ」と判断される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "save_only",
            "reason": "日常的な記録",
            "confidence": 0.9
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        decision = await auto_decision.decide_action(
            text="今日は壁打ち1時間やりました",
            scene_type="wall_practice"
        )

        # 検証
        assert decision["action"] == ActionType.SAVE_ONLY.value
        assert decision["confidence"] == 0.9
        assert auto_decision.should_save_only(decision)
        assert not auto_decision.should_deep_dive(decision)
        assert not auto_decision.should_compare(decision)

    @pytest.mark.asyncio
    async def test_decide_action_deep_dive(self, auto_decision, mock_model):
        """新しい気づきは「深堀質問」と判断される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "deep_dive",
            "reason": "「うまくいった」という曖昧な表現があり、具体化が必要",
            "confidence": 0.85
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        decision = await auto_decision.decide_action(
            text="今日のサーブはうまくいった",
            scene_type="school"
        )

        # 検証
        assert decision["action"] == ActionType.DEEP_DIVE.value
        assert decision["confidence"] == 0.85
        assert auto_decision.should_deep_dive(decision)
        assert not auto_decision.should_save_only(decision)
        assert not auto_decision.should_compare(decision)

    @pytest.mark.asyncio
    async def test_decide_action_compare(self, auto_decision, mock_model):
        """過去に類似テーマがある場合は「比較」と判断される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "compare",
            "reason": "バックハンドについて繰り返し出ているテーマ",
            "confidence": 0.8
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        previous_memo = {
            "date": "2025-11-20",
            "raw_text": "バックハンドが安定しない"
        }

        decision = await auto_decision.decide_action(
            text="バックハンドがまた調子悪い",
            scene_type="free_practice",
            previous_memo=previous_memo
        )

        # 検証
        assert decision["action"] == ActionType.COMPARE.value
        assert decision["confidence"] == 0.8
        assert auto_decision.should_compare(decision)
        assert not auto_decision.should_save_only(decision)
        assert not auto_decision.should_deep_dive(decision)

    @pytest.mark.asyncio
    async def test_low_confidence_fallback(self, auto_decision, mock_model):
        """自信度が低い場合はデフォルト（保存のみ）にフォールバック"""
        # モックレスポンス（低い自信度）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "deep_dive",
            "reason": "曖昧な判断",
            "confidence": 0.5  # 閾値0.7未満
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        decision = await auto_decision.decide_action(
            text="テスト",
            scene_type="free_practice",
            confidence_threshold=0.7
        )

        # 検証: 自信度が低いのでsave_onlyにフォールバック
        assert decision["action"] == ActionType.SAVE_ONLY.value
        assert "自信度が低い" in decision["reason"]

    @pytest.mark.asyncio
    async def test_error_handling_invalid_json(self, auto_decision, mock_model):
        """JSONパースエラー時のフォールバック"""
        # モックレスポンス（無効なJSON）
        mock_response = Mock()
        mock_response.text = "This is not JSON"
        mock_model.generate_content.return_value = mock_response

        # テスト実行（エラーが発生するはず）
        with pytest.raises(ValueError, match="Failed to parse decision JSON"):
            await auto_decision.decide_action(
                text="テスト",
                scene_type="free_practice"
            )

    @pytest.mark.asyncio
    async def test_error_handling_missing_fields(self, auto_decision, mock_model):
        """必須フィールドが欠けている場合はフォールバックする"""
        # モックレスポンス（必須フィールド欠如）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "save_only"
            # "confidence" が欠けている
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行: エラーが発生するがフォールバックで save_only を返す
        decision = await auto_decision.decide_action(
            text="テスト",
            scene_type="free_practice"
        )

        # 検証: フォールバックで save_only が返される
        assert decision["action"] == ActionType.SAVE_ONLY.value
        assert decision["confidence"] == 0.0
        assert "エラーが発生したため保存のみ" in decision["reason"]

    @pytest.mark.asyncio
    async def test_invalid_action_type(self, auto_decision, mock_model):
        """無効なアクションタイプはsave_onlyにフォールバック"""
        # モックレスポンス（無効なアクション）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "invalid_action",
            "reason": "テスト",
            "confidence": 0.9
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        decision = await auto_decision.decide_action(
            text="テスト",
            scene_type="free_practice"
        )

        # 検証: 無効なアクションはsave_onlyにフォールバック
        assert decision["action"] == ActionType.SAVE_ONLY.value

    @pytest.mark.asyncio
    async def test_previous_memo_formatting(self, auto_decision, mock_model):
        """前回メモが正しくフォーマットされる"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({
            "action": "save_only",
            "reason": "テスト",
            "confidence": 0.9
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        previous_memo = {
            "date": "2025-11-20",
            "raw_text": "前回のメモです" * 50  # 長いテキスト
        }

        await auto_decision.decide_action(
            text="テスト",
            scene_type="free_practice",
            previous_memo=previous_memo
        )

        # プロンプトが呼ばれたか確認
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args

        # プロンプトに前回メモの日付が含まれているか
        prompt = call_args[0][0]
        assert "2025-11-20" in prompt
        # 長すぎるテキストは切り捨てられているか（200文字まで + "..."）
        assert "..." in prompt
