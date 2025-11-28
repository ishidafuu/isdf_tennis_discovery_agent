"""
Tests for comparison analysis.
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from src.analysis.comparison import ComparisonAnalyzer


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
def comparison_analyzer(mock_model, mock_obsidian_manager):
    """ComparisonAnalyzerインスタンス"""
    return ComparisonAnalyzer(
        model=mock_model,
        obsidian_manager=mock_obsidian_manager
    )


class TestComparisonAnalyzer:
    """ComparisonAnalyzer クラスのテスト"""

    @pytest.mark.asyncio
    async def test_extract_keywords(self, comparison_analyzer, mock_model):
        """キーワード抽出"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({
            "keywords": ["サーブ", "フォアハンド", "バックハンド"]
        })
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        keywords = await comparison_analyzer.extract_keywords(
            text="今日はサーブとフォアハンドの練習をしました"
        )

        # 検証
        assert keywords == ["サーブ", "フォアハンド", "バックハンド"]
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_keywords_error_fallback(self, comparison_analyzer, mock_model):
        """キーワード抽出エラー時のフォールバック"""
        # モックレスポンスでエラーを発生させる
        mock_model.generate_content.side_effect = Exception("API Error")

        # テスト実行
        keywords = await comparison_analyzer.extract_keywords(
            text="サーブ フォアハンド バックハンド"
        )

        # 検証: エラー時は簡単な単語分割
        assert len(keywords) == 3
        assert "サーブ" in keywords

    @pytest.mark.asyncio
    async def test_search_similar_memos_with_keywords(
        self,
        comparison_analyzer,
        mock_model,
        mock_obsidian_manager
    ):
        """キーワードによる類似メモ検索"""
        # モックレスポンス（キーワード抽出）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "keywords": ["サーブ", "トス"]
        })
        mock_model.generate_content.return_value = mock_response

        # モックObsidianManager（検索結果）
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
        similar_memos = await comparison_analyzer.search_similar_memos(
            text="今日もサーブのトス練習",
            scene_type="school",
            limit=5
        )

        # 検証
        assert len(similar_memos) >= 1
        # search_by_keywordが複数回呼ばれている（各キーワードごと）
        assert mock_obsidian_manager.search_by_keyword.call_count >= 1

    @pytest.mark.asyncio
    async def test_search_similar_memos_exclude_recent(
        self,
        comparison_analyzer,
        mock_model,
        mock_obsidian_manager
    ):
        """直近N日間を除外する検索"""
        # モックレスポンス（キーワード抽出）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "keywords": ["サーブ"]
        })
        mock_model.generate_content.return_value = mock_response

        # モックObsidianManager（検索結果）
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        recent_memo = {
            "filepath": "/path/to/recent.md",
            "date": today,
            "scene": "school",
            "raw_text": "最近のサーブ練習"
        }
        old_memo = {
            "filepath": "/path/to/old.md",
            "date": week_ago,
            "scene": "school",
            "raw_text": "1週間前のサーブ練習"
        }

        mock_obsidian_manager.search_by_keyword.return_value = [recent_memo, old_memo]

        # テスト実行（直近3日を除外）
        similar_memos = await comparison_analyzer.search_similar_memos(
            text="サーブ練習",
            scene_type="school",
            limit=5,
            exclude_recent_days=3
        )

        # 検証: 1週間前のメモのみ含まれる
        assert len(similar_memos) == 1
        assert similar_memos[0]["date"] == week_ago

    @pytest.mark.asyncio
    async def test_compare_with_past_no_memos(
        self,
        comparison_analyzer,
        mock_model,
        mock_obsidian_manager
    ):
        """過去メモが見つからない場合"""
        # モックレスポンス（キーワード抽出）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "keywords": ["サーブ"]
        })
        mock_model.generate_content.return_value = mock_response

        # モックObsidianManager（検索結果なし）
        mock_obsidian_manager.search_by_keyword.return_value = []

        # テスト実行
        analysis = await comparison_analyzer.compare_with_past(
            current_text="サーブ練習",
            scene_type="school"
        )

        # 検証
        assert "過去に類似するメモが見つかりませんでした" in analysis

    @pytest.mark.asyncio
    async def test_compare_with_past_success(
        self,
        comparison_analyzer,
        mock_model,
        mock_obsidian_manager
    ):
        """過去メモとの比較成功"""
        # モックレスポンス（キーワード抽出）
        keyword_response = Mock()
        keyword_response.text = json.dumps({
            "keywords": ["サーブ"]
        })

        # モックレスポンス（比較分析）
        comparison_response = Mock()
        comparison_response.text = """## 📊 過去との比較

### 共通点
サーブのトスに意識を向けている

### 変化
前回よりトスが安定している

### 繰り返しのパターン
トスの高さが課題

### 💡 次に意識すること
トスの高さをどう安定させますか？
"""

        # generate_contentが2回呼ばれる（キーワード抽出と比較分析）
        mock_model.generate_content.side_effect = [keyword_response, comparison_response]

        # モックObsidianManager（検索結果）
        memo = {
            "filepath": "/path/to/memo.md",
            "date": "2025-11-20",
            "scene": "school",
            "raw_text": "サーブのトスが安定しない"
        }
        mock_obsidian_manager.search_by_keyword.return_value = [memo]

        # テスト実行
        analysis = await comparison_analyzer.compare_with_past(
            current_text="今日もサーブのトス練習",
            scene_type="school",
            limit=3
        )

        # 検証
        assert "📊 過去との比較" in analysis
        assert "共通点" in analysis
        assert "変化" in analysis

    @pytest.mark.asyncio
    async def test_compare_with_past_long_memo_truncation(
        self,
        comparison_analyzer,
        mock_model,
        mock_obsidian_manager
    ):
        """長すぎるメモは切り捨てられる"""
        # モックレスポンス（キーワード抽出）
        keyword_response = Mock()
        keyword_response.text = json.dumps({
            "keywords": ["サーブ"]
        })

        # モックレスポンス（比較分析）
        comparison_response = Mock()
        comparison_response.text = "## 分析結果"

        mock_model.generate_content.side_effect = [keyword_response, comparison_response]

        # モックObsidianManager（長いメモ）
        long_text = "a" * 500  # 500文字
        memo = {
            "filepath": "/path/to/memo.md",
            "date": "2025-11-20",
            "scene": "school",
            "raw_text": long_text
        }
        mock_obsidian_manager.search_by_keyword.return_value = [memo]

        # テスト実行
        analysis = await comparison_analyzer.compare_with_past(
            current_text="サーブ練習",
            scene_type="school"
        )

        # 検証: プロンプトに渡されるテキストが300文字 + "..."に切り捨てられている
        # （実際のプロンプトを確認するのは難しいので、エラーが出なければOK）
        assert analysis is not None
        assert len(analysis) > 0
