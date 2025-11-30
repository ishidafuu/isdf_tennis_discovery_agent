# AI処理実装

## transcription.py

```python
import google.generativeai as genai
import os
import aiohttp

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def transcribe_audio(audio_url: str) -> str:
    """音声を文字起こし"""

    try:
        # 音声ファイルをダウンロード
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url) as resp:
                audio_data = await resp.read()

        # Gemini で文字起こし
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 音声ファイルをアップロード
        audio_file = genai.upload_file(audio_data, mime_type='audio/ogg')

        # 文字起こしリクエスト
        response = model.generate_content([
            "この音声を文字起こししてください。",
            audio_file
        ])

        return response.text

    except Exception as e:
        print(f"文字起こしエラー: {e}")
        return None
```

---

## structured_extraction.py

```python
import google.generativeai as genai
import json
from src.ai.prompts import get_prompt_for_scene

async def extract_structured_data(text: str, scene_type: str) -> dict:
    """構造化データを抽出"""

    # シーン別のプロンプトを取得
    prompt = get_prompt_for_scene(scene_type, text)

    # Gemini で構造化
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    # JSONをパース
    try:
        structured_data = json.loads(response.text)
    except json.JSONDecodeError:
        # パースに失敗した場合、フォールバック
        structured_data = {"raw_text": text}

    # メタデータを追加
    from datetime import datetime
    structured_data["scene"] = scene_type
    structured_data["date"] = datetime.now().strftime('%Y-%m-%d')
    structured_data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M')
    structured_data["raw_text"] = text

    return structured_data

async def structure_text_memo(text: str, scene_type: str, urls: list = None) -> dict:
    """テキストメモを構造化"""

    prompt = f"""
以下のテニス練習メモを構造化してください。

**シーン:** {scene_type}
**メモ内容:**
{text}

{f"**参考URL:** {', '.join(urls)}" if urls else ""}

以下の形式でJSONを返してください：
{{
    "summary": "一文での要約",
    "details": {{
        "technique": "技術的な内容（あれば）",
        "feeling": "感覚的な内容（あれば）",
        "reference": "参考情報（URLや記事の内容）",
        "next_action": "次回への課題（あれば）"
    }},
    "tags": ["自動生成タグ"],
    "key_points": ["重要ポイント1", "重要ポイント2"]
}}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"raw_text": text, "summary": text[:100]}
```

---

## prompts.py

```python
def get_prompt_for_scene(scene_type: str, text: str) -> str:
    """シーン別のプロンプトを返す"""

    prompts = {
        "壁打ち": get_wall_practice_prompt,
        "スクール": get_school_prompt,
        "試合": get_match_prompt,
    }

    prompt_func = prompts.get(scene_type, get_generic_prompt)
    return prompt_func(text)

def get_wall_practice_prompt(text: str) -> str:
    return f"""
以下の音声メモから、壁打ち練習の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "drill": "実施したドリル（例: フォアハンドストローク）",
  "duration": "時間（分、推定でOK）",
  "focus": "今日の焦点（何を意識したか）",
  "body_sensation": "身体感覚の気づき",
  "improvement": "改善した点",
  "issue": "課題として残った点",
  "next_action": "次回やること"
}}

回答は必ずJSON形式で。値が不明な場合はnullにしてください。
"""

def get_school_prompt(text: str) -> str:
    return f"""
以下の音声メモから、スクール練習の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "coach_feedback": "コーチからの指摘・アドバイス",
  "new_technique": "新しく学んだ技術",
  "practice_content": "練習内容",
  "realization": "自分の気づき",
  "homework": "次回までの課題",
  "next_action": "次回やること"
}}

回答は必ずJSON形式で。値が不明な場合はnullにしてください。
"""

def get_match_prompt(text: str) -> str:
    return f"""
以下の音声メモから、試合の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "opponent": "対戦相手の名前（不明ならnull）",
  "opponent_level": "相手のレベル（初級/中級/上級、推定でOK）",
  "score": "スコア（例: 6-4, 6-3、不明ならnull）",
  "result": "勝ち/負け/不明",
  "good_plays": "良かったプレー・戦術",
  "bad_plays": "課題となったプレー",
  "mental": "メンタル面の気づき",
  "strategy": "戦術・戦略の振り返り",
  "next_action": "次回への課題"
}}

回答は必ずJSON形式で。値が不明な場合はnullにしてください。
"""

def get_generic_prompt(text: str) -> str:
    return f"""
以下の音声メモから、テニス練習の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "summary": "メモの要約",
  "key_points": "重要なポイント（配列）",
  "next_action": "次回やること"
}}

回答は必ずJSON形式で。
"""
```

---

## question_generation.py

```python
import google.generativeai as genai

async def generate_follow_up_question(text: str, scene_type: str) -> str:
    """追加質問を生成"""

    prompt = f"""
以下の音声メモに対して、ソクラテス式の質問を1つ生成してください。

音声メモ:
{text}

シーン: {scene_type}

質問の目的:
- ユーザーの気づきを深める
- 曖昧な表現を具体化させる
- 次のアクションを明確にする

質問の例:
- 「なぜそう思ったんですか？」
- 「具体的にどういう感覚でしたか？」
- 「他に試せることはありますか？」

生成した質問のみを出力してください（前置きや説明不要）。
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text.strip()
```

---

## テスト例

### test_structured_extraction.py

```python
import pytest
from src.ai.structured_extraction import extract_structured_data

@pytest.mark.asyncio
async def test_wall_practice_extraction():
    text = "今日はフォアハンドを30分練習した。トップスピンが安定してきた。"

    result = await extract_structured_data(text, "壁打ち")

    assert result['scene'] == "壁打ち"
    assert 'drill' in result
    assert 'フォアハンド' in result['drill']

@pytest.mark.asyncio
async def test_match_extraction():
    text = "今日の試合、6-4, 6-3で勝った。サーブが良かった。"

    result = await extract_structured_data(text, "試合")

    assert result['scene'] == "試合"
    assert result['score'] == "6-4, 6-3"
    assert result['result'] == "勝ち"
```

---

## 次のドキュメント

- [obsidian-storage.md](obsidian-storage.md) - Obsidianストレージ管理
