"""
矛盾検出機能 - 考えの変化や矛盾を指摘
"""
import json
import logging
from typing import List, Dict, Any, Optional

import google.generativeai as genai

from src.storage.obsidian_manager import ObsidianManager


logger = logging.getLogger(__name__)


class ContradictionDetector:
    """矛盾・変化検出器"""

    DETECTION_PROMPT = """今回のメモと過去のメモを比較し、矛盾や考えの変化があれば指摘してください。

【今回のメモ】
{current_text}

【過去のメモ】
{past_memos}

判定基準:
- **矛盾**: 過去と現在で正反対のことを言っている
- **変化**: 以前と異なるアプローチや考え方をしている
- **進化**: 意図的な改善や学習の結果としての変化

判定結果をJSON形式で出力してください:
{{
  "has_contradiction": true/false,
  "contradiction_type": "矛盾" | "変化" | "進化" | null,
  "previous_statement": "過去の発言内容（矛盾/変化がある場合のみ）",
  "current_statement": "今回の発言内容（矛盾/変化がある場合のみ）",
  "comment": "指摘のコメント（ユーザーに問いかける形式で）",
  "confidence": 0.0-1.0
}}

重要:
- 矛盾や変化がない場合は has_contradiction を false にする
- commentは必ず質問形式で（例: 「考えが変わったのですか？」）
- JSON以外のテキストは出力しないでください
"""

    def __init__(
        self,
        model: genai.GenerativeModel,
        obsidian_manager: ObsidianManager
    ):
        """
        Initialize ContradictionDetector.

        Args:
            model: Gemini GenerativeModel instance
            obsidian_manager: ObsidianManager instance
        """
        self.model = model
        self.obsidian_manager = obsidian_manager

    async def detect_contradiction(
        self,
        current_text: str,
        scene_type: Optional[str] = None,
        lookback_count: int = 5,
        confidence_threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """
        矛盾・変化を検出

        Args:
            current_text: 今回のメモテキスト
            scene_type: シーンタイプ（Noneの場合は全シーン）
            lookback_count: 過去何件のメモと比較するか
            confidence_threshold: 自信度の閾値（これ以下は検出しない）

        Returns:
            矛盾が検出された場合は検出結果、なければ None
        """
        # 過去のメモを取得
        past_memos = await self.obsidian_manager.get_latest_memo(
            scene=scene_type,
            count=lookback_count
        )

        if not past_memos or len(past_memos) == 0:
            logger.info("No past memos found for contradiction detection")
            return None

        # 過去メモを整形
        past_memos_text = ""
        for i, memo in enumerate(past_memos, 1):
            date = memo.get('date', '日付不明')
            body = memo.get('raw_text', '') or memo.get('body', '')

            # 長すぎる場合は切り捨て
            if len(body) > 200:
                body = body[:200] + "..."

            past_memos_text += f"""{i}. {date}: {body}

"""

        # プロンプトを構築
        prompt = self.DETECTION_PROMPT.format(
            current_text=current_text,
            past_memos=past_memos_text
        )

        logger.info(f"Detecting contradictions against {len(past_memos)} past memos")

        try:
            # Gemini APIで矛盾検出
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)

            # バリデーション
            if "has_contradiction" not in result:
                logger.warning("Invalid response: missing 'has_contradiction'")
                return None

            # 矛盾がない場合
            if not result["has_contradiction"]:
                logger.info("No contradiction detected")
                return None

            # 自信度チェック
            confidence = result.get("confidence", 0.0)
            if confidence < confidence_threshold:
                logger.info(
                    f"Confidence too low ({confidence:.2f} < {confidence_threshold}), "
                    "ignoring contradiction"
                )
                return None

            logger.info(
                f"Contradiction detected: {result.get('contradiction_type', 'unknown')} "
                f"(confidence: {confidence:.2f})"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse contradiction detection JSON: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error in detect_contradiction: {e}")
            return None

    def format_contradiction_message(self, detection_result: Dict[str, Any]) -> str:
        """
        矛盾検出結果をユーザー向けメッセージに整形

        Args:
            detection_result: detect_contradiction() の戻り値

        Returns:
            ユーザー向けメッセージ（Markdown形式）
        """
        if not detection_result or not detection_result.get("has_contradiction"):
            return ""

        contradiction_type = detection_result.get("contradiction_type", "変化")
        previous = detection_result.get("previous_statement", "（詳細不明）")
        current = detection_result.get("current_statement", "（詳細不明）")
        comment = detection_result.get("comment", "考えが変わりましたか？")
        confidence = detection_result.get("confidence", 0.0)

        # 絵文字を選択
        if contradiction_type == "矛盾":
            emoji = "⚠️"
        elif contradiction_type == "進化":
            emoji = "🌱"
        else:
            emoji = "💭"

        message = f"""
{emoji} **{contradiction_type}に気づきました**

**過去:**
{previous}

**今回:**
{current}

{comment}

（確信度: {confidence:.0%}）
"""

        return message.strip()
