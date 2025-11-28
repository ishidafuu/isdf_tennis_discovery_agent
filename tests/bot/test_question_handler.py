"""
Tests for question handler.
"""
import pytest
from unittest.mock import Mock, AsyncMock

from src.bot.question_handler import QuestionHandler


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
def mock_comparison_analyzer():
    """モックComparisonAnalyzer"""
    analyzer = AsyncMock()
    return analyzer


@pytest.fixture
def question_handler(mock_model, mock_obsidian_manager, mock_comparison_analyzer):
    """QuestionHandlerインスタンス"""
    return QuestionHandler(
        model=mock_model,
        obsidian_manager=mock_obsidian_manager,
        comparison_analyzer=mock_comparison_analyzer
    )


class TestQuestionHandler:
    """QuestionHandler クラスのテスト"""

    @pytest.mark.asyncio
    async def test_search_related_memos(
        self,
        question_handler,
        mock_obsidian_manager,
        mock_comparison_analyzer
    ):
        """関連メモの検索"""
        # モックキーワード抽出
        mock_comparison_analyzer.extract_keywords.return_value = ["サーブ", "トス"]

        # モックObsidianManager
        memo1 = {
            "filepath": "/path/to/memo1.md",
            "date": "2025-11-20",
            "scene": "school",
            "raw_text": "サーブの練習"
        }
        memo2 = {
            "filepath": "/path/to/memo2.md",
            "date": "2025-11-15",
            "scene": "wall_practice",
            "raw_text": "トスの改善"
        }
        mock_obsidian_manager.search_by_keyword.return_value = [memo1, memo2]

        # テスト実行
        related_memos = await question_handler.search_related_memos(
            question="サーブのトスがうまくいかない"
        )

        # 検証
        assert len(related_memos) >= 1
        mock_comparison_analyzer.extract_keywords.assert_called_once()

    @pytest.mark.asyncio
    async def test_answer_question_no_memos(
        self,
        question_handler,
        mock_comparison_analyzer
    ):
        """関連メモがない場合"""
        # モックキーワード抽出（空のキーワード）
        mock_comparison_analyzer.extract_keywords.return_value = []

        # テスト実行
        result = await question_handler.answer_question(
            question="テニスについて教えて"
        )

        # 検証
        assert "関連するメモが見つかりませんでした" in result["answer"]
        assert len(result["related_memos"]) == 0

    @pytest.mark.asyncio
    async def test_answer_question_success(
        self,
        question_handler,
        mock_model,
        mock_obsidian_manager,
        mock_comparison_analyzer
    ):
        """質問回答の成功"""
        # モックキーワード抽出
        mock_comparison_analyzer.extract_keywords.return_value = ["サーブ"]

        # モックObsidianManager
        memo = {
            "filepath": "/path/to/memo.md",
            "date": "2025-11-20",
            "scene": "school",
            "raw_text": "サーブのトスは小指を締めると安定する"
        }
        mock_obsidian_manager.search_by_keyword.return_value = [memo]

        # モックGemini
        mock_response = Mock()
        mock_response.text = "過去のメモによると、小指を締めるとトスが安定するようです。"
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        result = await question_handler.answer_question(
            question="サーブのトスのコツは？"
        )

        # 検証
        assert "小指を締める" in result["answer"]
        assert len(result["related_memos"]) == 1
        assert result["related_memos"][0]["date"] == "2025-11-20"

    @pytest.mark.asyncio
    async def test_answer_question_error_fallback(
        self,
        question_handler,
        mock_model,
        mock_obsidian_manager,
        mock_comparison_analyzer
    ):
        """エラー時のフォールバック"""
        # モックキーワード抽出
        mock_comparison_analyzer.extract_keywords.return_value = ["サーブ"]

        # モックObsidianManager
        memo = {
            "filepath": "/path/to/memo.md",
            "date": "2025-11-20",
            "scene": "school",
            "raw_text": "サーブ練習"
        }
        mock_obsidian_manager.search_by_keyword.return_value = [memo]

        # モックGeminiでエラー
        mock_model.generate_content.side_effect = Exception("API Error")

        # テスト実行
        result = await question_handler.answer_question(
            question="サーブのコツは？"
        )

        # 検証: エラー時もフォールバックで回答を返す
        assert "回答の生成に失敗しました" in result["answer"]
        assert len(result["related_memos"]) == 1

    def test_format_answer_message(self, question_handler):
        """回答メッセージのフォーマット"""
        answer_data = {
            "answer": "過去のメモによると、トスが重要です。",
            "related_memos": [
                {
                    "date": "2025-11-20",
                    "scene": "school",
                    "raw_text": "トス練習"
                },
                {
                    "date": "2025-11-15",
                    "scene": "wall_practice",
                    "raw_text": "サーブ練習"
                }
            ],
            "keywords": ["サーブ", "トス"]
        }

        message = question_handler.format_answer_message(
            question="サーブのコツは？",
            answer_data=answer_data
        )

        # 検証
        assert "❓" in message
        assert "サーブのコツは？" in message
        assert "トスが重要" in message
        assert "📚 参照したメモ" in message
        assert "2025-11-20" in message
        assert "2025-11-15" in message

    def test_format_answer_message_no_memos(self, question_handler):
        """関連メモがない場合のメッセージフォーマット"""
        answer_data = {
            "answer": "関連するメモが見つかりませんでした。",
            "related_memos": [],
            "keywords": []
        }

        message = question_handler.format_answer_message(
            question="テニスについて教えて",
            answer_data=answer_data
        )

        # 検証
        assert "関連するメモが見つかりませんでした" in message
        assert "📚 参照したメモ" not in message  # メモがないので表示されない
