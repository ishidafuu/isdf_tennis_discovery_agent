"""
Markdown building and GitHub push helpers for media memos (REFACTORED).

Unified media handling to reduce code duplication.
"""
from typing import Literal
import yaml


def build_media_markdown(
    memo_data: dict,
    scene_name: str,
    media_type: Literal["image", "video"]
) -> str:
    """
    Build markdown content for media memo (unified for image/video).

    Args:
        memo_data: Memo data dictionary
        scene_name: Scene display name
        media_type: Type of media ("image" or "video")

    Returns:
        Markdown content as string
    """
    # Media type specific settings
    media_config = {
        "image": {"emoji": "📸", "label": "画像"},
        "video": {"emoji": "🎥", "label": "動画"},
    }
    config = media_config[media_type]

    # Frontmatter
    frontmatter_data = {
        "date": memo_data['date'],
        "scene": scene_name,
        "input_type": media_type,
        "tags": memo_data.get('tags', ['tennis', media_type]),
    }
    frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    markdown = f"""---
{frontmatter}---

# {config['label']}メモ - {scene_name} - {memo_data['date']}

## {config['emoji']} {config['label']}

![[{memo_data['file_path']}]]

"""

    # User comment
    if memo_data.get('user_comment'):
        markdown += f"""## 💭 メモ

{memo_data['user_comment']}

"""

    return markdown


def build_image_markdown(memo_data: dict, scene_name: str) -> str:
    """
    Build markdown content for image memo.

    DEPRECATED: Use build_media_markdown(..., media_type="image") instead.
    Kept for backward compatibility.

    Args:
        memo_data: Memo data dictionary
        scene_name: Scene display name

    Returns:
        Markdown content as string
    """
    return build_media_markdown(memo_data, scene_name, "image")


def build_video_markdown(memo_data: dict, scene_name: str) -> str:
    """
    Build markdown content for video memo.

    DEPRECATED: Use build_media_markdown(..., media_type="video") instead.
    Kept for backward compatibility.

    Args:
        memo_data: Memo data dictionary
        scene_name: Scene display name

    Returns:
        Markdown content as string
    """
    return build_media_markdown(memo_data, scene_name, "video")


def push_media_memo_to_github(
    github_sync,
    session,
    markdown_content: str,
    scene_name: str,
    media_type: Literal["image", "video"]
) -> str:
    """
    Push media memo to GitHub repository (unified for image/video).

    Args:
        github_sync: GitHubSync instance
        session: PracticeSession object
        markdown_content: Markdown content to push
        scene_name: Scene name for the filename
        media_type: Type of media ("image" or "video")

    Returns:
        URL of the created/updated file
    """
    from src.storage.markdown_builder import MarkdownBuilder

    # Media type specific labels
    media_label = {"image": "画像", "video": "動画"}
    suffix = media_label[media_type]

    builder = MarkdownBuilder()
    year = session.date.strftime("%Y")
    month = session.date.strftime("%m")
    filename = builder.get_filename_for_session(session, f"{scene_name}-{suffix}")
    file_path = f"{github_sync.base_path}/{year}/{month}/{filename}"

    date_str = session.date.strftime("%Y-%m-%d")
    commit_message = f"Add {media_type} memo: {date_str} ({scene_name})"

    file_url = github_sync._push_file(
        file_path=file_path,
        content=markdown_content,
        commit_message=commit_message
    )

    return file_url


def push_image_memo_to_github(
    github_sync,
    session,
    markdown_content: str,
    scene_name: str
) -> str:
    """
    Push image memo to GitHub repository.

    DEPRECATED: Use push_media_memo_to_github(..., media_type="image") instead.
    Kept for backward compatibility.

    Args:
        github_sync: GitHubSync instance
        session: PracticeSession object
        markdown_content: Markdown content to push
        scene_name: Scene name for the filename

    Returns:
        URL of the created/updated file
    """
    return push_media_memo_to_github(
        github_sync, session, markdown_content, scene_name, "image"
    )


def push_video_memo_to_github(
    github_sync,
    session,
    markdown_content: str,
    scene_name: str
) -> str:
    """
    Push video memo to GitHub repository.

    DEPRECATED: Use push_media_memo_to_github(..., media_type="video") instead.
    Kept for backward compatibility.

    Args:
        github_sync: GitHubSync instance
        session: PracticeSession object
        markdown_content: Markdown content to push
        scene_name: Scene name for the filename

    Returns:
        URL of the created/updated file
    """
    return push_media_memo_to_github(
        github_sync, session, markdown_content, scene_name, "video"
    )
