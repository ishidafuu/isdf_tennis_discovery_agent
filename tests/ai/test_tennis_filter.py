"""
Tests for tennis relevance filtering.
"""
import pytest
import json
from unittest.mock import Mock

from src.ai.gemini_client import GeminiClient


@pytest.fixture
def mock_model():
    """モックGeminiモデル"""
    model = Mock()
    model.generate_content = Mock()
    return model


@pytest.fixture
def gemini_client(mock_model):
    """GeminiClientインスタンス（モデルを差し替え）"""
    client = GeminiClient(api_key="test_key")
    client.model = mock_model
    return client


class TestTennisRelatedFilter:
    """テニス関連判定のテスト"""

    @pytest.mark.asyncio
    async def test_tennis_practice_is_related(self, gemini_client, mock_model):
        """テニス練習の内容は関連ありと判定される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": True})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "今日は壁打ち1時間やりました。サーブの調子が良かったです。"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証
        assert is_tennis is True
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_tennis_match_is_related(self, gemini_client, mock_model):
        """試合の内容は関連ありと判定される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": True})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "昨日の試合はストレートで勝ちました。フォアハンドの精度が上がっています。"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証
        assert is_tennis is True

    @pytest.mark.asyncio
    async def test_tennis_equipment_is_related(self, gemini_client, mock_model):
        """テニス用具の内容は関連ありと判定される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": True})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "新しいラケットを買いました。ガットのテンションは55ポンドです。"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証
        assert is_tennis is True

    @pytest.mark.asyncio
    async def test_casual_chat_is_not_related(self, gemini_client, mock_model):
        """雑談は関連なしと判定される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": False})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "今日は天気が良いですね。お昼ご飯は何を食べようかな。"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証
        assert is_tennis is False

    @pytest.mark.asyncio
    async def test_greeting_is_not_related(self, gemini_client, mock_model):
        """挨拶のみは関連なしと判定される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": False})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "こんにちは！元気ですか？"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証
        assert is_tennis is False

    @pytest.mark.asyncio
    async def test_other_sports_is_not_related(self, gemini_client, mock_model):
        """他のスポーツは関連なしと判定される"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": False})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "今日はサッカーの試合を見ました。バスケットボールも楽しいですね。"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証
        assert is_tennis is False

    @pytest.mark.asyncio
    async def test_tennis_keyword_but_unrelated_context(self, gemini_client, mock_model):
        """「テニス」という単語があっても文脈が関連なければFalse"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": False})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "テニスのゲームを買いました。今夜は友達とゲームで遊びます。"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証
        assert is_tennis is False

    @pytest.mark.asyncio
    async def test_json_parse_error_returns_false(self, gemini_client, mock_model):
        """JSONパースエラー時はFalseを返す（安全側に倒す）"""
        # モックレスポンス（無効なJSON）
        mock_response = Mock()
        mock_response.text = "This is not valid JSON"
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "テスト内容"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証: エラー時はFalseを返す
        assert is_tennis is False

    @pytest.mark.asyncio
    async def test_missing_field_returns_false(self, gemini_client, mock_model):
        """必須フィールドが欠けている場合はFalseを返す"""
        # モックレスポンス（フィールド欠如）
        mock_response = Mock()
        mock_response.text = json.dumps({})  # is_tennis_related が欠けている
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        text = "テスト内容"
        is_tennis = await gemini_client.is_tennis_related(text)

        # 検証: フィールドがない場合はFalseを返す
        assert is_tennis is False

    @pytest.mark.asyncio
    async def test_prompt_contains_tennis_keywords(self, gemini_client, mock_model):
        """プロンプトにテニス用語の例が含まれているか確認"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({"is_tennis_related": True})
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        await gemini_client.is_tennis_related("テスト内容")

        # プロンプトが呼ばれたか確認
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args

        # プロンプト内容を確認
        prompt = call_args[0][0]
        assert "サーブ" in prompt or "serve" in prompt
        assert "ボレー" in prompt or "volley" in prompt
        assert "ストローク" in prompt
        assert "フォアハンド" in prompt or "forehand" in prompt
        assert "バックハンド" in prompt or "backhand" in prompt
