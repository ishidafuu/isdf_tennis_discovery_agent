"""
過去メモとの比較分析機能
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import google.generativeai as genai

from src.storage.obsidian_manager import ObsidianManager


logger = logging.getLogger(__name__)


class ComparisonAnalyzer:
    """過去メモとの比較分析"""

    COMPARISON_PROMPT = """今回のメモと過去のメモを比較分析してください。

【今回のメモ】
{current_text}

【過去のメモ】
{past_memos}

以下の観点で分析してください:
1. **共通点**: 何が一貫しているか（技術、感覚、パターン）
2. **変化**: 何が改善/変化したか（ポジティブな変化、ネガティブな変化）
3. **パターン**: 繰り返し出てくるテーマや傾向
4. **提案**: 次に意識すべきこと（ユーザーの気づきを促す質問形式で）

分析結果を以下の形式で出力してください:

## 📊 過去との比較

### 共通点
[共通するパターンや一貫している要素]

### 変化
[改善点や変化したポイント]

### 繰り返しのパターン
[繰り返し出てくるテーマ]

### 💡 次に意識すること
[質問形式での提案]

重要: 分析結果のみを出力し、前置きや説明は不要です。
"""

    KEYWORD_EXTRACTION_PROMPT = """以下のテキストから、重要なキーワードを3-5個抽出してください。

テキスト:
{text}

抽出基準:
- 技術名（サーブ、フォアハンド、バックハンドなど）
- 身体部位や感覚に関する言葉
- 練習内容や課題を表す言葉

JSON形式で出力してください:
{{
  "keywords": ["キーワード1", "キーワード2", ...]
}}

重要: JSON以外のテキストは出力しないでください。
"""

    def __init__(
        self,
        model: genai.GenerativeModel,
        obsidian_manager: ObsidianManager
    ):
        """
        Initialize ComparisonAnalyzer.

        Args:
            model: Gemini GenerativeModel instance
            obsidian_manager: ObsidianManager instance
        """
        self.model = model
        self.obsidian_manager = obsidian_manager

    async def extract_keywords(self, text: str) -> List[str]:
        """
        テキストからキーワードを抽出

        Args:
            text: テキスト

        Returns:
            キーワードのリスト
        """
        import json

        prompt = self.KEYWORD_EXTRACTION_PROMPT.format(text=text)

        logger.info("Extracting keywords from text")

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            data = json.loads(response.text)
            keywords = data.get("keywords", [])

            logger.info(f"Extracted keywords: {keywords}")
            return keywords

        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            # フォールバック: 簡単な単語分割
            words = text.split()
            return words[:3] if len(words) >= 3 else words

    async def search_similar_memos(
        self,
        text: str,
        scene_type: Optional[str] = None,
        limit: int = 5,
        exclude_recent_days: int = 0
    ) -> List[Dict[str, Any]]:
        """
        類似するメモを検索

        Args:
            text: 検索対象のテキスト
            scene_type: シーンタイプ（Noneの場合は全シーン）
            limit: 取得する最大件数
            exclude_recent_days: 直近N日間を除外（0の場合は除外なし）

        Returns:
            類似メモのリスト
        """
        # キーワード抽出
        keywords = await self.extract_keywords(text)

        if not keywords:
            logger.warning("No keywords extracted, using all memos")
            # キーワードがない場合は最新のメモを取得
            return await self.obsidian_manager.get_memos_in_range(
                start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                end_date=datetime.now().strftime("%Y-%m-%d"),
                scene=scene_type,
                limit=limit
            )

        # キーワードで検索
        similar_memos = []
        for keyword in keywords:
            memos = await self.obsidian_manager.search_by_keyword(
                keyword=keyword,
                scene=scene_type,
                limit=limit * 2  # 多めに取得してフィルタリング
            )
            similar_memos.extend(memos)

        # 重複を除去（ファイルパスでユニーク化）
        unique_memos = {}
        for memo in similar_memos:
            filepath = memo.get('filepath', '')
            if filepath and filepath not in unique_memos:
                unique_memos[filepath] = memo

        # 日付でフィルタリング（直近N日を除外）
        if exclude_recent_days > 0:
            cutoff_date = datetime.now() - timedelta(days=exclude_recent_days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")

            filtered_memos = [
                memo for memo in unique_memos.values()
                if memo.get('date', '') < cutoff_str
            ]
        else:
            filtered_memos = list(unique_memos.values())

        # 日付でソート（新しい順）
        filtered_memos.sort(
            key=lambda m: m.get('date', ''), reverse=True
        )

        # 件数制限
        result = filtered_memos[:limit]

        logger.info(f"Found {len(result)} similar memos (keywords: {keywords})")
        return result

    async def compare_with_past(
        self,
        current_text: str,
        scene_type: Optional[str] = None,
        limit: int = 3
    ) -> str:
        """
        過去のメモと比較分析

        Args:
            current_text: 今回のメモテキスト
            scene_type: シーンタイプ
            limit: 比較する過去メモの最大件数

        Returns:
            比較分析結果（Markdown形式）
        """
        # 類似メモを検索
        similar_memos = await self.search_similar_memos(
            text=current_text,
            scene_type=scene_type,
            limit=limit,
            exclude_recent_days=3  # 直近3日は除外
        )

        if len(similar_memos) == 0:
            logger.info("No similar memos found")
            return "過去に類似するメモが見つかりませんでした。\nもっと練習を記録してみてください。"

        # 過去メモを整形
        past_memos_text = ""
        for i, memo in enumerate(similar_memos, 1):
            date = memo.get('date', '日付不明')
            scene = memo.get('scene', 'unknown')
            body = memo.get('raw_text', '') or memo.get('body', '')

            # 長すぎる場合は切り捨て
            if len(body) > 300:
                body = body[:300] + "..."

            past_memos_text += f"""{i}. {date} ({scene})
{body}

"""

        # プロンプトを構築
        prompt = self.COMPARISON_PROMPT.format(
            current_text=current_text,
            past_memos=past_memos_text
        )

        logger.info(f"Comparing with {len(similar_memos)} past memos")

        try:
            # Geminiで比較分析
            response = self.model.generate_content(prompt)
            analysis = response.text.strip()

            logger.info("Comparison analysis completed")
            return analysis

        except Exception as e:
            logger.error(f"Failed to generate comparison analysis: {e}")
            # フォールバック
            return f"""## 📊 過去との比較

過去に {len(similar_memos)} 件の類似するメモが見つかりました:

{past_memos_text}

**エラー**: 分析の生成に失敗しました。手動で比較してみてください。
"""
