"""
深堀質問生成機能 - ソクラテス式問答で気づきを促す
"""
import logging
from typing import List, Dict, Any, Optional

import google.generativeai as genai


logger = logging.getLogger(__name__)


class QuestionGenerator:
    """ソクラテス式質問生成器"""

    QUESTION_PROMPT = """以下の音声メモに対して、ソクラテス式の質問を1つ生成してください。

音声メモ:
{text}

シーン: {scene_type}

質問の目的:
- ユーザーの気づきを深める
- 曖昧な表現を具体化させる
- 次のアクションを明確にする
- 身体感覚を言語化させる

質問のパターン例:
- **理由を聞く**: 「なぜそう思ったんですか？」
- **具体化を促す**: 「『うまくいった』とは、具体的にどういう感覚でしたか？」
- **他の可能性**: 「他に試せることはありますか？」
- **次のアクション**: 「次回も同じように意識しますか？」
- **過去との違い**: 「前回と何が違いましたか？」
- **身体感覚**: 「その時、身体のどこを意識しましたか？」

重要:
- 質問は1文で簡潔に
- アドバイスではなく、問いかける形式
- ユーザーの言葉を引用して質問に含めると効果的
- 生成した質問のみを出力（前置きや説明は不要）
"""

    DEEP_DIVE_PROMPT = """以下の会話履歴から、次の質問を生成してください。

会話履歴:
{conversation_history}

シーン: {scene_type}

現在のターン数: {current_turn} / {max_turns}

質問の目的:
- 前回の回答をさらに深掘りする
- 曖昧な表現があれば具体化させる
- 新しい気づきを引き出す
- 身体感覚やコンテキストを引き出す

重要:
- 前回の回答を踏まえた質問にする
- 同じような質問を繰り返さない
- ターン数が進むにつれて、より具体的・深い質問にする
- 生成した質問のみを出力（前置きや説明は不要）
"""

    DEPTH_CHECK_PROMPT = """以下の会話履歴を見て、十分に深掘りできたか判定してください。

会話履歴:
{conversation_history}

判定基準:
- 曖昧な表現が具体化されている
- 身体感覚が言語化されている
- 次のアクションが明確になっている
- ユーザーが新しい気づきを得ている

判定結果をJSON形式で出力してください:
{{
  "is_deep_enough": true/false,
  "reason": "判定理由（1-2文で簡潔に）"
}}

重要: JSON以外のテキストは出力しないでください。
"""

    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize QuestionGenerator.

        Args:
            model: Gemini GenerativeModel instance
        """
        self.model = model

    async def generate_question(
        self,
        text: str,
        scene_type: str
    ) -> str:
        """
        追加質問を生成

        Args:
            text: 音声メモまたはテキストメモ
            scene_type: シーンタイプ（wall_practice, school, match, etc.）

        Returns:
            生成された質問（文字列）
        """
        prompt = self.QUESTION_PROMPT.format(
            text=text,
            scene_type=scene_type
        )

        logger.info(f"Generating question for scene: {scene_type}")

        try:
            response = self.model.generate_content(prompt)
            question = response.text.strip()

            logger.info(f"Generated question: {question}")
            return question

        except Exception as e:
            logger.error(f"Failed to generate question: {e}")
            # フォールバック質問
            return "もう少し詳しく教えてもらえますか？"

    async def generate_deep_dive_question(
        self,
        conversation_history: List[str],
        scene_type: str,
        current_turn: int,
        max_turns: int
    ) -> str:
        """
        複数ターン会話用の深掘り質問を生成

        Args:
            conversation_history: 会話履歴のリスト
            scene_type: シーンタイプ
            current_turn: 現在のターン数
            max_turns: 最大ターン数

        Returns:
            生成された質問（文字列）
        """
        # 会話履歴を整形
        history_text = "\n".join(conversation_history)

        prompt = self.DEEP_DIVE_PROMPT.format(
            conversation_history=history_text,
            scene_type=scene_type,
            current_turn=current_turn,
            max_turns=max_turns
        )

        logger.info(f"Generating deep-dive question (turn {current_turn}/{max_turns})")

        try:
            response = self.model.generate_content(prompt)
            question = response.text.strip()

            logger.info(f"Generated deep-dive question: {question}")
            return question

        except Exception as e:
            logger.error(f"Failed to generate deep-dive question: {e}")
            # フォールバック質問
            return "他に気づいたことはありますか？"

    async def is_deep_enough(
        self,
        conversation_history: List[str]
    ) -> bool:
        """
        会話が十分深掘りできたか判定

        Args:
            conversation_history: 会話履歴のリスト

        Returns:
            十分深掘りできた場合 True
        """
        import json

        # 会話履歴を整形
        history_text = "\n".join(conversation_history)

        prompt = self.DEPTH_CHECK_PROMPT.format(
            conversation_history=history_text
        )

        logger.info("Checking if conversation is deep enough")

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            is_deep = result.get("is_deep_enough", False)
            reason = result.get("reason", "判定理由なし")

            logger.info(f"Depth check: {is_deep} - {reason}")
            return is_deep

        except Exception as e:
            logger.error(f"Failed to check depth: {e}")
            # エラー時は保守的に「まだ深掘りできる」と判定
            return False


class ConversationManager:
    """複数ターン会話の管理"""

    def __init__(
        self,
        question_generator: QuestionGenerator,
        max_turns: int = 3,
        timeout_seconds: int = 60
    ):
        """
        Initialize ConversationManager.

        Args:
            question_generator: QuestionGenerator instance
            max_turns: 最大ターン数
            timeout_seconds: タイムアウト時間（秒）
        """
        self.question_generator = question_generator
        self.max_turns = max_turns
        self.timeout_seconds = timeout_seconds

    async def start_conversation(
        self,
        initial_text: str,
        scene_type: str
    ) -> List[Dict[str, str]]:
        """
        複数ターン会話を開始

        Args:
            initial_text: 初回のメモテキスト
            scene_type: シーンタイプ

        Returns:
            会話履歴のリスト（各要素は {"role": "user"/"assistant", "content": "..."}）
        """
        conversation: List[Dict[str, str]] = [
            {"role": "user", "content": initial_text}
        ]

        current_turn = 1

        while current_turn <= self.max_turns:
            # 質問を生成
            question = await self.question_generator.generate_deep_dive_question(
                conversation_history=[msg["content"] for msg in conversation],
                scene_type=scene_type,
                current_turn=current_turn,
                max_turns=self.max_turns
            )

            # 会話履歴に追加
            conversation.append({
                "role": "assistant",
                "content": question
            })

            # ここで実際のDiscord Botではユーザーの回答を待つ
            # このクラスは会話のロジックのみを担当し、
            # 実際のユーザー入力待ちは呼び出し側が行う
            logger.info(f"Conversation paused at turn {current_turn}, waiting for user response")
            break  # 実際の実装では、ここでユーザー応答を待つ

        return conversation

    def add_user_response(
        self,
        conversation: List[Dict[str, str]],
        response: str
    ) -> List[Dict[str, str]]:
        """
        ユーザーの応答を会話履歴に追加

        Args:
            conversation: 現在の会話履歴
            response: ユーザーの応答

        Returns:
            更新された会話履歴
        """
        conversation.append({
            "role": "user",
            "content": response
        })
        return conversation

    async def should_continue(
        self,
        conversation: List[Dict[str, str]]
    ) -> bool:
        """
        会話を続けるべきか判定

        Args:
            conversation: 現在の会話履歴

        Returns:
            会話を続ける場合 True
        """
        # ターン数チェック
        user_turns = sum(1 for msg in conversation if msg["role"] == "user")
        if user_turns >= self.max_turns:
            logger.info(f"Max turns ({self.max_turns}) reached")
            return False

        # 深さチェック
        conversation_text = [msg["content"] for msg in conversation]
        is_deep = await self.question_generator.is_deep_enough(conversation_text)

        if is_deep:
            logger.info("Conversation is deep enough, ending")
            return False

        return True
