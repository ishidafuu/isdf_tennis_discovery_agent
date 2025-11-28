"""
AI自動判断ロジック - メモの内容を分析し、次のアクションを自動判断
"""
import json
import logging
from typing import Dict, Any, Optional, Literal
from enum import Enum

import google.generativeai as genai


logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """次のアクションタイプ"""
    SAVE_ONLY = "save_only"  # そのまま保存（日常的なメモ）
    DEEP_DIVE = "deep_dive"  # 深堀質問すべき（新しい気づき、曖昧な表現）
    COMPARE = "compare"  # 過去と比較すべき（過去に類似テーマあり）


class AutoDecision:
    """AIによる自動判断ロジック"""

    DECISION_PROMPT = """以下の音声メモを分析し、次のアクションを判断してください。

音声メモ:
{text}

シーン: {scene_type}

前回のメモ: {previous_memo}

判断基準:
1. **そのまま保存 (save_only)**: 日常的な記録、特に深掘り不要
   - 例: ルーティンワーク、単純な記録、特に新しい気づきなし

2. **深堀質問 (deep_dive)**: 新しい気づき、曖昧な表現、深掘りする価値あり
   - 例: 「うまくいった」「調子が良かった」などの曖昧な表現
   - 例: 新しい技術を試した、新しい感覚を発見した
   - 例: 具体的な身体感覚が語られていない

3. **過去と比較 (compare)**: 過去に似たテーマがあり、比較すると有益
   - 例: 繰り返し出てくるテーマ（サーブ、バックハンドなど）
   - 例: 前回と異なる結果や感覚が出ている

判定結果をJSON形式で出力してください:
{{
  "action": "save_only" | "deep_dive" | "compare",
  "reason": "判断理由（1-2文で簡潔に）",
  "confidence": 0.0-1.0（自信度、0.0=自信なし、1.0=確信）
}}

重要: JSON以外のテキストは出力しないでください。
"""

    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize AutoDecision.

        Args:
            model: Gemini GenerativeModel instance
        """
        self.model = model

    async def decide_action(
        self,
        text: str,
        scene_type: str,
        previous_memo: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        AIが自動的に次のアクションを判断

        Args:
            text: 音声メモまたはテキストメモ
            scene_type: シーンタイプ（wall_practice, school, match, etc.）
            previous_memo: 前回のメモ（辞書形式）
            confidence_threshold: 自信度の閾値（これ以下の場合はデフォルトアクション）

        Returns:
            判断結果の辞書
            {
                "action": "save_only" | "deep_dive" | "compare",
                "reason": "判断理由",
                "confidence": 0.0-1.0
            }

        Raises:
            ValueError: JSON抽出に失敗した場合
        """
        # 前回メモのテキスト化
        previous_text = "なし"
        if previous_memo:
            previous_text = previous_memo.get('raw_text', '') or previous_memo.get('body', '')
            if previous_text:
                previous_text = f"{previous_memo.get('date', '日付不明')}: {previous_text[:200]}..."

        # プロンプトを構築
        prompt = self.DECISION_PROMPT.format(
            text=text,
            scene_type=scene_type,
            previous_memo=previous_text
        )

        logger.info(f"Deciding action for scene: {scene_type}")

        try:
            # Gemini APIで判断（同期呼び出し）
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            # レスポンステキストを取得
            response_text = response.text

            # JSONをパース
            decision = json.loads(response_text)

            # バリデーション
            if "action" not in decision or "confidence" not in decision:
                raise ValueError("Missing required fields in decision response")

            # アクションタイプを検証
            if decision["action"] not in [e.value for e in ActionType]:
                logger.warning(f"Invalid action type: {decision['action']}, defaulting to save_only")
                decision["action"] = ActionType.SAVE_ONLY.value

            # 自信度が低い場合はデフォルト（保存のみ）
            if decision["confidence"] < confidence_threshold:
                logger.info(
                    f"Low confidence ({decision['confidence']:.2f} < {confidence_threshold}), "
                    f"defaulting to save_only"
                )
                decision["action"] = ActionType.SAVE_ONLY.value
                decision["reason"] = f"自信度が低いため保存のみ（元の判断: {decision.get('reason', 'なし')}）"

            logger.info(
                f"Decision: {decision['action']} (confidence: {decision['confidence']:.2f}) "
                f"- {decision.get('reason', 'No reason provided')}"
            )

            return decision

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse decision JSON: {e}")
            raise ValueError(f"Failed to parse decision JSON: {e}\nResponse: {response_text}")

        except Exception as e:
            logger.error(f"Unexpected error in decide_action: {e}")
            # フォールバック: エラー時はデフォルトアクション
            return {
                "action": ActionType.SAVE_ONLY.value,
                "reason": f"エラーが発生したため保存のみ: {str(e)}",
                "confidence": 0.0
            }

    def should_deep_dive(self, decision: Dict[str, Any]) -> bool:
        """
        深堀質問すべきかどうか判定

        Args:
            decision: decide_action()の戻り値

        Returns:
            深堀すべき場合 True
        """
        return decision.get("action") == ActionType.DEEP_DIVE.value

    def should_compare(self, decision: Dict[str, Any]) -> bool:
        """
        過去と比較すべきかどうか判定

        Args:
            decision: decide_action()の戻り値

        Returns:
            比較すべき場合 True
        """
        return decision.get("action") == ActionType.COMPARE.value

    def should_save_only(self, decision: Dict[str, Any]) -> bool:
        """
        そのまま保存のみかどうか判定

        Args:
            decision: decide_action()の戻り値

        Returns:
            保存のみの場合 True
        """
        return decision.get("action") == ActionType.SAVE_ONLY.value
