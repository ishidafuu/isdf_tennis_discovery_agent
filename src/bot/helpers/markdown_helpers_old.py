"""
Markdown building and GitHub push helpers for media memos.
"""
import yaml


def build_image_markdown(memo_data: dict, scene_name: str) -> str:
    """
    Build markdown content for image memo.

    Args:
        memo_data: Memo data dictionary
        scene_name: Scene display name

    Returns:
        Markdown content as string
    """
    # Frontmatter
    frontmatter_data = {
        "date": memo_data['date'],
        "scene": scene_name,
        "input_type": "image",
        "tags": memo_data.get('tags', ['tennis', 'image']),
    }
    frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    markdown = f"""---
{frontmatter}---

# 画像メモ - {scene_name} - {memo_data['date']}

## 📸 画像

![[{memo_data['file_path']}]]

"""

    # User comment
    if memo_data.get('user_comment'):
        markdown += f"""## 💭 メモ

{memo_data['user_comment']}

"""

    return markdown


def build_video_markdown(memo_data: dict, scene_name: str) -> str:
    """
    Build markdown content for video memo.

    Args:
        memo_data: Memo data dictionary
        scene_name: Scene display name

    Returns:
        Markdown content as string
    """
    # Frontmatter
    frontmatter_data = {
        "date": memo_data['date'],
        "scene": scene_name,
        "input_type": "video",
        "tags": memo_data.get('tags', ['tennis', 'video']),
    }
    frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    markdown = f"""---
{frontmatter}---

# 動画メモ - {scene_name} - {memo_data['date']}

## 🎥 動画

![[{memo_data['file_path']}]]

"""

    # User comment
    if memo_data.get('user_comment'):
        markdown += f"""## 💭 メモ

{memo_data['user_comment']}

"""

    return markdown


def push_image_memo_to_github(
    github_sync,
    session,
    markdown_content: str,
    scene_name: str
) -> str:
    """
    Push image memo to GitHub repository.

    Args:
        github_sync: GitHubSync instance
        session: PracticeSession object
        markdown_content: Markdown content to push
        scene_name: Scene name for the filename

    Returns:
        URL of the created/updated file
    """
    from src.storage.markdown_builder import MarkdownBuilder

    builder = MarkdownBuilder()
    year = session.date.strftime("%Y")
    month = session.date.strftime("%m")
    filename = builder.get_filename_for_session(session, f"{scene_name}-画像")
    file_path = f"{github_sync.base_path}/{year}/{month}/{filename}"

    date_str = session.date.strftime("%Y-%m-%d")
    commit_message = f"Add image memo: {date_str} ({scene_name})"

    file_url = github_sync._push_file(
        file_path=file_path,
        content=markdown_content,
        commit_message=commit_message
    )

    return file_url


def push_video_memo_to_github(
    github_sync,
    session,
    markdown_content: str,
    scene_name: str
) -> str:
    """
    Push video memo to GitHub repository.

    Args:
        github_sync: GitHubSync instance
        session: PracticeSession object
        markdown_content: Markdown content to push
        scene_name: Scene name for the filename

    Returns:
        URL of the created/updated file
    """
    from src.storage.markdown_builder import MarkdownBuilder

    builder = MarkdownBuilder()
    year = session.date.strftime("%Y")
    month = session.date.strftime("%m")
    filename = builder.get_filename_for_session(session, f"{scene_name}-動画")
    file_path = f"{github_sync.base_path}/{year}/{month}/{filename}"

    date_str = session.date.strftime("%Y-%m-%d")
    commit_message = f"Add video memo: {date_str} ({scene_name})"

    file_url = github_sync._push_file(
        file_path=file_path,
        content=markdown_content,
        commit_message=commit_message
    )

    return file_url
