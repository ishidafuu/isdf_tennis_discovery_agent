"""Prompts for Gemini AI

このモジュールは、各シーンに応じたプロンプトを生成する機能を提供します。
テンプレート化により、保守性と拡張性を向上させています。
"""

from string import Template
import json
from typing import Dict, Any


# 共通プロンプトテンプレート
PROMPT_TEMPLATE = Template("""以下の音声メモから、${scene_name}の情報を抽出してください。

音声メモ:
${text}

抽出する情報（JSON形式）:
${schema}

**重要な注意事項:**
- すべてのフィールドは必須です。値がない場合は空文字列""または適切なデフォルト値を使用
- tags は配列形式で、空の場合は []
- ユーザーが明示的に言及していない項目は空文字列""にする
- 推測や一般論は避け、ユーザーの実際の体験のみを抽出する
- JSON以外のテキストは出力しない
""")


# シーン別の設定
SCENE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "wall_practice": {
        "name": "壁打ち練習",
        "schema": {
            "tags": ["技術カテゴリ（例: forehand, backhand, serve等）"],
            "drill": "実施したドリル（例: フォアハンドストローク）",
            "duration": "時間（分、推定でOK）",
            "focus": "今日の焦点（何を意識したか）",
            "body_sensation": "身体感覚の気づき",
            "improvement": "改善した点",
            "issue": "課題として残った点",
            "next_action": "次回やること",
            "summary": "練習の簡潔な要約（2-3文）"
        },
        "notes": [
            "duration は数値（分単位）、不明な場合は 0"
        ]
    },
    "school": {
        "name": "スクール練習",
        "schema": {
            "tags": ["技術カテゴリ（例: forehand, backhand, serve等）"],
            "coach_feedback": "コーチからの指摘・アドバイス",
            "new_technique": "新しく学んだ技術",
            "practice_content": "練習内容",
            "realization": "自分の気づき",
            "homework": "次回までの課題",
            "next_action": "次回やること",
            "summary": "練習の簡潔な要約（2-3文）"
        }
    },
    "match": {
        "name": "試合",
        "schema": {
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
        },
        "notes": [
            "result は \"勝ち\"、\"負け\"、\"不明\" のいずれか"
        ]
    },
    "free_practice": {
        "name": "練習",
        "schema": {
            "tags": ["技術カテゴリ"],
            "practice_content": "練習内容",
            "realization": "気づき",
            "issue": "課題",
            "next_action": "次回やること",
            "summary": "練習の簡潔な要約（2-3文）"
        }
    }
}


def get_prompt_for_scene(scene_type: str, text: str) -> str:
    """シーンタイプに応じたプロンプトを生成

    Args:
        scene_type: シーンタイプ（wall_practice, school, match, free_practice）
        text: 音声メモのテキスト

    Returns:
        生成されたプロンプト文字列
    """
    # デフォルトはfree_practice
    config = SCENE_CONFIGS.get(scene_type, SCENE_CONFIGS["free_practice"])

    # 追加注意事項があれば結合
    additional_notes = ""
    if "notes" in config:
        additional_notes = "\n" + "\n".join(f"- {note}" for note in config["notes"])

    prompt = PROMPT_TEMPLATE.substitute(
        scene_name=config["name"],
        text=text,
        schema=json.dumps(config["schema"], ensure_ascii=False, indent=2)
    )

    # 追加注意事項を挿入
    if additional_notes:
        prompt = prompt.replace(
            "**重要な注意事項:**",
            f"**重要な注意事項:**{additional_notes}"
        )

    return prompt


# 後方互換性のための既存関数（内部実装は新システムを使用）
def get_wall_practice_prompt(text: str) -> str:
    """壁打ち練習用のプロンプトを生成

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return get_prompt_for_scene("wall_practice", text)


def get_school_prompt(text: str) -> str:
    """スクール練習用のプロンプトを生成

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return get_prompt_for_scene("school", text)


def get_match_prompt(text: str) -> str:
    """試合用のプロンプトを生成

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return get_prompt_for_scene("match", text)


def get_generic_prompt(text: str) -> str:
    """汎用プロンプトを生成（フリー練習等）

    Args:
        text: 文字起こしテキスト

    Returns:
        プロンプト文字列
    """
    return get_prompt_for_scene("free_practice", text)


# シーンのマッピング定義（後方互換性のため保持）
SCENE_NAMES = {
    "壁打ち": "wall_practice",
    "スクール": "school",
    "試合": "match",
    "フリー練習": "free_practice",
    "振り返り": "reflection"
}


# プロンプト選択関数（後方互換性のため保持）
PROMPT_FUNCTIONS = {
    "wall_practice": get_wall_practice_prompt,
    "school": get_school_prompt,
    "match": get_match_prompt,
    "free_practice": get_generic_prompt,
}
