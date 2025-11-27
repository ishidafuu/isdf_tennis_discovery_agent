"""
Channel handler for detecting scenes from Discord channel names.
"""
from typing import Optional


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

    # チャンネル名のマッピング
    channel_mapping = {
        "壁打ち": ("wall_practice", "壁打ち"),
        "wall": ("wall_practice", "壁打ち"),
        "wall-practice": ("wall_practice", "壁打ち"),
        "スクール": ("school", "スクール"),
        "school": ("school", "スクール"),
        "lesson": ("school", "スクール"),
        "試合": ("match", "試合"),
        "match": ("match", "試合"),
        "game": ("match", "試合"),
        "フリー練習": ("free_practice", "フリー練習"),
        "free": ("free_practice", "フリー練習"),
        "free-practice": ("free_practice", "フリー練習"),
        "振り返り": ("reflection", "振り返り"),
        "reflection": ("reflection", "振り返り"),
        "review": ("reflection", "振り返り"),
    }

    # 完全一致を試す
    for key, value in channel_mapping.items():
        if key in channel_name or key in channel_lower:
            return value

    # デフォルト: フリー練習として扱う
    return ("free_practice", "その他")


def is_reflection_channel(channel_name: str) -> bool:
    """
    振り返りチャンネルかどうかを判定

    Args:
        channel_name: Discordチャンネル名

    Returns:
        振り返りチャンネルならTrue
    """
    scene_type, _ = detect_scene_from_channel(channel_name)
    return scene_type == "reflection"


def get_scene_emoji(scene_type: str) -> str:
    """
    シーンタイプに対応する絵文字を取得

    Args:
        scene_type: シーンタイプ

    Returns:
        絵文字文字列
    """
    emoji_mapping = {
        "wall_practice": "🧱",
        "school": "🎓",
        "match": "🏆",
        "free_practice": "🎾",
        "reflection": "📝",
    }
    return emoji_mapping.get(scene_type, "🎾")


def get_scene_description(scene_type: str) -> str:
    """
    シーンタイプの説明を取得

    Args:
        scene_type: シーンタイプ

    Returns:
        説明文字列
    """
    description_mapping = {
        "wall_practice": "基礎練習・反復ドリル",
        "school": "コーチの指導あり",
        "match": "実戦・練習試合",
        "free_practice": "友人との自由練習",
        "reflection": "後日の追記・補足",
    }
    return description_mapping.get(scene_type, "練習記録")
