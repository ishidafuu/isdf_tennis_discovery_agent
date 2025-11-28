"""
Tests for question generation logic.
"""
import pytest
import json
from unittest.mock import Mock

from src.ai.question_generation import QuestionGenerator, ConversationManager


@pytest.fixture
def mock_model():
    """モックGeminiモデル"""
    model = Mock()
    model.generate_content = Mock()
    return model


@pytest.fixture
def question_generator(mock_model):
    """QuestionGeneratorインスタンス"""
    return QuestionGenerator(model=mock_model)


@pytest.fixture
def conversation_manager(question_generator):
    """ConversationManagerインスタンス"""
    return ConversationManager(
        question_generator=question_generator,
        max_turns=3,
        timeout_seconds=60
    )


class TestQuestionGenerator:
    """QuestionGenerator クラスのテスト"""

    @pytest.mark.asyncio
    async def test_generate_question(self, question_generator, mock_model):
        """基本的な質問生成"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = "なぜそう思ったんですか？"
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        question = await question_generator.generate_question(
            text="今日のサーブはうまくいった",
            scene_type="school"
        )

        # 検証
        assert question == "なぜそう思ったんですか？"
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_question_with_error(self, question_generator, mock_model):
        """エラー時のフォールバック質問"""
        # モックレスポンスでエラーを発生させる
        mock_model.generate_content.side_effect = Exception("API Error")

        # テスト実行
        question = await question_generator.generate_question(
            text="テスト",
            scene_type="free_practice"
        )

        # 検証: フォールバック質問が返される
        assert question == "もう少し詳しく教えてもらえますか？"

    @pytest.mark.asyncio
    async def test_generate_deep_dive_question(self, question_generator, mock_model):
        """深掘り質問の生成"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = "『うまくいった』とは、具体的にどういう感覚でしたか？"
        mock_model.generate_content.return_value = mock_response

        # 会話履歴
        conversation_history = [
            "今日のサーブはうまくいった",
            "なぜそう思ったんですか？",
            "トスが安定していたから"
        ]

        # テスト実行
        question = await question_generator.generate_deep_dive_question(
            conversation_history=conversation_history,
            scene_type="school",
            current_turn=2,
            max_turns=3
        )

        # 検証
        assert "具体的" in question
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_deep_enough_true(self, question_generator, mock_model):
        """十分深掘りできた場合"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({
            "is_deep_enough": True,
            "reason": "身体感覚が具体的に言語化されている"
        })
        mock_model.generate_content.return_value = mock_response

        # 会話履歴
        conversation_history = [
            "今日のサーブはうまくいった",
            "なぜそう思ったんですか？",
            "トスを上げる時に、左手の小指を締める感覚があって、それで安定した"
        ]

        # テスト実行
        is_deep = await question_generator.is_deep_enough(conversation_history)

        # 検証
        assert is_deep is True

    @pytest.mark.asyncio
    async def test_is_deep_enough_false(self, question_generator, mock_model):
        """まだ深掘りできる場合"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = json.dumps({
            "is_deep_enough": False,
            "reason": "まだ曖昧な表現が残っている"
        })
        mock_model.generate_content.return_value = mock_response

        # 会話履歴
        conversation_history = [
            "今日のサーブはうまくいった"
        ]

        # テスト実行
        is_deep = await question_generator.is_deep_enough(conversation_history)

        # 検証
        assert is_deep is False

    @pytest.mark.asyncio
    async def test_is_deep_enough_error_fallback(self, question_generator, mock_model):
        """エラー時は保守的に「まだ深掘りできる」と判定"""
        # モックレスポンスでエラーを発生させる
        mock_model.generate_content.side_effect = Exception("API Error")

        # テスト実行
        is_deep = await question_generator.is_deep_enough(["テスト"])

        # 検証: エラー時は False（まだ深掘りできる）
        assert is_deep is False


class TestConversationManager:
    """ConversationManager クラスのテスト"""

    @pytest.mark.asyncio
    async def test_start_conversation(self, conversation_manager, mock_model):
        """会話開始"""
        # モックレスポンス
        mock_response = Mock()
        mock_response.text = "なぜそう思ったんですか？"
        mock_model.generate_content.return_value = mock_response

        # テスト実行
        conversation = await conversation_manager.start_conversation(
            initial_text="今日のサーブはうまくいった",
            scene_type="school"
        )

        # 検証
        assert len(conversation) == 2  # 初回メッセージ + 質問
        assert conversation[0]["role"] == "user"
        assert conversation[0]["content"] == "今日のサーブはうまくいった"
        assert conversation[1]["role"] == "assistant"
        assert "なぜ" in conversation[1]["content"]

    def test_add_user_response(self, conversation_manager):
        """ユーザー応答の追加"""
        # 既存の会話
        conversation = [
            {"role": "user", "content": "初回メッセージ"},
            {"role": "assistant", "content": "質問1"}
        ]

        # ユーザー応答を追加
        updated = conversation_manager.add_user_response(
            conversation=conversation,
            response="応答1"
        )

        # 検証
        assert len(updated) == 3
        assert updated[2]["role"] == "user"
        assert updated[2]["content"] == "応答1"

    @pytest.mark.asyncio
    async def test_should_continue_max_turns(self, conversation_manager, mock_model):
        """最大ターン数に達した場合は終了"""
        # 3ターン分の会話（max_turns=3）
        conversation = [
            {"role": "user", "content": "メッセージ1"},
            {"role": "assistant", "content": "質問1"},
            {"role": "user", "content": "応答1"},
            {"role": "assistant", "content": "質問2"},
            {"role": "user", "content": "応答2"},
            {"role": "assistant", "content": "質問3"},
            {"role": "user", "content": "応答3"}
        ]

        # テスト実行
        should_continue = await conversation_manager.should_continue(conversation)

        # 検証: 最大ターンに達したので False
        assert should_continue is False

    @pytest.mark.asyncio
    async def test_should_continue_deep_enough(self, conversation_manager, mock_model):
        """十分深掘りできた場合は終了"""
        # モックレスポンス（深掘り完了）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "is_deep_enough": True,
            "reason": "十分深掘りできた"
        })
        mock_model.generate_content.return_value = mock_response

        # 会話履歴（2ターン目）
        conversation = [
            {"role": "user", "content": "メッセージ1"},
            {"role": "assistant", "content": "質問1"},
            {"role": "user", "content": "詳細な応答"}
        ]

        # テスト実行
        should_continue = await conversation_manager.should_continue(conversation)

        # 検証: 深掘り完了なので False
        assert should_continue is False

    @pytest.mark.asyncio
    async def test_should_continue_yes(self, conversation_manager, mock_model):
        """まだ続けるべき場合"""
        # モックレスポンス（まだ深掘りできる）
        mock_response = Mock()
        mock_response.text = json.dumps({
            "is_deep_enough": False,
            "reason": "まだ曖昧"
        })
        mock_model.generate_content.return_value = mock_response

        # 会話履歴（1ターン目）
        conversation = [
            {"role": "user", "content": "メッセージ1"},
            {"role": "assistant", "content": "質問1"},
            {"role": "user", "content": "応答1"}
        ]

        # テスト実行
        should_continue = await conversation_manager.should_continue(conversation)

        # 検証: まだ続けられるので True
        assert should_continue is True
