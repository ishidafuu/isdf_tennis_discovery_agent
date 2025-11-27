# Phase 1: 処理機能

## 概要

処理フェーズでは、入力された情報をどのように構造化するかを定義します。

**設計原則:**
- **シーン別に最適化**: 壁打ち、スクール、試合で処理を変える
- **前回との関連付け**: サイクルを実現する
- **シンプルな処理**: Phase 1では自動判断は最小限

---

## 処理の全体フロー

```
[入力: 音声文字起こし + シーン情報]
    ↓
[1. シーン別の構造化データ抽出]
    ↓
[2. 前回ログとの関連付け]
    ↓
[3. メタデータの付与]
    ↓
[出力: 構造化データ + Markdown]
```

---

## シーン別の構造化データ抽出

### 基本方針

各シーンで**抽出すべき情報が異なる**ため、プロンプトを変える。

### 壁打ち用プロンプト

```python
def get_wall_practice_prompt(text):
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

回答は必ずJSON形式で。
"""
```

### スクール用プロンプト

```python
def get_school_prompt(text):
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

回答は必ずJSON形式で。
"""
```

### 試合用プロンプト

```python
def get_match_prompt(text):
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

回答は必ずJSON形式で。
"""
```

### 汎用プロンプト（フリー練習用）

```python
def get_generic_prompt(text):
    return f"""
以下の音声メモから、練習の情報を抽出してください。

音声メモ:
{text}

抽出する情報（JSON形式）:
{{
  "practice_content": "練習内容",
  "realization": "気づき",
  "issue": "課題",
  "next_action": "次回やること"
}}

回答は必ずJSON形式で。
"""
```

### 実装コード

```python
import json
from google import generativeai as genai
from datetime import datetime

async def extract_structured_data(text, scene_type):
    """シーン別に構造化データを抽出"""

    # プロンプトを選択
    if scene_type == "壁打ち":
        prompt = get_wall_practice_prompt(text)
    elif scene_type == "スクール":
        prompt = get_school_prompt(text)
    elif scene_type == "試合":
        prompt = get_match_prompt(text)
    else:
        prompt = get_generic_prompt(text)

    # Gemini APIで構造化
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    # JSONをパース
    try:
        structured_data = json.loads(response.text)
    except json.JSONDecodeError:
        # パースに失敗した場合、フォールバック
        structured_data = {"raw_text": text}

    # メタデータを追加
    structured_data["scene"] = scene_type
    structured_data["date"] = datetime.now().strftime('%Y-%m-%d')
    structured_data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M')
    structured_data["raw_text"] = text

    return structured_data
```

---

## テキストメモの構造化

### テキスト構造化プロンプト

```python
async def structure_text_memo(text, scene_type, urls=None):
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

**注意:**
- 簡潔なメモでも、できる限り情報を抽出すること
- URLがある場合は、reference に記載
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return json.loads(response.text)
```

---

## 画像・動画メモの処理

### 基本方針

画像・動画は**自動解析を行わず**、ファイル保存とユーザーコメントの記録のみを行います。

### メタデータの構造

```python
{
    'timestamp': '2025-01-27 14:30',
    'input_type': 'image',  # or 'video'
    'file_path': 'attachments/2025-01-27/2025-01-27_壁打ち_143000.jpg',
    'user_comment': '今日のサーブフォーム。トスの位置を確認。',
    'scene': '壁打ち'
}
```

---

## 前回ログとの関連付け

### 目的

- **サイクルの実現**: 前回の課題が今回どうなったかを追跡
- **継続性**: 「前回→今回→次回」の流れを作る

### ObsidianManager（ファイルベース）

```python
from pathlib import Path
from datetime import datetime
import yaml

class ObsidianManager:
    """Obsidian Vault のファイル操作を管理"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.daily_path = self.vault_path / "daily"

    def get_latest_memo(self, scene_type: str = None) -> dict | None:
        """最新のメモを取得（ファイル名ベース）"""

        # daily/ フォルダ内のmdファイルを取得
        md_files = list(self.daily_path.glob("*.md"))

        if not md_files:
            return None

        # ファイル名でソート（新しい順）
        # ファイル名形式: 2025-01-27-壁打ち.md
        md_files.sort(reverse=True)

        # シーン指定がある場合はフィルタリング
        if scene_type:
            md_files = [f for f in md_files if scene_type in f.name]

        if not md_files:
            return None

        # 最新ファイルを読み込み
        latest_file = md_files[0]
        return self._parse_markdown(latest_file)

    def get_memos_in_range(self, start_date: datetime, end_date: datetime) -> list:
        """期間内のメモを取得"""

        md_files = list(self.daily_path.glob("*.md"))
        memos = []

        for file in md_files:
            # ファイル名から日付を抽出
            date_str = file.name[:10]  # "2025-01-27"
            try:
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if start_date <= file_date <= end_date:
                    memo = self._parse_markdown(file)
                    if memo:
                        memos.append(memo)
            except ValueError:
                continue

        return sorted(memos, key=lambda x: x.get('date', ''))

    def _parse_markdown(self, file_path: Path) -> dict | None:
        """Markdownファイルをパース"""

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Frontmatterを抽出
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return {
                    **frontmatter,
                    'body': body,
                    'file_path': str(file_path)
                }

        return None
```

### 関連性の判定

```python
async def check_relation_with_previous(current_text: str, previous_memo: dict) -> dict:
    """前回メモとの関連性を判定"""

    if not previous_memo:
        return {"is_related": False}

    prompt = f"""
前回のメモと今回のメモを比較して、関連性を判定してください。

前回のメモ（{previous_memo.get('date', '不明')}）:
{previous_memo.get('raw_text', previous_memo.get('body', ''))}

前回の課題:
{previous_memo.get('next_action', 'なし')}

今回のメモ:
{current_text}

判定結果をJSON形式で出力してください:
{{
  "is_related": true/false,
  "relation_type": "課題への取り組み/同じテーマの継続/新しい気づき/関連なし",
  "previous_issue_resolved": true/false/null,
  "comment": "関連性についてのコメント"
}}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"is_related": False}
```

---

## タグの自動生成

```python
async def generate_tags(text: str, scene_type: str) -> list:
    """メモからタグを自動生成"""

    prompt = f"""
以下のテニス練習メモから、適切なタグを5つ以内で生成してください。

シーン: {scene_type}
メモ:
{text}

タグの例:
- 技術名: フォアハンド, バックハンド, サーブ, スライス
- 要素: トス, フットワーク, グリップ
- 状態: 改善, 課題, 発見
- メンタル: 集中, 焦り, 自信

JSON配列形式で出力してください: ["タグ1", "タグ2", ...]
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    try:
        tags = json.loads(response.text)
        return tags[:5]  # 最大5つ
    except json.JSONDecodeError:
        return [scene_type]
```

---

## エラーハンドリング

```python
class ProcessingError(Exception):
    """処理エラーの基底クラス"""
    pass

class GeminiAPIError(ProcessingError):
    """Gemini API関連のエラー"""
    pass

class JSONParseError(ProcessingError):
    """JSONパースエラー"""
    pass

async def safe_extract_structured_data(text: str, scene_type: str) -> dict:
    """エラーハンドリング付きの構造化データ抽出"""

    try:
        return await extract_structured_data(text, scene_type)

    except Exception as e:
        # エラー時はフォールバック
        return {
            "raw_text": text,
            "scene": scene_type,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "error": str(e),
            "processing_status": "fallback"
        }
```

---

## 次のドキュメント

- [output.md](output.md) - 出力機能
- [../02-dialogue/index.md](../02-dialogue/index.md) - Phase 2: 対話の深化
