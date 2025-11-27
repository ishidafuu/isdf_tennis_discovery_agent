"""
Scene-specific Markdown templates for Obsidian.
"""
from datetime import datetime
from typing import Any, Dict
import yaml


def build_wall_practice_markdown(data: Dict[str, Any], raw_transcript: str = "") -> str:
    """
    壁打ちメモのMarkdown生成

    Args:
        data: 構造化データ
        raw_transcript: 文字起こし全文

    Returns:
        Markdown文字列
    """
    date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Frontmatter
    frontmatter_data = {
        "date": date_str,
        "scene": "壁打ち",
        "duration": data.get('duration', 0),
        "tags": data.get('tags', ['tennis', 'wall-practice']),
    }
    frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    markdown = f"""---
{frontmatter}---

# 壁打ち練習 - {date_str}

## 今日の焦点

{data.get('focus', '')}

## 身体感覚の気づき

> [!note] リアルタイムメモ
> {data.get('body_sensation', '')}

## 改善した点

{data.get('improvement', '')}

## 課題として残った点

{data.get('issue', '')}

## 次回やること

{data.get('next_action', '')}

## 練習内容

- **ドリル**: {data.get('drill', '')}
- **時間**: {data.get('duration', 0)}分

"""

    # サマリー追加
    if data.get('summary'):
        markdown += f"""## 📊 練習サマリー

{data['summary']}

"""

    # 文字起こし全文
    if raw_transcript:
        markdown += f"""---

## 📝 文字起こし全文

{raw_transcript}
"""

    return markdown


def build_school_markdown(data: Dict[str, Any], raw_transcript: str = "") -> str:
    """
    スクールメモのMarkdown生成

    Args:
        data: 構造化データ
        raw_transcript: 文字起こし全文

    Returns:
        Markdown文字列
    """
    date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Frontmatter
    frontmatter_data = {
        "date": date_str,
        "scene": "スクール",
        "coach_feedback": bool(data.get('coach_feedback')),
        "tags": data.get('tags', ['tennis', 'school']),
    }
    frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    markdown = f"""---
{frontmatter}---

# スクール練習 - {date_str}

## コーチからの指摘

> [!warning] コーチのアドバイス
> {data.get('coach_feedback', '')}

## 新しく学んだ技術

{data.get('new_technique', '')}

## 練習内容

{data.get('practice_content', '')}

## 自分の気づき

> [!note] リアルタイムメモ
> {data.get('realization', '')}

## 次回までの課題

{data.get('homework', '')}

## 次回やること

{data.get('next_action', '')}

"""

    # サマリー追加
    if data.get('summary'):
        markdown += f"""## 📊 練習サマリー

{data['summary']}

"""

    # 文字起こし全文
    if raw_transcript:
        markdown += f"""---

## 📝 文字起こし全文

{raw_transcript}
"""

    return markdown


def build_match_markdown(data: Dict[str, Any], raw_transcript: str = "") -> str:
    """
    試合メモのMarkdown生成

    Args:
        data: 構造化データ
        raw_transcript: 文字起こし全文

    Returns:
        Markdown文字列
    """
    date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Frontmatter
    frontmatter_data = {
        "date": date_str,
        "scene": "試合",
        "opponent": data.get('opponent', '不明'),
        "opponent_level": data.get('opponent_level', '不明'),
        "score": data.get('score', '不明'),
        "result": data.get('result', '不明'),
        "tags": data.get('tags', ['tennis', 'match']),
    }
    frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    markdown = f"""---
{frontmatter}---

# 試合 - {date_str}

## 試合結果

| 項目 | 内容 |
|------|------|
| **対戦相手** | {data.get('opponent', '不明')} |
| **相手レベル** | {data.get('opponent_level', '不明')} |
| **スコア** | {data.get('score', '不明')} |
| **結果** | {data.get('result', '不明')} |

## 良かったプレー

> [!success] うまくいったこと
> {data.get('good_plays', '')}

## 課題となったプレー

> [!warning] 改善が必要
> {data.get('bad_plays', '')}

## メンタル面

> [!note] 心理状態
> {data.get('mental', '')}

## 戦術・戦略

{data.get('strategy', '')}

## 次回への課題

{data.get('next_action', '')}

"""

    # サマリー追加
    if data.get('summary'):
        markdown += f"""## 📊 試合サマリー

{data['summary']}

"""

    # 文字起こし全文
    if raw_transcript:
        markdown += f"""---

## 📝 文字起こし全文

{raw_transcript}
"""

    return markdown


def build_generic_markdown(data: Dict[str, Any], scene_name: str = "その他", raw_transcript: str = "") -> str:
    """
    汎用メモのMarkdown生成

    Args:
        data: 構造化データ
        scene_name: シーン表示名
        raw_transcript: 文字起こし全文

    Returns:
        Markdown文字列
    """
    date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    # Frontmatter
    frontmatter_data = {
        "date": date_str,
        "scene": scene_name,
        "tags": data.get('tags', ['tennis']),
    }
    frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    markdown = f"""---
{frontmatter}---

# {scene_name} - {date_str}

## 練習内容

{data.get('practice_content', '')}

## 気づき

> [!note] リアルタイムメモ
> {data.get('realization', '')}

## 課題

{data.get('issue', '')}

## 次回やること

{data.get('next_action', '')}

"""

    # サマリー追加
    if data.get('summary'):
        markdown += f"""## 📊 練習サマリー

{data['summary']}

"""

    # 文字起こし全文
    if raw_transcript:
        markdown += f"""---

## 📝 文字起こし全文

{raw_transcript}
"""

    return markdown


# テンプレート選択関数
TEMPLATE_FUNCTIONS = {
    "wall_practice": build_wall_practice_markdown,
    "school": build_school_markdown,
    "match": build_match_markdown,
    "free_practice": build_generic_markdown,
}


def build_markdown_for_scene(
    scene_type: str,
    scene_name: str,
    data: Dict[str, Any],
    raw_transcript: str = ""
) -> str:
    """
    シーンタイプに応じたMarkdownを生成

    Args:
        scene_type: シーンタイプ（"wall_practice", "school", etc.）
        scene_name: シーン表示名（"壁打ち", "スクール", etc.）
        data: 構造化データ
        raw_transcript: 文字起こし全文

    Returns:
        Markdown文字列
    """
    template_func = TEMPLATE_FUNCTIONS.get(scene_type)

    if template_func is None:
        # デフォルトは汎用テンプレート
        return build_generic_markdown(data, scene_name, raw_transcript)

    if scene_type == "free_practice":
        return template_func(data, scene_name, raw_transcript)

    return template_func(data, raw_transcript)
