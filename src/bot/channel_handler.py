"""
Channel handler for detecting scenes from Discord channel names (REFACTORED).

Uses centralized constants and returns type-safe SceneInfo objects.
"""
from typing import Optional

from src.constants import (
    SceneType,
    CHANNEL_TO_SCENE,
    SCENE_EMOJIS,
    SCENE_DISPLAY_NAMES,
    SCENE_DESCRIPTIONS,
    DEFAULT_SCENE_NAME,
)
from src.models.scene_data import SceneInfo


def detect_scene_from_channel(channel_name: str) -> tuple[str, str]:
    """
    チャンネル名からシーンを判定

    Args:
        channel_name: Discordチャンネル名

    Returns:
        (scene_type, scene_display_name) のタプル
        scene_type: 内部で使用するシーンタイプ（"wall_practice", "school", etc.）
        scene_display_name: 表示用シーン名（"壁打ち", "スクール", etc.）
    """
    # チャンネル名を小文字に変換して判定
    channel_lower = channel_name.lower()

    # チャンネル名のマッピング（constants から取得）
    for key, value in CHANNEL_TO_SCENE.items():
        if key in channel_name or key in channel_lower:
            return value

    # デフォルト: フリー練習として扱う
    return (SceneType.FREE_PRACTICE, DEFAULT_SCENE_NAME)


def get_scene_info(channel_name: str) -> SceneInfo:
    """
    チャンネル名からSceneInfoオブジェクトを取得

    Args:
        channel_name: Discordチャンネル名

    Returns:
        SceneInfo object with type, name, emoji, and description
    """
    scene_type, scene_name = detect_scene_from_channel(channel_name)

    return SceneInfo(
        type=scene_type,
        name=scene_name,
        emoji=SCENE_EMOJIS.get(scene_type, "🎾"),
        description=SCENE_DESCRIPTIONS.get(scene_type, "練習記録"),
    )


def is_reflection_channel(channel_name: str) -> bool:
    """
    振り返りチャンネルかどうかを判定

    Args:
        channel_name: Discordチャンネル名

    Returns:
        振り返りチャンネルならTrue
    """
    scene_type, _ = detect_scene_from_channel(channel_name)
    return scene_type == SceneType.REFLECTION


def is_question_channel(channel_name: str) -> bool:
    """
    質問チャンネルかどうかを判定

    Args:
        channel_name: Discordチャンネル名

    Returns:
        質問チャンネルならTrue
    """
    scene_type, _ = detect_scene_from_channel(channel_name)
    return scene_type == SceneType.QUESTION


def is_analysis_channel(channel_name: str) -> bool:
    """
    分析チャンネルかどうかを判定

    Args:
        channel_name: Discordチャンネル名

    Returns:
        分析チャンネルならTrue
    """
    scene_type, _ = detect_scene_from_channel(channel_name)
    return scene_type == SceneType.ANALYSIS


def get_scene_emoji(scene_type: str) -> str:
    """
    シーンタイプに対応する絵文字を取得

    DEPRECATED: Use SceneInfo.emoji or SCENE_EMOJIS[scene_type] instead.

    Args:
        scene_type: シーンタイプ

    Returns:
        絵文字文字列
    """
    return SCENE_EMOJIS.get(scene_type, "🎾")


def get_scene_description(scene_type: str) -> str:
    """
    シーンタイプの説明を取得

    DEPRECATED: Use SceneInfo.description or SCENE_DESCRIPTIONS[scene_type] instead.

    Args:
        scene_type: シーンタイプ

    Returns:
        説明文字列
    """
    return SCENE_DESCRIPTIONS.get(scene_type, "練習記録")


def is_allowed_channel(channel_name: str) -> bool:
    """
    許可されたチャンネルかどうかを判定

    指定されたチャンネル（壁打ち、スクール、試合、フリー練習、振り返り、質問、分析）
    のみでBotが反応するようにする。

    Args:
        channel_name: Discordチャンネル名

    Returns:
        許可されたチャンネルならTrue、それ以外はFalse
    """
    # チャンネル名を小文字に変換
    channel_lower = channel_name.lower()

    # CHANNEL_TO_SCENEに定義されているチャンネル名のいずれかにマッチするかチェック
    for key in CHANNEL_TO_SCENE.keys():
        if key in channel_name or key in channel_lower:
            return True

    # どのチャンネルにもマッチしない場合はFalse
    return False
