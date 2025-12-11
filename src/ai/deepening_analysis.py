"""
AI analysis for deepening information from Discord replies.

Analyzes user replies to practice memos and formats them
as structured deepening information.
"""
import json
from typing import Optional, Dict, Any


async def analyze_and_format_reply(gemini_client, reply_content: str) -> Optional[Dict[str, Any]]:
    """
    Analyze and format a reply as deepening information.

    Args:
        gemini_client: GeminiClient instance
        reply_content: Content of the user's reply

    Returns:
        Dictionary containing:
        - is_deepening: bool (whether this is deepening info)
        - pattern: str (contrast/change/reason/detail)
        - formatted: str (formatted Markdown)
        - summary: str (summary for user confirmation)

        Returns None if not deepening information.
    """
    prompt = f"""
以下のテキストを分析してください。

テキスト:
{reply_content}

タスク:
1. これは「深堀り情報」ですか？
   - 深堀り情報: テニスの技術的な気づきに関する詳細情報（対比、変化、根拠、具体化など）
   - 深堀り情報でない: 「了解」「ありがとう」「OK」などの挨拶や短い返答

2. 深堀り情報の場合、以下のどのパターンに該当しますか？
   - contrast: 他の方法との対比（「〇〇以外だとどうなる？」への回答）
   - change: 以前との変化（「以前はどうだった？」への回答）
   - reason: 気づいた理由・根拠（「なぜそう気づいた？」への回答）
   - detail: 具体的な変更点（「どこをどう変えた？」への回答）

3. 深堀り情報の場合、Markdown形式で整形してください。

出力形式（JSON）:
{{
  "is_deepening": true/false,
  "pattern": "contrast" | "change" | "reason" | "detail" | null,
  "formatted": "整形されたMarkdown文字列",
  "summary": "ユーザーへの確認メッセージ"
}}

例:
入力: 「スピンだと打点がずれて変な回転がかかる。スライスは安定するけどスピードが出ない」
出力:
{{
  "is_deepening": true,
  "pattern": "contrast",
  "formatted": "\\n### 深堀り情報\\n\\n**対比**: フラット以外だとどうなる？\\n- スピン: 打点がずれて変な回転がかかる\\n- スライス: 安定するがスピード不足\\n",
  "summary": "対比情報を記録しました:\\n- スピン: 打点がずれて変な回転\\n- スライス: 安定するがスピード不足"
}}

入力: 「了解」
出力:
{{
  "is_deepening": false,
  "pattern": null,
  "formatted": "",
  "summary": ""
}}

それでは、上記のテキストを分析してJSON形式で出力してください。
"""

    try:
        response = await gemini_client.generate_content(prompt)
        response_text = response.text.strip()

        # Extract JSON from response (may be wrapped in code blocks)
        if "```json" in response_text:
            json_start = response_text.index("```json") + 7
            json_end = response_text.rindex("```")
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.index("```") + 3
            json_end = response_text.rindex("```")
            response_text = response_text[json_start:json_end].strip()

        result = json.loads(response_text)

        return result if result.get('is_deepening') else None

    except Exception as e:
        print(f"Error analyzing reply: {e}")
        return None


def format_deepening_markdown(pattern: str, content: str) -> str:
    """
    Format deepening information as Markdown.

    Args:
        pattern: Question pattern (contrast/change/reason/detail)
        content: Reply content

    Returns:
        Formatted Markdown string
    """
    pattern_labels = {
        'contrast': '対比',
        'change': '変化',
        'reason': '根拠',
        'detail': '具体化'
    }

    label = pattern_labels.get(pattern, '補足')

    return f"""

### 深堀り情報

**{label}**:
{content}
"""
