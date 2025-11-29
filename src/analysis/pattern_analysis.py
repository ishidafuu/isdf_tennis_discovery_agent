"""
Pattern analysis module for identifying trends and insights in practice memos.

This module provides functionality to analyze practice patterns, detect
turning points, and identify correlations in tennis practice data.
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


class PatternAnalyzer:
    """Analyze patterns in practice memos using AI."""

    def __init__(self, model: Optional[genai.GenerativeModel] = None):
        """
        Initialize Pattern Analyzer.

        Args:
            model: Gemini model instance. If None, creates a new one.
        """
        self.model = model or genai.GenerativeModel("gemini-2.5-flash")

    async def extract_condition_patterns(self, memos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract patterns from good and bad condition memos.

        Args:
            memos: List of memo dictionaries

        Returns:
            Dictionary containing:
                - good_patterns: Common themes in good condition
                - bad_patterns: Common themes in bad condition
                - key_differences: Important differences between conditions
                - recommendations: Suggestions for improvement

        Raises:
            ValueError: If memos list is empty or analysis fails
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        # Classify memos into good/bad condition
        good_memos = [m for m in memos if self._is_good_condition(m)]
        bad_memos = [m for m in memos if self._is_bad_condition(m)]

        logger.info(f"📊 Analyzing patterns: {len(good_memos)} good, {len(bad_memos)} bad")

        if not good_memos and not bad_memos:
            return {
                "good_patterns": {},
                "bad_patterns": {},
                "key_differences": [],
                "recommendations": ["データが不足しています。より多くの練習記録を蓄積してください。"]
            }

        prompt = f"""
以下の練習メモを分析し、好調時と不調時のパターンを抽出してください。

【好調時のメモ（{len(good_memos)}件）】
{self._format_memos_for_analysis(good_memos[:10])}

【不調時のメモ（{len(bad_memos)}件）】
{self._format_memos_for_analysis(bad_memos[:10])}

以下の形式でJSON出力してください:
{{
    "good_patterns": {{
        "common_themes": ["共通するテーマ"],
        "physical_sensations": ["身体感覚"],
        "mental_states": ["メンタル状態"],
        "practice_types": ["練習タイプ"]
    }},
    "bad_patterns": {{
        "common_themes": ["共通するテーマ"],
        "physical_sensations": ["身体感覚"],
        "mental_states": ["メンタル状態"],
        "practice_types": ["練習タイプ"]
    }},
    "key_differences": ["好調と不調の重要な違い"],
    "recommendations": ["改善のための提案"]
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
            logger.info("✅ Pattern analysis completed")
            return result

        except Exception as e:
            logger.error(f"❌ Pattern analysis failed: {e}")
            raise ValueError(f"Failed to analyze patterns: {e}")

    async def analyze_time_series(self, memos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze time series trends in practice memos.

        Args:
            memos: List of memo dictionaries with 'date' field

        Returns:
            Dictionary containing:
                - practice_frequency: Frequency changes over time
                - improving_skills: Skills showing improvement
                - ongoing_issues: Persistent challenges
                - turning_points: Key moments in progress
                - growth_forecast: Prediction for future growth

        Raises:
            ValueError: If memos list is empty or analysis fails
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        # Sort by date
        sorted_memos = sorted(memos, key=lambda x: x.get('date', ''))

        # Aggregate by month
        monthly_data = self._aggregate_by_month(sorted_memos)

        logger.info(f"📈 Analyzing time series: {len(monthly_data)} months")

        prompt = f"""
以下の月別データからトレンドを分析してください。

{json.dumps(monthly_data, ensure_ascii=False, indent=2)}

以下の観点で分析:
1. 練習頻度の変化
2. 改善が見られる技術
3. 継続している課題
4. ターニングポイント
5. 次の成長予測

JSON形式で出力してください:
{{
    "practice_frequency": {{
        "trend": "increasing/stable/decreasing",
        "description": "詳細な説明"
    }},
    "improving_skills": [
        {{
            "skill": "技術名",
            "progress": "進捗状況"
        }}
    ],
    "ongoing_issues": [
        {{
            "issue": "課題",
            "duration": "継続期間"
        }}
    ],
    "turning_points": [
        {{
            "month": "YYYY-MM",
            "description": "転機の内容"
        }}
    ],
    "growth_forecast": "今後の成長予測"
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
            logger.info("✅ Time series analysis completed")
            return result

        except Exception as e:
            logger.error(f"❌ Time series analysis failed: {e}")
            raise ValueError(f"Failed to analyze time series: {e}")

    async def find_turning_points(self, memos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify turning points in practice progression.

        A turning point is a moment when significant change occurred:
        - Major insight or breakthrough
        - Technical improvement
        - Mental shift
        - Change in practice approach

        Args:
            memos: List of memo dictionaries

        Returns:
            List of dictionaries containing:
                - date: Date of turning point
                - description: What changed
                - impact: Impact on subsequent practice
                - importance: high/medium/low

        Raises:
            ValueError: If memos list is empty or analysis fails
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        # Sort by date
        sorted_memos = sorted(memos, key=lambda x: x.get('date', ''))

        logger.info(f"🔍 Finding turning points in {len(sorted_memos)} memos")

        prompt = """
以下の練習メモの時系列から、成長のターニングポイント（転機）を特定してください。

【メモ一覧（時系列順）】
"""

        for memo in sorted_memos[:50]:  # Limit to 50 memos to avoid token limit
            date = memo.get('date', '不明')
            scene = memo.get('scene', '不明')
            summary = memo.get('summary', '')
            raw_text = memo.get('raw_text', '')

            text = summary if summary else raw_text[:200]
            prompt += f"\n{date} ({scene}): {text}"

        prompt += """

ターニングポイントとは:
- 大きな気づきがあった時
- 技術的なブレイクスルー
- メンタル面での転換
- 練習方法の変更

以下の形式でJSON出力:
[
    {
        "date": "日付",
        "description": "何が変わったか",
        "impact": "その後への影響",
        "importance": "high/medium/low"
    }
]
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            result = json.loads(response.text)
            logger.info(f"✅ Found {len(result)} turning points")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to find turning points: {e}")
            raise ValueError(f"Failed to find turning points: {e}")

    async def analyze_correlations(
        self,
        memos: List[Dict[str, Any]],
        metric_x: str,
        metric_y: str
    ) -> Dict[str, Any]:
        """
        Analyze correlation between two metrics.

        Args:
            memos: List of memo dictionaries
            metric_x: First metric to analyze (e.g., "practice_frequency", "condition")
            metric_y: Second metric to analyze (e.g., "success_rate", "somatic_marker")

        Returns:
            Dictionary containing correlation analysis

        Raises:
            ValueError: If memos list is empty or metrics are invalid
        """
        if not memos:
            raise ValueError("Memos list cannot be empty")

        logger.info(f"🔗 Analyzing correlation: {metric_x} vs {metric_y}")

        # Extract metrics from memos
        data_points = []
        for memo in memos:
            x_value = memo.get(metric_x)
            y_value = memo.get(metric_y)

            if x_value is not None and y_value is not None:
                data_points.append({
                    "date": memo.get('date', ''),
                    metric_x: x_value,
                    metric_y: y_value
                })

        if not data_points:
            return {
                "correlation": "insufficient_data",
                "description": f"{metric_x}と{metric_y}のデータが不足しています。"
            }

        prompt = f"""
以下のデータから、{metric_x}と{metric_y}の相関を分析してください。

【データポイント】
{json.dumps(data_points, ensure_ascii=False, indent=2)}

以下の形式でJSON出力:
{{
    "correlation": "positive/negative/none/unclear",
    "strength": "strong/moderate/weak",
    "description": "相関の詳細な説明",
    "insights": ["気づき・洞察"],
    "recommendations": ["改善提案"]
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
            logger.info("✅ Correlation analysis completed")
            return result

        except Exception as e:
            logger.error(f"❌ Correlation analysis failed: {e}")
            raise ValueError(f"Failed to analyze correlations: {e}")

    # Helper methods

    def _is_good_condition(self, memo: Dict[str, Any]) -> bool:
        """Check if memo indicates good condition."""
        indicators = ['うまくいった', '改善', '成功', '良かった', '上達', 'できた', '好調']

        condition = memo.get('condition', '').lower()
        if condition in ['good', 'excellent']:
            return True

        text = (
            memo.get('summary', '') + ' ' +
            memo.get('raw_text', '')
        ).lower()

        return any(ind in text for ind in indicators)

    def _is_bad_condition(self, memo: Dict[str, Any]) -> bool:
        """Check if memo indicates bad condition."""
        indicators = ['うまくいかない', '課題', '失敗', '悪い', 'できない', 'ミス', '不調']

        condition = memo.get('condition', '').lower()
        if condition in ['bad', 'poor']:
            return True

        text = (
            memo.get('summary', '') + ' ' +
            memo.get('raw_text', '')
        ).lower()

        return any(ind in text for ind in indicators)

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

    def _aggregate_by_month(self, memos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate memos by month."""
        monthly_data = {}

        for memo in memos:
            date_str = memo.get('date', '')
            if not date_str:
                continue

            month = date_str[:7]  # "2025-01"

            if month not in monthly_data:
                monthly_data[month] = {
                    "count": 0,
                    "improvements": [],
                    "issues": [],
                    "tags": []
                }

            monthly_data[month]["count"] += 1

            # Extract improvements
            if success_patterns := memo.get('success_patterns'):
                for pattern in success_patterns:
                    if isinstance(pattern, dict):
                        desc = pattern.get('description', '')
                    else:
                        desc = str(pattern)
                    if desc:
                        monthly_data[month]["improvements"].append(desc)

            # Extract issues
            if failure_patterns := memo.get('failure_patterns'):
                for pattern in failure_patterns:
                    if isinstance(pattern, dict):
                        symptom = pattern.get('symptom', '')
                    else:
                        symptom = str(pattern)
                    if symptom:
                        monthly_data[month]["issues"].append(symptom)

            if issues := memo.get('issues'):
                for issue in issues:
                    if isinstance(issue, dict):
                        desc = issue.get('description', '')
                    else:
                        desc = str(issue)
                    if desc:
                        monthly_data[month]["issues"].append(desc)

            # Collect tags
            if tags := memo.get('tags'):
                monthly_data[month]["tags"].extend(tags)

        return monthly_data


# Helper function to get analyzer instance
def get_pattern_analyzer(model: Optional[genai.GenerativeModel] = None) -> PatternAnalyzer:
    """
    Get a PatternAnalyzer instance.

    Args:
        model: Optional Gemini model instance

    Returns:
        PatternAnalyzer instance
    """
    return PatternAnalyzer(model)
