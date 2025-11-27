"""
Prompts for different tennis practice scenes.
"""

# シーン別の構造化データ抽出プロンプト

def get_wall_practice_prompt(text: str) -> str:
    """
    壁打ち用プロンプト

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return f"""以下の音声メモから、壁打ち練習の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "tags": ["技術カテゴリ（例: forehand, backhand, serve等）"],
  "drill": "実施したドリル（例: フォアハンドストローク）",
  "duration": "時間（分、推定でOK）",
  "focus": "今日の焦点（何を意識したか）",
  "body_sensation": "身体感覚の気づき",
  "improvement": "改善した点",
  "issue": "課題として残った点",
  "next_action": "次回やること",
  "summary": "練習の簡潔な要約（2-3文）"
}}

**重要な注意事項:**
- すべてのフィールドは必須です。値がない場合は空文字列""または0を使用
- tags は配列形式で、空の場合は []
- duration は数値（分単位）、不明な場合は 0
- ユーザーが明示的に言及していない項目は空文字列""にする
- 推測や一般論は避け、ユーザーの実際の体験のみを抽出する
- JSON以外のテキストは出力しない
"""


def get_school_prompt(text: str) -> str:
    """
    スクール用プロンプト

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return f"""以下の音声メモから、スクール練習の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "tags": ["技術カテゴリ（例: forehand, backhand, serve等）"],
  "coach_feedback": "コーチからの指摘・アドバイス",
  "new_technique": "新しく学んだ技術",
  "practice_content": "練習内容",
  "realization": "自分の気づき",
  "homework": "次回までの課題",
  "next_action": "次回やること",
  "summary": "練習の簡潔な要約（2-3文）"
}}

**重要な注意事項:**
- すべてのフィールドは必須です。値がない場合は空文字列""を使用
- tags は配列形式で、空の場合は []
- ユーザーが明示的に言及していない項目は空文字列""にする
- 推測や一般論は避け、ユーザーの実際の体験のみを抽出する
- JSON以外のテキストは出力しない
"""


def get_match_prompt(text: str) -> str:
    """
    試合用プロンプト

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return f"""以下の音声メモから、試合の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "tags": ["試合関連タグ（例: match, singles, doubles等）"],
  "opponent": "対戦相手の名前（不明なら空文字列）",
  "opponent_level": "相手のレベル（初級/中級/上級、推定でOK）",
  "score": "スコア（例: 6-4, 6-3、不明なら空文字列）",
  "result": "勝ち/負け/不明",
  "good_plays": "良かったプレー・戦術",
  "bad_plays": "課題となったプレー",
  "mental": "メンタル面の気づき",
  "strategy": "戦術・戦略の振り返り",
  "next_action": "次回への課題",
  "summary": "試合の簡潔な要約（2-3文）"
}}

**重要な注意事項:**
- すべてのフィールドは必須です。値がない場合は空文字列""を使用
- tags は配列形式で、空の場合は []
- result は "勝ち"、"負け"、"不明" のいずれか
- ユーザーが明示的に言及していない項目は空文字列""にする
- 推測や一般論は避け、ユーザーの実際の体験のみを抽出する
- JSON以外のテキストは出力しない
"""


def get_generic_prompt(text: str) -> str:
    """
    汎用プロンプト（フリー練習等）

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return f"""以下の音声メモから、練習の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "tags": ["技術カテゴリ"],
  "practice_content": "練習内容",
  "realization": "気づき",
  "issue": "課題",
  "next_action": "次回やること",
  "summary": "練習の簡潔な要約（2-3文）"
}}

**重要な注意事項:**
- すべてのフィールドは必須です。値がない場合は空文字列""を使用
- tags は配列形式で、空の場合は []
- ユーザーが明示的に言及していない項目は空文字列""にする
- 推測や一般論は避け、ユーザーの実際の体験のみを抽出する
- JSON以外のテキストは出力しない
"""


# シーンのマッピング定義
SCENE_NAMES = {
    "壁打ち": "wall_practice",
    "スクール": "school",
    "試合": "match",
    "フリー練習": "free_practice",
    "振り返り": "reflection"
}

# プロンプト選択関数
PROMPT_FUNCTIONS = {
    "wall_practice": get_wall_practice_prompt,
    "school": get_school_prompt,
    "match": get_match_prompt,
    "free_practice": get_generic_prompt,
}


def get_prompt_for_scene(scene_type: str, text: str) -> str:
    """
    シーンタイプに応じたプロンプトを取得

    Args:
        scene_type: シーンタイプ（"wall_practice", "school", "match", etc.）
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    prompt_func = PROMPT_FUNCTIONS.get(scene_type, get_generic_prompt)
    return prompt_func(text)
