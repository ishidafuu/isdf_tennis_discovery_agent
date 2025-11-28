"""
#質問チャンネルのハンドリング - 過去の記録から質問に回答
"""
import logging
from typing import List, Dict, Any, Optional

import google.generativeai as genai

from src.storage.obsidian_manager import ObsidianManager
from src.analysis.comparison import ComparisonAnalyzer


logger = logging.getLogger(__name__)


class QuestionHandler:
    """質問チャンネルのハンドラー"""

    ANSWER_PROMPT = """以下の質問に、過去のメモを参考にして回答してください。

【質問】
{question}

【参考になる過去のメモ】
{relevant_memos}

回答のガイドライン:
- 過去のメモに基づいて事実を述べる
- ユーザー自身の体験や気づきを引用する
- アドバイスではなく、過去の成功体験を思い出させる
- 質問に対する直接的な答えだけでなく、関連する情報も提供する
- ユーザーが次に取るべきアクションを質問形式で促す

回答:
"""

    def __init__(
        self,
        model: genai.GenerativeModel,
        obsidian_manager: ObsidianManager,
        comparison_analyzer: ComparisonAnalyzer
    ):
        """
        Initialize QuestionHandler.

        Args:
            model: Gemini GenerativeModel instance
            obsidian_manager: ObsidianManager instance
            comparison_analyzer: ComparisonAnalyzer instance
        """
        self.model = model
        self.obsidian_manager = obsidian_manager
        self.comparison_analyzer = comparison_analyzer

    async def search_related_memos(
        self,
        question: str,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        質問に関連するメモを検索

        Args:
            question: 質問テキスト
            user_id: ユーザーID（将来のマルチユーザー対応用）
            limit: 取得する最大件数

        Returns:
            関連メモのリスト
        """
        # ComparisonAnalyzerのキーワード抽出を利用
        keywords = await self.comparison_analyzer.extract_keywords(question)

        logger.info(f"Searching memos for question with keywords: {keywords}")

        # キーワードで検索
        related_memos = []
        for keyword in keywords:
            memos = await self.obsidian_manager.search_by_keyword(
                keyword=keyword,
                limit=limit * 2  # 多めに取得
            )
            related_memos.extend(memos)

        # 重複を除去（ファイルパスでユニーク化）
        unique_memos = {}
        for memo in related_memos:
            filepath = memo.get('filepath', '')
            if filepath and filepath not in unique_memos:
                unique_memos[filepath] = memo

        # 日付でソート（新しい順）
        sorted_memos = sorted(
            unique_memos.values(),
            key=lambda m: m.get('date', ''),
            reverse=True
        )

        # 件数制限
        result = sorted_memos[:limit]

        logger.info(f"Found {len(result)} related memos")
        return result

    async def answer_question(
        self,
        question: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        質問に回答

        Args:
            question: 質問テキスト
            user_id: ユーザーID（将来のマルチユーザー対応用）

        Returns:
            回答の辞書
            {
                "answer": "回答テキスト",
                "related_memos": [関連メモのリスト],
                "keywords": [抽出されたキーワード]
            }
        """
        # 関連メモを検索
        related_memos = await self.search_related_memos(
            question=question,
            user_id=user_id,
            limit=5
        )

        # 関連メモがない場合
        if len(related_memos) == 0:
            logger.info("No related memos found for question")
            return {
                "answer": "関連するメモが見つかりませんでした。\nもっと練習を記録してみてください。",
                "related_memos": [],
                "keywords": []
            }

        # 関連メモを整形
        relevant_memos_text = ""
        for i, memo in enumerate(related_memos, 1):
            date = memo.get('date', '日付不明')
            scene = memo.get('scene', 'unknown')
            body = memo.get('raw_text', '') or memo.get('body', '')

            # 長すぎる場合は切り捨て
            if len(body) > 300:
                body = body[:300] + "..."

            relevant_memos_text += f"""{i}. {date} ({scene})
{body}

"""

        # プロンプトを構築
        prompt = self.ANSWER_PROMPT.format(
            question=question,
            relevant_memos=relevant_memos_text
        )

        logger.info(f"Generating answer for question with {len(related_memos)} related memos")

        try:
            # Geminiで回答生成
            response = self.model.generate_content(prompt)
            answer = response.text.strip()

            logger.info("Answer generated successfully")

            # キーワード抽出
            keywords = await self.comparison_analyzer.extract_keywords(question)

            return {
                "answer": answer,
                "related_memos": related_memos,
                "keywords": keywords
            }

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            # フォールバック
            return {
                "answer": f"回答の生成に失敗しました。\n\n参考になりそうなメモ:\n{relevant_memos_text}",
                "related_memos": related_memos,
                "keywords": []
            }

    def format_answer_message(
        self,
        question: str,
        answer_data: Dict[str, Any]
    ) -> str:
        """
        回答をDiscordメッセージ形式に整形

        Args:
            question: 質問テキスト
            answer_data: answer_question() の戻り値

        Returns:
            Discord用メッセージ（Markdown形式）
        """
        answer = answer_data.get("answer", "回答を生成できませんでした")
        related_memos = answer_data.get("related_memos", [])

        # 参照メモリスト
        memo_list = ""
        if len(related_memos) > 0:
            memo_list = "\n\n**📚 参照したメモ:**\n"
            for memo in related_memos:
                date = memo.get('date', '日付不明')
                scene = memo.get('scene', 'unknown')
                memo_list += f"- {date} ({scene})\n"

        message = f"""❓ **質問**: {question}

{answer}{memo_list}
"""

        return message.strip()
