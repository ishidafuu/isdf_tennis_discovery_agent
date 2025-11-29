"""
Analysis channel handler for analyzing practice memos over time periods.

#分析チャンネルでの期間分析機能。「今月の成長を分析して」などのリクエストに対応。
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re


def detect_period_from_text(text: str) -> Dict[str, Any]:
    """
    テキストから期間を判定する。

    Args:
        text: ユーザーの入力テキスト

    Returns:
        期間情報を含む辞書 {"days": int, "label": str}
    """
    text_lower = text.lower()

    # 期間パターンのマッピング
    patterns = [
        (r'今週|this week|week', {"days": 7, "label": "今週"}),
        (r'今月|this month|month', {"days": 30, "label": "今月"}),
        (r'3ヶ月|3か月|three months', {"days": 90, "label": "3ヶ月"}),
        (r'半年|six months', {"days": 180, "label": "半年"}),
        (r'1年|一年|year', {"days": 365, "label": "1年"}),
    ]

    for pattern, period_info in patterns:
        if re.search(pattern, text_lower):
            return period_info

    # デフォルト: 今月
    return {"days": 30, "label": "今月"}


async def analyze_memos_with_ai(
    memos: list,
    period: str,
    ai_model
) -> str:
    """
    メモをAIで分析する。

    Args:
        memos: メモのリスト
        period: 期間ラベル（"今月"、"3ヶ月"など）
        ai_model: Gemini AIモデルインスタンス

    Returns:
        分析結果のテキスト
    """
    if not memos:
        return f"{period}のメモがありません。"

    # メモをテキストにまとめる
    memo_text = ""
    for memo in memos:
        date = memo.get('date', '不明')
        scene = memo.get('scene', '不明')
        body = memo.get('body', '')

        # 主要な情報のみを抽出（全文は長すぎる可能性）
        improvement = extract_section(body, '改善')
        issue = extract_section(body, '課題')

        memo_text += f"""
### {date} ({scene})
改善: {improvement or 'なし'}
課題: {issue or 'なし'}

"""

    # AI分析プロンプト
    prompt = f"""以下は、ユーザーの過去{period}の練習メモです。
成長を分析してください。

【メモ】
{memo_text}

【分析項目】
1. 改善した点（具体的に）
2. 継続中の課題
3. 頻繁に出てくるテーマ
4. 次に取り組むべきこと
5. 全体的な評価とアドバイス

【分析結果】
"""

    # Gemini AIで分析
    response = ai_model.generate_content(prompt)

    return response.text


def extract_section(markdown_text: str, section_name: str) -> Optional[str]:
    """
    Markdownから特定のセクションを抽出する。

    Args:
        markdown_text: Markdownテキスト
        section_name: セクション名（例: "改善"、"課題"）

    Returns:
        セクションの内容、または None
    """
    # セクションのパターン
    patterns = [
        rf'## (?:{section_name}|{section_name.upper()})[^\n]*\n(.+?)(?=\n##|\Z)',
        rf'{section_name}.*?[:：]\s*(.+?)(?=\n|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, markdown_text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # 長さ制限
            if len(content) > 200:
                content = content[:200] + "..."
            return content

    return None


def format_analysis_response(
    period_label: str,
    memo_count: int,
    analysis_text: str
) -> str:
    """
    分析結果を整形されたMarkdownで返す。

    Args:
        period_label: 期間ラベル（"今月"など）
        memo_count: メモの件数
        analysis_text: AI分析結果

    Returns:
        整形された分析レポート
    """
    response = f"""📊 **{period_label}の分析**

練習記録: {memo_count}件

{analysis_text}

---
*この分析は過去{period_label}の練習メモを基に生成されました。*
"""
    return response
