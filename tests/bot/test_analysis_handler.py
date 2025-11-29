"""
Tests for analysis channel handler.
"""
import pytest
from src.bot.analysis_handler import (
    detect_period_from_text,
    extract_section,
    format_analysis_response,
)


def test_detect_period_from_text_week():
    """「今週」の検出"""
    period = detect_period_from_text("今週の成長を分析して")
    assert period["days"] == 7
    assert period["label"] == "今週"


def test_detect_period_from_text_month():
    """「今月」の検出"""
    period = detect_period_from_text("今月の練習を分析してください")
    assert period["days"] == 30
    assert period["label"] == "今月"


def test_detect_period_from_text_three_months():
    """「3ヶ月」の検出"""
    period = detect_period_from_text("3ヶ月でどのくらい成長した？")
    assert period["days"] == 90
    assert period["label"] == "3ヶ月"


def test_detect_period_from_text_default():
    """デフォルト（期間指定なし）"""
    period = detect_period_from_text("分析して")
    assert period["days"] == 30
    assert period["label"] == "今月"


def test_extract_section_found():
    """セクション抽出成功"""
    markdown = """
## 記録

今日の練習

## 改善

フォアハンドが安定した

## 課題

バックハンドの練習
"""
    improvement = extract_section(markdown, "改善")
    assert improvement is not None
    assert "フォアハンド" in improvement

    issue = extract_section(markdown, "課題")
    assert issue is not None
    assert "バックハンド" in issue


def test_extract_section_not_found():
    """セクションが存在しない場合"""
    markdown = """
## 記録

今日の練習
"""
    improvement = extract_section(markdown, "改善")
    assert improvement is None


def test_extract_section_with_colon():
    """コロン形式のセクション抽出"""
    markdown = """
今日の練習

改善: フォアハンドが安定した
課題: バックハンドの練習
"""
    improvement = extract_section(markdown, "改善")
    assert improvement is not None
    assert "フォアハンド" in improvement


def test_format_analysis_response():
    """分析レスポンスのフォーマット"""
    response = format_analysis_response(
        period_label="今月",
        memo_count=15,
        analysis_text="テスト分析結果"
    )

    assert "今月の分析" in response
    assert "15件" in response
    assert "テスト分析結果" in response
