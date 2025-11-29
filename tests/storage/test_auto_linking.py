"""
Tests for auto-linking functionality.
"""
import pytest
from datetime import datetime
from src.storage.auto_linking import (
    format_link,
    remove_duplicate_links,
    extract_links_from_markdown,
)


def test_format_link():
    """リンクフォーマットが正しく動作することを確認"""
    memo = {
        'file_name': '2025-11-29-壁打ち.md',
        'date': '2025-11-29',
        'scene': '壁打ち'
    }

    # ラベルなし
    link = format_link(memo)
    assert '[[2025-11-29-壁打ち|2025-11-29 壁打ち]]' in link

    # ラベルあり
    link = format_link(memo, "前回")
    assert '[[2025-11-29-壁打ち|2025-11-29 前回]]' in link


def test_format_link_without_md_extension():
    """ファイル名に.mdがない場合"""
    memo = {
        'file_name': '2025-11-29-壁打ち',
        'date': '2025-11-29',
        'scene': '壁打ち'
    }

    link = format_link(memo)
    assert '[[2025-11-29-壁打ち|2025-11-29 壁打ち]]' in link


def test_remove_duplicate_links():
    """重複リンクの削除"""
    links = [
        "- [[2025-11-29-壁打ち|2025-11-29 壁打ち]]",
        "- [[2025-11-28-スクール|2025-11-28 スクール]]",
        "- [[2025-11-29-壁打ち|2025-11-29 前回]]",  # 重複（ファイル名が同じ）
        "- [[2025-11-27-試合|2025-11-27 試合]]",
    ]

    unique = remove_duplicate_links(links)

    # 重複が削除されている
    assert len(unique) == 3
    assert unique[0] == "- [[2025-11-29-壁打ち|2025-11-29 壁打ち]]"
    assert unique[1] == "- [[2025-11-28-スクール|2025-11-28 スクール]]"
    assert unique[2] == "- [[2025-11-27-試合|2025-11-27 試合]]"


def test_extract_links_from_markdown():
    """Markdownからリンクを抽出"""
    content = """
# テスト

これは[[2025-11-29-壁打ち|壁打ち]]の記録です。
前回は[[2025-11-28-スクール]]でした。

## 関連メモ
- [[2025-11-27-試合|試合]]
"""

    links = extract_links_from_markdown(content)

    assert len(links) == 3
    assert "2025-11-29-壁打ち|壁打ち" in links
    assert "2025-11-28-スクール" in links
    assert "2025-11-27-試合|試合" in links


def test_extract_links_from_markdown_empty():
    """リンクがないMarkdown"""
    content = """
# テスト

これはリンクがないテキストです。
"""

    links = extract_links_from_markdown(content)
    assert len(links) == 0
