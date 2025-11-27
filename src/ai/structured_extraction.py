"""
Structured data extraction from transcripts based on scene type.
"""
import json
from typing import Dict, Any
import google.generativeai as genai

from src.ai.prompts import get_prompt_for_scene


async def extract_structured_data(
    text: str,
    scene_type: str,
    model: genai.GenerativeModel
) -> Dict[str, Any]:
    """
    シーン別に構造化データを抽出

    Args:
        text: 文字起こしテキスト
        scene_type: シーンタイプ（"wall_practice", "school", etc.）
        model: Gemini生成モデル

    Returns:
        構造化データの辞書

    Raises:
        ValueError: JSON抽出に失敗した場合
    """
    # シーン別プロンプトを取得
    prompt = get_prompt_for_scene(scene_type, text)

    # Gemini APIで構造化
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )

    # JSONをパース
    try:
        structured_data = json.loads(response.text)

        # デフォルト値の設定
        if structured_data.get("tags") is None:
            structured_data["tags"] = []
        if structured_data.get("summary") is None:
            structured_data["summary"] = ""

        return structured_data

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response.text}")


def ensure_required_fields(data: Dict[str, Any], scene_type: str) -> Dict[str, Any]:
    """
    必須フィールドが存在することを保証

    Args:
        data: 構造化データ
        scene_type: シーンタイプ

    Returns:
        必須フィールドを含む構造化データ
    """
    # 共通フィールド
    if "tags" not in data or data["tags"] is None:
        data["tags"] = []
    if "summary" not in data or data["summary"] is None:
        data["summary"] = ""
    if "next_action" not in data or data["next_action"] is None:
        data["next_action"] = ""

    # シーン別の必須フィールド
    if scene_type == "wall_practice":
        defaults = {
            "drill": "",
            "duration": 0,
            "focus": "",
            "body_sensation": "",
            "improvement": "",
            "issue": "",
        }
    elif scene_type == "school":
        defaults = {
            "coach_feedback": "",
            "new_technique": "",
            "practice_content": "",
            "realization": "",
            "homework": "",
        }
    elif scene_type == "match":
        defaults = {
            "opponent": "",
            "opponent_level": "",
            "score": "",
            "result": "不明",
            "good_plays": "",
            "bad_plays": "",
            "mental": "",
            "strategy": "",
        }
    else:  # free_practice or others
        defaults = {
            "practice_content": "",
            "realization": "",
            "issue": "",
        }

    # デフォルト値を設定
    for key, default_value in defaults.items():
        if key not in data or data[key] is None:
            data[key] = default_value

    return data
