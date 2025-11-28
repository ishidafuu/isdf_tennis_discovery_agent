"""
Tests for contradiction detection.
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock

from src.analysis.contradiction_detection import ContradictionDetector


@pytest.fixture
def mock_model():
    """モックGeminiモデル"""
    model = Mock()
    model.generate_content = Mock()
    return model


@pytest.fixture
def mock_obsidian_manager():
    """モックObsidianManager"""
    manager = AsyncMock()
    return manager


@pytest.fixture
def contradiction_detector(mock_model, mock_obsidian_manager):
    """ContradictionDetectorインスタンス"""
    return ContradictionDetector(
        model=mock_model,
        obsidian_manager=mock_obsidian_manager
    )


class TestContradictionDetector:
    """ContradictionDetector クラスのテスト"""

    @pytest.mark.asyncio
    async def test_detect_contradiction_no_past_memos(
        self,
        contradiction_detector,
        mock_obsidian_manager
    ):
        """過去メモがない場合はNoneを返す"""
        # モックObsidianManager（過去メモなし）
        mock_obsidian_manager.get_latest_memo.return_value = []

        # テスト実行
        result = await contradiction_detector.detect_contradiction(
            current_text="今日はサーブ練習",
            scene_type="school"
        )

        # 検証
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_contradiction_no_contradiction(
        self,
        contradiction_detector,
        mock_model,
        mock_obsidian_manager
    ):
        """矛盾がない場合はNoneを返す"""
        # モックObsidianManager（過去メモあり）
        past_memo = {
            "date": "2025-11-20",
            "raw_text": "サーブの練習"
        }
        mock_obsidian_manager.get_latest_memo.return_value = [past_memo]

        # モックレスポンス（矛盾なし）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "has_contradiction": False
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        result = await contradiction_detector.detect_contradiction(
            current_text="今日もサーブ練習",
            scene_type="school"
        )

        # 検証
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_contradiction_found(
        self,
        contradiction_detector,
        mock_model,
        mock_obsidian_manager
    ):
        """矛盾が検出された場合"""
        # モックObsidianManager（過去メモあり）
        past_memo = {
            "date": "2025-11-20",
            "raw_text": "フラットサーブが安定している"
        }
        mock_obsidian_manager.get_latest_memo.return_value = [past_memo]

        # モックレスポンス（矛盾あり）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "has_contradiction": True,
            "contradiction_type": "矛盾",
            "previous_statement": "フラットサーブが安定している",
            "current_statement": "フラットサーブが全く入らない",
            "comment": "何が変わったのですか？",
            "confidence": 0.9
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        result = await contradiction_detector.detect_contradiction(
            current_text="今日はフラットサーブが全く入らない",
            scene_type="school"
        )

        # 検証
        assert result is not None
        assert result["has_contradiction"] is True
        assert result["contradiction_type"] == "矛盾"
        assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_detect_contradiction_low_confidence(
        self,
        contradiction_detector,
        mock_model,
        mock_obsidian_manager
    ):
        """自信度が低い場合は無視する"""
        # モックObsidianManager（過去メモあり）
        past_memo = {
            "date": "2025-11-20",
            "raw_text": "サーブ練習"
        }
        mock_obsidian_manager.get_latest_memo.return_value = [past_memo]

        # モックレスポンス（矛盾あり、低い自信度）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "has_contradiction": True,
            "contradiction_type": "変化",
            "previous_statement": "サーブ練習",
            "current_statement": "ボレー練習",
            "comment": "内容が違いますね",
            "confidence": 0.5  # 閾値0.7未満
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        result = await contradiction_detector.detect_contradiction(
            current_text="今日はボレー練習",
            scene_type="school",
            confidence_threshold=0.7
        )

        # 検証: 自信度が低いのでNone
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_contradiction_evolution(
        self,
        contradiction_detector,
        mock_model,
        mock_obsidian_manager
    ):
        """進化（意図的な変化）の検出"""
        # モックObsidianManager（過去メモあり）
        past_memo = {
            "date": "2025-11-20",
            "raw_text": "小指を締める感覚でサーブ"
        }
        mock_obsidian_manager.get_latest_memo.return_value = [past_memo]

        # モックレスポンス（進化）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "has_contradiction": True,
            "contradiction_type": "進化",
            "previous_statement": "小指を締める感覚",
            "current_statement": "手のひら全体で押す感覚",
            "comment": "新しいアプローチを試しているのですね。どちらが効果的でしたか？",
            "confidence": 0.85
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        result = await contradiction_detector.detect_contradiction(
            current_text="手のひら全体で押す感覚に変えた",
            scene_type="school"
        )

        # 検証
        assert result is not None
        assert result["contradiction_type"] == "進化"

    @pytest.mark.asyncio
    async def test_detect_contradiction_error_handling(
        self,
        contradiction_detector,
        mock_model,
        mock_obsidian_manager
    ):
        """エラー時はNoneを返す"""
        # モックObsidianManager（過去メモあり）
        past_memo = {
            "date": "2025-11-20",
            "raw_text": "サーブ練習"
        }
        mock_obsidian_manager.get_latest_memo.return_value = [past_memo]

        # モックレスポンス（無効なJSON）
        mock_response = Mock()
        mock_response.text = "This is not JSON"
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        result = await contradiction_detector.detect_contradiction(
            current_text="今日はサーブ練習",
            scene_type="school"
        )

        # 検証: エラー時はNone
        assert result is None

    def test_format_contradiction_message_contradiction(self, contradiction_detector):
        """矛盾のメッセージフォーマット"""
        detection_result = {
            "has_contradiction": True,
            "contradiction_type": "矛盾",
            "previous_statement": "フラットサーブが安定している",
            "current_statement": "フラットサーブが全く入らない",
            "comment": "何が変わったのですか？",
            "confidence": 0.9
        }

        message = contradiction_detector.format_contradiction_message(detection_result)

        # 検証
        assert "⚠️" in message  # 矛盾の絵文字
        assert "矛盾に気づきました" in message
        assert "フラットサーブが安定している" in message
        assert "フラットサーブが全く入らない" in message
        assert "90%" in message  # 確信度

    def test_format_contradiction_message_evolution(self, contradiction_detector):
        """進化のメッセージフォーマット"""
        detection_result = {
            "has_contradiction": True,
            "contradiction_type": "進化",
            "previous_statement": "小指を締める感覚",
            "current_statement": "手のひら全体で押す感覚",
            "comment": "新しいアプローチですね",
            "confidence": 0.85
        }

        message = contradiction_detector.format_contradiction_message(detection_result)

        # 検証
        assert "🌱" in message  # 進化の絵文字
        assert "進化に気づきました" in message

    def test_format_contradiction_message_change(self, contradiction_detector):
        """変化のメッセージフォーマット"""
        detection_result = {
            "has_contradiction": True,
            "contradiction_type": "変化",
            "previous_statement": "サーブ中心の練習",
            "current_statement": "ボレー中心の練習",
            "comment": "練習内容を変えたのですか？",
            "confidence": 0.75
        }

        message = contradiction_detector.format_contradiction_message(detection_result)

        # 検証
        assert "💭" in message  # 変化の絵文字
        assert "変化に気づきました" in message

    def test_format_contradiction_message_no_contradiction(self, contradiction_detector):
        """矛盾がない場合は空文字列"""
        detection_result = {
            "has_contradiction": False
        }

        message = contradiction_detector.format_contradiction_message(detection_result)

        # 検証
        assert message == ""

    def test_format_contradiction_message_none(self, contradiction_detector):
        """Noneの場合は空文字列"""
        message = contradiction_detector.format_contradiction_message(None)

        # 検証
        assert message == ""
