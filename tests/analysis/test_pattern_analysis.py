"""
Tests for the pattern analysis module.
"""
import pytest
import asyncio
from src.analysis.pattern_analysis import PatternAnalyzer, get_pattern_analyzer


@pytest.fixture
def sample_memos():
    """Sample memos for testing."""
    return [
        {
            "date": "2025-01-01",
            "scene": "壁打ち",
            "summary": "サーブがうまくいった",
            "tags": ["serve"],
            "condition": "good",
            "success_patterns": [{"description": "トスが安定していた"}],
            "failure_patterns": [],
            "raw_text": "今日はサーブの練習がうまくいった。トスが安定していて良かった。"
        },
        {
            "date": "2025-01-05",
            "scene": "スクール",
            "summary": "フォアハンドに課題",
            "tags": ["forehand"],
            "condition": "bad",
            "success_patterns": [],
            "failure_patterns": [{"symptom": "ボールが浮いてしまう"}],
            "raw_text": "フォアハンドがうまくいかない。ボールが浮いてしまう。"
        },
        {
            "date": "2025-01-10",
            "scene": "壁打ち",
            "summary": "サーブの改善",
            "tags": ["serve"],
            "condition": "good",
            "success_patterns": [{"description": "2ndサーブが安定した"}],
            "failure_patterns": [],
            "raw_text": "2ndサーブの改善ができた。"
        }
    ]


@pytest.mark.asyncio
async def test_extract_condition_patterns(sample_memos):
    """Test pattern extraction from good/bad condition memos."""
    analyzer = get_pattern_analyzer()

    result = await analyzer.extract_condition_patterns(sample_memos)

    assert "good_patterns" in result
    assert "bad_patterns" in result
    assert "key_differences" in result
    assert "recommendations" in result


@pytest.mark.asyncio
async def test_analyze_time_series(sample_memos):
    """Test time series analysis."""
    analyzer = get_pattern_analyzer()

    result = await analyzer.analyze_time_series(sample_memos)

    assert "practice_frequency" in result
    assert "improving_skills" in result
    assert "ongoing_issues" in result


@pytest.mark.asyncio
async def test_find_turning_points(sample_memos):
    """Test turning point detection."""
    analyzer = get_pattern_analyzer()

    result = await analyzer.find_turning_points(sample_memos)

    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_analyze_correlations(sample_memos):
    """Test correlation analysis."""
    analyzer = get_pattern_analyzer()

    # Add condition and tags for correlation
    for memo in sample_memos:
        memo["practice_frequency"] = 1

    result = await analyzer.analyze_correlations(
        sample_memos,
        "practice_frequency",
        "condition"
    )

    assert "correlation" in result


@pytest.mark.asyncio
async def test_empty_memos_error():
    """Test that empty memos list raises an error."""
    analyzer = get_pattern_analyzer()

    with pytest.raises(ValueError, match="Memos list cannot be empty"):
        await analyzer.extract_condition_patterns([])


def test_is_good_condition(sample_memos):
    """Test good condition detection."""
    analyzer = get_pattern_analyzer()

    good_memo = sample_memos[0]
    assert analyzer._is_good_condition(good_memo) is True

    bad_memo = sample_memos[1]
    assert analyzer._is_good_condition(bad_memo) is False


def test_is_bad_condition(sample_memos):
    """Test bad condition detection."""
    analyzer = get_pattern_analyzer()

    bad_memo = sample_memos[1]
    assert analyzer._is_bad_condition(bad_memo) is True

    good_memo = sample_memos[0]
    assert analyzer._is_bad_condition(good_memo) is False
