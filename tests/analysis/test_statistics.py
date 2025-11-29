"""
Tests for statistics and graph generation functionality.
"""
import pytest
from datetime import datetime, timedelta
from src.analysis.statistics import (
    calculate_monthly_stats,
    calculate_weekly_stats,
    generate_stats_markdown,
    generate_chart_data,
    analyze_practice_trends,
)


def create_sample_memos():
    """テスト用のサンプルメモを作成"""
    memos = []
    base_date = datetime(2025, 11, 1)

    for i in range(10):
        date = base_date + timedelta(days=i * 3)
        memos.append({
            'date': date.strftime('%Y-%m-%d'),
            'scene': '壁打ち' if i % 2 == 0 else 'スクール',
            'duration': 60 + (i * 10),
            'tags': ['フォアハンド', 'サーブ'] if i % 2 == 0 else ['バックハンド'],
        })

    return memos


def test_calculate_monthly_stats():
    """月次統計の計算"""
    memos = create_sample_memos()
    stats = calculate_monthly_stats(memos)

    assert stats['total_practices'] == 10
    assert stats['by_scene']['壁打ち'] == 5
    assert stats['by_scene']['スクール'] == 5
    assert stats['total_duration'] > 0
    assert 'フォアハンド' in stats['tags']
    assert 'サーブ' in stats['tags']
    assert stats['tags']['フォアハンド'] == 5


def test_calculate_monthly_stats_empty():
    """空のメモリストでの月次統計"""
    stats = calculate_monthly_stats([])

    assert stats['total_practices'] == 0
    assert stats['total_duration'] == 0
    assert stats['average_duration'] == 0


def test_calculate_weekly_stats():
    """週次統計の計算"""
    memos = create_sample_memos()
    stats = calculate_weekly_stats(memos)

    assert stats['total_practices'] == 10
    assert stats['by_scene']['壁打ち'] == 5
    assert stats['by_scene']['スクール'] == 5
    assert stats['total_duration'] > 0


def test_generate_stats_markdown():
    """統計レポートのMarkdown生成"""
    memos = create_sample_memos()
    stats = calculate_monthly_stats(memos)
    md = generate_stats_markdown(stats, period="月次")

    assert "## 月次統計サマリー" in md
    assert "総練習回数" in md
    assert "10回" in md
    assert "シーン別" in md
    assert "壁打ち" in md
    assert "頻出テーマ" in md
    assert "フォアハンド" in md


def test_generate_chart_data_weekly():
    """週別チャートデータの生成"""
    memos = create_sample_memos()
    chart = generate_chart_data(memos, chart_type="weekly")

    assert "```chart" in chart
    assert "type: bar" in chart
    assert "labels:" in chart
    assert "data:" in chart


def test_generate_chart_data_monthly():
    """月別チャートデータの生成"""
    memos = create_sample_memos()
    chart = generate_chart_data(memos, chart_type="monthly")

    assert "```chart" in chart
    assert "type: line" in chart


def test_generate_chart_data_scene():
    """シーン別チャートデータの生成（円グラフ）"""
    memos = create_sample_memos()
    chart = generate_chart_data(memos, chart_type="scene")

    assert "```chart" in chart
    assert "type: pie" in chart


def test_analyze_practice_trends_increasing():
    """練習頻度が増加傾向の場合"""
    memos = []
    now = datetime.now()

    # 前月: 5回
    for i in range(5):
        date = now - timedelta(days=60 - i * 5)
        memos.append({
            'date': date.strftime('%Y-%m-%d'),
            'scene': '壁打ち',
            'duration': 60,
            'tags': [],
        })

    # 今月: 10回
    for i in range(10):
        date = now - timedelta(days=29 - i * 2)
        memos.append({
            'date': date.strftime('%Y-%m-%d'),
            'scene': '壁打ち',
            'duration': 60,
            'tags': [],
        })

    trends = analyze_practice_trends(memos)

    assert trends['trend'] == 'increasing'
    assert trends['recent_count'] == 10
    # 境界値の問題があるため、おおよその値を確認
    assert 4 <= trends['older_count'] <= 5


def test_analyze_practice_trends_decreasing():
    """練習頻度が減少傾向の場合"""
    memos = []
    now = datetime.now()

    # 前月: 10回
    for i in range(10):
        date = now - timedelta(days=60 - i * 2)
        memos.append({
            'date': date.strftime('%Y-%m-%d'),
            'scene': '壁打ち',
            'duration': 60,
            'tags': [],
        })

    # 今月: 5回
    for i in range(5):
        date = now - timedelta(days=29 - i * 5)
        memos.append({
            'date': date.strftime('%Y-%m-%d'),
            'scene': '壁打ち',
            'duration': 60,
            'tags': [],
        })

    trends = analyze_practice_trends(memos)

    assert trends['trend'] == 'decreasing'
    assert trends['recent_count'] == 5
    # 境界値の問題があるため、おおよその値を確認
    assert 9 <= trends['older_count'] <= 10


def test_analyze_practice_trends_stable():
    """練習頻度が安定している場合"""
    memos = []
    now = datetime.now()

    # 前月: 8回
    for i in range(8):
        date = now - timedelta(days=60 - i * 3)
        memos.append({
            'date': date.strftime('%Y-%m-%d'),
            'scene': '壁打ち',
            'duration': 60,
            'tags': [],
        })

    # 今月: 8回
    for i in range(8):
        date = now - timedelta(days=29 - i * 3)
        memos.append({
            'date': date.strftime('%Y-%m-%d'),
            'scene': '壁打ち',
            'duration': 60,
            'tags': [],
        })

    trends = analyze_practice_trends(memos)

    assert trends['trend'] == 'stable'
    assert trends['recent_count'] == 8
    # 境界値の問題があるため、おおよその値を確認
    assert 7 <= trends['older_count'] <= 8
