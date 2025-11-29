"""
Media utility functions for Discord attachments.
"""
import re


def is_audio_file(filename: str) -> bool:
    """
    Check if file is an audio file.

    Args:
        filename: File name

    Returns:
        True if it's an audio file
    """
    audio_extensions = [".ogg", ".mp3", ".wav", ".m4a", ".opus", ".webm"]
    return any(filename.lower().endswith(ext) for ext in audio_extensions)


def is_image_file(filename: str) -> bool:
    """
    Check if file is an image file.

    Args:
        filename: File name

    Returns:
        True if it's an image file
    """
    image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def is_video_file(filename: str) -> bool:
    """
    Check if file is a video file.

    Args:
        filename: File name

    Returns:
        True if it's a video file
    """
    video_extensions = [".mp4", ".mov", ".avi", ".webm"]
    return any(filename.lower().endswith(ext) for ext in video_extensions)


def extract_urls(text: str) -> list[str]:
    """
    Extract URLs from text.

    Args:
        text: Text content

    Returns:
        List of URLs found in the text
    """
    url_pattern = r'https?://[^\s<>"\']+'
    return re.findall(url_pattern, text)


def extract_scene_from_dm_text(text: str) -> tuple[str, str]:
    """
    Extract scene information from DM text.

    Args:
        text: DM message content

    Returns:
        Tuple of (scene_type, scene_display_name)
    """
    if not text:
        return ("free_practice", "その他")

    text_lower = text.lower()

    # Scene keywords
    if "壁打ち" in text or "wall" in text_lower:
        return ("wall_practice", "壁打ち")
    elif "スクール" in text or "school" in text_lower or "lesson" in text_lower:
        return ("school", "スクール")
    elif "試合" in text or "match" in text_lower or "game" in text_lower:
        return ("match", "試合")
    elif "フリー練習" in text or "free" in text_lower:
        return ("free_practice", "フリー練習")

    # Default to free practice
    return ("free_practice", "その他")
