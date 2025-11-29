"""
Prediction and recommendation module for tennis practice.

This module provides functionality to predict growth, suggest practice menus,
and forecast condition based on historical practice data.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PracticePredictor:
    """Predict growth and generate recommendations based on practice history."""

    def __init__(self, model: Optional[genai.GenerativeModel] = None):
        """
        Initialize Practice Predictor.

        Args:
            model: Gemini model instance. If None, creates a new one.
        """
        self.model = model or genai.GenerativeModel("gemini-2.5-flash")

    async def predict_growth(
        self,
        memos: List[Dict[str, Any]],
        target_skill: Optional[str] = None,
        months: int = 3
    ) -> Dict[str, Any]:
        """
        Predict future growth based on recent practice history.

        Args:
            memos: List of memo dictionaries
            target_skill: Optional specific skill to analyze
            months: Number of recent months to analyze (default: 3)

        Returns:
            Dictionary containing:
                - growing_skills: Skills showing improvement
                - struggling_skills: Skills with challenges
                - one_month_forecast: Prediction for next month
                - recommended_focus: Recommended practice areas

        Raises:
            ValueError: If memos list is empty or prediction fails
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        # Get recent memos
        recent_memos = self._get_recent_memos(memos, months)

        logger.info(f"🔮 Predicting growth from {len(recent_memos)} recent memos")

        prompt = f"""
以下の練習メモを分析し、今後の成長を予測してください。

【最近{months}ヶ月のメモ（{len(recent_memos)}件）】
{self._format_memos_for_analysis(recent_memos)}

{f"【分析対象の技術】: {target_skill}" if target_skill else ""}

以下の観点で予測:
1. 順調に成長している技術
2. 伸び悩んでいる技術
3. 今後1ヶ月での予測
4. 重点的に練習すべきこと

JSON形式で出力:
{{
    "growing_skills": [
        {{
            "skill": "技術名",
            "progress": "進捗状況",
            "prediction": "予測"
        }}
    ],
    "struggling_skills": [
        {{
            "skill": "技術名",
            "barrier": "壁となっていること",
            "suggestion": "提案"
        }}
    ],
    "one_month_forecast": "1ヶ月後の予測",
    "recommended_focus": ["重点練習項目"]
}}
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            logger.info("✅ Growth prediction completed")
            return result

        except Exception as e:
            logger.error(f"❌ Growth prediction failed: {e}")
            raise ValueError(f"Failed to predict growth: {e}")

    async def suggest_practice_menu(
        self,
        memos: List[Dict[str, Any]],
        available_time: int = 60,
        scene: str = "壁打ち"
    ) -> str:
        """
        Generate a practice menu based on recent challenges and goals.

        Args:
            memos: List of memo dictionaries
            available_time: Available practice time in minutes (default: 60)
            scene: Practice scene type (default: "壁打ち")

        Returns:
            Formatted practice menu in Markdown

        Raises:
            ValueError: If memos list is empty or generation fails
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        # Extract recent issues and next actions
        recent_issues = []
        next_actions = []

        for memo in memos[-10:]:  # Last 10 memos
            if issues := memo.get('issues'):
                for issue in issues:
                    if isinstance(issue, dict):
                        desc = issue.get('description', '')
                    else:
                        desc = str(issue)
                    if desc:
                        recent_issues.append(desc)

            if actions := memo.get('next_actions'):
                for action in actions:
                    if isinstance(action, dict):
                        theme = action.get('theme', '')
                    else:
                        theme = str(action)
                    if theme:
                        next_actions.append(theme)

        logger.info(f"📋 Generating practice menu for {scene} ({available_time}分)")

        prompt = f"""
以下の情報を元に、練習メニューを提案してください。

【練習時間】{available_time}分
【練習場所】{scene}

【最近の課題】
{chr(10).join(f'- {issue}' for issue in recent_issues[:5])}

【次回のアクション】
{chr(10).join(f'- {action}' for action in next_actions[:5])}

以下の形式で練習メニューを作成:

## 今日の練習メニュー（{available_time}分）

### ウォームアップ（5分）
- 内容

### メイン練習1（XX分）
- 内容
- ポイント

### メイン練習2（XX分）
- 内容
- ポイント

### クールダウン（5分）
- 内容

### 今日の意識ポイント
- 課題に対するフォーカスポイント
"""

        try:
            response = self.model.generate_content(prompt)
            logger.info("✅ Practice menu generated")
            return response.text.strip()

        except Exception as e:
            logger.error(f"❌ Practice menu generation failed: {e}")
            raise ValueError(f"Failed to generate practice menu: {e}")

    async def predict_condition(self, memos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict current condition based on recent practice patterns.

        Args:
            memos: List of memo dictionaries

        Returns:
            Dictionary containing:
                - overall_condition: good/normal/needs_rest
                - fatigue_level: 1-5 scale
                - recommendation: Recommendation for today's practice
                - warning_signs: List of warning signs to watch for

        Raises:
            ValueError: If memos list is empty or prediction fails
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        # Get last 14 days of memos
        recent_memos = memos[-14:]

        # Calculate practice intervals
        practice_intervals = self._calculate_practice_intervals(recent_memos)

        # Count fatigue indicators
        fatigue_indicators = self._count_fatigue_indicators(recent_memos)

        logger.info(f"🏥 Predicting condition from {len(recent_memos)} recent memos")

        prompt = f"""
以下の情報から、現在のコンディションを予測してください。

【練習間隔（日）】
{practice_intervals}

【疲労関連のキーワード出現数】
{fatigue_indicators}

【最近のメモの傾向】
{self._format_recent_trends(recent_memos)}

以下の形式でJSON出力:
{{
    "overall_condition": "good/normal/needs_rest",
    "fatigue_level": 1-5,
    "recommendation": "今日の練習についての提案",
    "warning_signs": ["注意すべきサイン"]
}}
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            logger.info("✅ Condition prediction completed")
            return result

        except Exception as e:
            logger.error(f"❌ Condition prediction failed: {e}")
            raise ValueError(f"Failed to predict condition: {e}")

    async def recommend_next_skill(self, memos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recommend the next skill to focus on based on current progress.

        Args:
            memos: List of memo dictionaries

        Returns:
            Dictionary containing:
                - recommended_skill: Skill to focus on
                - reasoning: Why this skill was chosen
                - prerequisites: What to prepare for this skill
                - expected_timeline: Expected time to improve

        Raises:
            ValueError: If memos list is empty or recommendation fails
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        logger.info(f"🎯 Recommending next skill from {len(memos)} memos")

        # Get recent memos
        recent_memos = self._get_recent_memos(memos, months=2)

        prompt = f"""
以下の練習メモから、次に取り組むべき技術を推奨してください。

【最近の練習記録】
{self._format_memos_for_analysis(recent_memos)}

以下の観点で分析:
1. 現在のレベル
2. 成長している技術
3. まだ手をつけていない技術
4. 次のステップとして適切な技術

JSON形式で出力:
{{
    "recommended_skill": "推奨する技術",
    "reasoning": "この技術を選んだ理由",
    "prerequisites": ["準備すべきこと"],
    "expected_timeline": "上達までの見込み期間"
}}
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            logger.info(f"✅ Recommended skill: {result.get('recommended_skill')}")
            return result

        except Exception as e:
            logger.error(f"❌ Skill recommendation failed: {e}")
            raise ValueError(f"Failed to recommend next skill: {e}")

    # Helper methods

    def _get_recent_memos(self, memos: List[Dict[str, Any]], months: int) -> List[Dict[str, Any]]:
        """Get memos from the last N months."""
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        recent = [m for m in memos if m.get('date', '') >= cutoff_str]

        # If no recent memos, return the last 10
        if not recent:
            return memos[-10:] if len(memos) >= 10 else memos

        return recent

    def _calculate_practice_intervals(self, memos: List[Dict[str, Any]]) -> str:
        """Calculate intervals between practice sessions."""
        if len(memos) < 2:
            return "データ不足"

        intervals = []
        sorted_memos = sorted(memos, key=lambda x: x.get('date', ''))

        for i in range(1, len(sorted_memos)):
            prev_date = sorted_memos[i-1].get('date', '')
            curr_date = sorted_memos[i].get('date', '')

            if prev_date and curr_date:
                try:
                    prev = datetime.strptime(prev_date, "%Y-%m-%d")
                    curr = datetime.strptime(curr_date, "%Y-%m-%d")
                    interval = (curr - prev).days
                    intervals.append(interval)
                except:
                    pass

        if not intervals:
            return "データ不足"

        avg_interval = sum(intervals) / len(intervals)
        return f"平均{avg_interval:.1f}日間隔、最短{min(intervals)}日、最長{max(intervals)}日"

    def _count_fatigue_indicators(self, memos: List[Dict[str, Any]]) -> int:
        """Count fatigue-related keywords in recent memos."""
        fatigue_keywords = [
            '疲れ', '疲労', '痛い', '痛み', 'だるい', '重い', '張り',
            '違和感', '無理', '休み', '休養'
        ]

        count = 0
        for memo in memos:
            text = (
                memo.get('summary', '') + ' ' +
                memo.get('raw_text', '')
            ).lower()

            for keyword in fatigue_keywords:
                count += text.count(keyword)

        return count

    def _format_recent_trends(self, memos: List[Dict[str, Any]]) -> str:
        """Format recent trends for analysis."""
        trends = []

        # Condition trend
        conditions = [m.get('condition', 'normal') for m in memos]
        good_count = sum(1 for c in conditions if c in ['good', 'excellent'])
        bad_count = sum(1 for c in conditions if c in ['bad', 'poor'])

        trends.append(f"調子: 好調{good_count}回、不調{bad_count}回")

        # Practice frequency
        trends.append(f"練習回数: {len(memos)}回（過去14日間）")

        return '\n'.join(trends)

    def _format_memos_for_analysis(self, memos: List[Dict[str, Any]]) -> str:
        """Format memos for AI analysis."""
        formatted = []

        for i, memo in enumerate(memos, 1):
            date = memo.get('date', '不明')
            scene = memo.get('scene', '不明')
            summary = memo.get('summary', '')
            raw_text = memo.get('raw_text', '')

            text = summary if summary else raw_text[:200]

            formatted.append(f"{i}. [{date}] ({scene}): {text}")

        return '\n'.join(formatted)


# Helper function to get predictor instance
def get_practice_predictor(model: Optional[genai.GenerativeModel] = None) -> PracticePredictor:
    """
    Get a PracticePredictor instance.

    Args:
        model: Optional Gemini model instance

    Returns:
        PracticePredictor instance
    """
    return PracticePredictor(model)
