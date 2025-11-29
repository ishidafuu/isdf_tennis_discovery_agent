"""
Auto-linking functionality for Obsidian memos.

メモ間の自動リンク生成機能。タグベース、日付ベースのリンクを生成し、
Obsidianのグラフビューでナレッジの構造を可視化する。
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import re


async def generate_auto_links(
    memo: Dict[str, Any],
    obsidian_manager,
    max_links: int = 10
) -> str:
    """
    関連メモへのリンクを自動生成する。

    Args:
        memo: メモデータ
        obsidian_manager: ObsidianManagerインスタンス
        max_links: 最大リンク数

    Returns:
        Markdownフォーマットのリンク文字列
    """
    links = []

    # 1. 日付ベースの前後リンク（最優先）
    scene = memo.get('scene', '')
    date_str = memo.get('date', '')

    if date_str and scene:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')

            # 前回のメモ
            prev_memo = await get_previous_memo(obsidian_manager, date, scene)
            if prev_memo:
                links.insert(0, format_link(prev_memo, "← 前回"))

            # 次回のメモ
            next_memo = await get_next_memo(obsidian_manager, date, scene)
            if next_memo:
                links.append(format_link(next_memo, "次回 →"))
        except ValueError:
            pass

    # 2. タグベースのリンク
    tags = memo.get('tags', [])
    if tags:
        tag_links = await generate_tag_based_links(
            memo,
            obsidian_manager,
            tags,
            max_links=5
        )
        links.extend(tag_links)

    # 3. 重複を削除（file_pathベース）
    unique_links = remove_duplicate_links(links)

    # 4. 最大リンク数に制限
    return "\n".join(unique_links[:max_links])


async def get_previous_memo(
    obsidian_manager,
    current_date: datetime,
    scene: str
) -> Optional[Dict[str, Any]]:
    """
    指定された日付とシーンより前の最新メモを取得する。

    Args:
        obsidian_manager: ObsidianManagerインスタンス
        current_date: 現在のメモの日付
        scene: シーン名

    Returns:
        前回のメモ、またはNone
    """
    # 過去90日間のメモを検索
    start_date = current_date - timedelta(days=90)
    memos = obsidian_manager.get_memos_in_range(
        start_date=start_date,
        end_date=current_date - timedelta(days=1),
        scene_name=scene
    )

    # 日付順でソート（新しい順）
    if memos:
        return memos[0]

    return None


async def get_next_memo(
    obsidian_manager,
    current_date: datetime,
    scene: str
) -> Optional[Dict[str, Any]]:
    """
    指定された日付とシーンより後の最も古いメモを取得する。

    Args:
        obsidian_manager: ObsidianManagerインスタンス
        current_date: 現在のメモの日付
        scene: シーン名

    Returns:
        次回のメモ、またはNone
    """
    # 未来90日間のメモを検索
    end_date = current_date + timedelta(days=90)
    memos = obsidian_manager.get_memos_in_range(
        start_date=current_date + timedelta(days=1),
        end_date=end_date,
        scene_name=scene
    )

    # 日付順でソート（古い順）
    if memos:
        return sorted(memos, key=lambda x: x.get('date', ''), reverse=False)[0]

    return None


async def generate_tag_based_links(
    current_memo: Dict[str, Any],
    obsidian_manager,
    tags: List[str],
    max_links: int = 5
) -> List[str]:
    """
    タグベースのリンクを生成する。

    Args:
        current_memo: 現在のメモ
        obsidian_manager: ObsidianManagerインスタンス
        tags: タグリスト
        max_links: 最大リンク数

    Returns:
        リンクのリスト
    """
    links = []
    current_file_path = current_memo.get('file_path')

    for tag in tags:
        # タグで検索（最大3件）
        related = obsidian_manager.get_memo_by_tags([tag], match_all=False)

        for memo in related[:3]:
            # 自分自身は除外
            if memo.get('file_path') == current_file_path:
                continue

            # リンクを生成（タグ名を含める）
            link_text = f"#{tag}"
            links.append(format_link(memo, link_text))

            if len(links) >= max_links:
                break

        if len(links) >= max_links:
            break

    return links


def format_link(memo: Dict[str, Any], label: Optional[str] = None) -> str:
    """
    メモへのリンクをObsidian形式でフォーマットする。

    Args:
        memo: メモデータ
        label: リンクのラベル（オプション）

    Returns:
        Obsidian形式のリンク文字列
    """
    # ファイル名から.mdを除去
    file_name = memo.get('file_name', '')
    if file_name.endswith('.md'):
        file_name = file_name[:-3]

    date = memo.get('date', '')
    scene = memo.get('scene', '')

    # ラベルが指定されていない場合はシーン名を使用
    if not label:
        label = scene

    # Obsidian形式: [[ファイル名|表示名]]
    return f"- [[{file_name}|{date} {label}]]"


def remove_duplicate_links(links: List[str]) -> List[str]:
    """
    リンクリストから重複を削除する（file_pathベース）。

    Args:
        links: リンクのリスト

    Returns:
        重複を削除したリンクリスト
    """
    seen = set()
    unique = []

    for link in links:
        # [[ファイル名|...]] の形式からファイル名を抽出
        match = re.search(r'\[\[([^\|]+)', link)
        if match:
            file_name = match.group(1)
            if file_name not in seen:
                seen.add(file_name)
                unique.append(link)

    return unique


async def update_backlinks(
    new_memo: Dict[str, Any],
    obsidian_manager,
    max_backlinks: int = 5
):
    """
    既存メモにバックリンクを追加する。

    新しいメモに関連するメモを検索し、それらのメモに
    新しいメモへのリンクを追加する。

    Args:
        new_memo: 新しく作成されたメモ
        obsidian_manager: ObsidianManagerインスタンス
        max_backlinks: 最大バックリンク数
    """
    # 新しいメモのタグを取得
    tags = new_memo.get('tags', [])
    if not tags:
        return

    # タグで関連メモを検索
    related_memos = obsidian_manager.get_memo_by_tags(tags, match_all=False)

    # 現在のメモは除外
    current_file_path = new_memo.get('file_path')
    related_memos = [m for m in related_memos if m.get('file_path') != current_file_path]

    # 最大バックリンク数に制限
    related_memos = related_memos[:max_backlinks]

    # 各関連メモにバックリンクを追加
    for related in related_memos:
        try:
            await add_backlink_to_memo(
                target_file=related['file_path'],
                new_memo=new_memo,
                obsidian_manager=obsidian_manager
            )
        except Exception as e:
            print(f"Error adding backlink to {related['file_path']}: {e}")


async def add_backlink_to_memo(
    target_file: str,
    new_memo: Dict[str, Any],
    obsidian_manager
):
    """
    指定されたメモにバックリンクを追加する。

    Args:
        target_file: リンクを追加する対象ファイル
        new_memo: リンク元の新しいメモ
        obsidian_manager: ObsidianManagerインスタンス
    """
    # バックリンクセクションの見出し
    backlink_section_header = "## 関連メモ"

    # ファイルを読み込み
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {target_file}: {e}")
        return

    # 新しいメモへのリンクを作成
    new_link = format_link(new_memo)

    # 既に「関連メモ」セクションが存在するか確認
    if backlink_section_header in content:
        # セクションが存在する場合、そこにリンクを追加
        # 重複チェック
        if new_link in content:
            return  # 既にリンクが存在する場合はスキップ

        # セクションの末尾にリンクを追加
        content = content.replace(
            backlink_section_header,
            f"{backlink_section_header}\n{new_link}"
        )
    else:
        # セクションが存在しない場合、末尾に追加
        content += f"\n\n{backlink_section_header}\n{new_link}\n"

    # ファイルに書き込み
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing file {target_file}: {e}")


def extract_links_from_markdown(content: str) -> List[str]:
    """
    Markdown内のObsidianリンクを抽出する。

    Args:
        content: Markdown content

    Returns:
        リンクのリスト（[[...]]形式）
    """
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, content)
    return matches
