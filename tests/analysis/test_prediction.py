"""
Tests for the prediction module.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from src.analysis.prediction import PracticePredictor, get_practice_predictor


@pytest.fixture
def sample_memos():
    """Sample memos for testing."""
    base_date = datetime.now() - timedelta(days=30)

    memos = []
    for i in range(10):
        date = base_date + timedelta(days=i * 3)
        memos.append({
            "date": date.strftime("%Y-%m-%d"),
            "scene": "壁打ち",
            "summary": f"練習{i+1}",
            "tags": ["serve", "forehand"],
            "condition": "good" if i % 2 == 0 else "normal",
            "success_patterns": [{"description": "良かった"}],
            "issues": [{"description": "課題がある"}],
            "next_actions": [{"theme": "改善する"}],
            "raw_text": f"練習内容{i+1}"
        })

    return memos


@pytest.mark.asyncio
async def test_predict_growth(sample_memos):
    """Test growth prediction."""
    predictor = get_practice_predictor()

    result = await predictor.predict_growth(sample_memos)

    assert "growing_skills" in result
    assert "struggling_skills" in result
    assert "one_month_forecast" in result
    assert "recommended_focus" in result


@pytest.mark.asyncio
async def test_predict_growth_with_target_skill(sample_memos):
    """Test growth prediction for specific skill."""
    predictor = get_practice_predictor()

    result = await predictor.predict_growth(sample_memos, target_skill="サーブ")

    assert result is not None


@pytest.mark.asyncio
async def test_suggest_practice_menu(sample_memos):
    """Test practice menu suggestion."""
    predictor = get_practice_predictor()

    result = await predictor.suggest_practice_menu(
        sample_memos,
        available_time=60,
        scene="壁打ち"
    )

    assert isinstance(result, str)
    assert "練習メニュー" in result or "ウォームアップ" in result


@pytest.mark.asyncio
async def test_predict_condition(sample_memos):
    """Test condition prediction."""
    predictor = get_practice_predictor()

    result = await predictor.predict_condition(sample_memos)

    assert "overall_condition" in result
    assert "fatigue_level" in result
    assert "recommendation" in result
    assert "warning_signs" in result


@pytest.mark.asyncio
async def test_recommend_next_skill(sample_memos):
    """Test next skill recommendation."""
    predictor = get_practice_predictor()

    result = await predictor.recommend_next_skill(sample_memos)

    assert "recommended_skill" in result
    assert "reasoning" in result
    assert "prerequisites" in result
    assert "expected_timeline" in result


@pytest.mark.asyncio
async def test_empty_memos_error():
    """Test that empty memos list raises an error."""
    predictor = get_practice_predictor()

    with pytest.raises(ValueError, match="Memos list cannot be empty"):
        await predictor.predict_growth([])


def test_calculate_practice_intervals(sample_memos):
    """Test practice interval calculation."""
    predictor = get_practice_predictor()

    intervals = predictor._calculate_practice_intervals(sample_memos)

    assert isinstance(intervals, str)
    assert "平均" in intervals or "データ不足" in intervals


def test_count_fatigue_indicators(sample_memos):
    """Test fatigue indicator counting."""
    predictor = get_practice_predictor()

    # Add fatigue-related text
    sample_memos[0]["raw_text"] = "今日は疲れた。腕が痛い。"

    count = predictor._count_fatigue_indicators(sample_memos[:1])

    assert count >= 2  # "疲れ" and "痛い"


def test_get_recent_memos(sample_memos):
    """Test getting recent memos."""
    predictor = get_practice_predictor()

    recent = predictor._get_recent_memos(sample_memos, months=1)

    assert len(recent) > 0
    assert len(recent) <= len(sample_memos)
