"""
Tests for sensation-based search functionality.
"""
import pytest
from src.search.sensation_search import (
    expand_sensation_keywords,
    score_sensation_results,
    calculate_relevance_score,
    extract_sensation_keywords,
)


def test_expand_sensation_keywords():
    """類義語展開が正しく動作することを確認"""
    # 感覚表現の展開
    keywords = expand_sensation_keywords("シュッという感覚")
    assert "シュッ" in keywords
    assert "スッ" in keywords
    assert "滑らか" in keywords
    assert "スムーズ" in keywords

    # 技術キーワードの展開
    keywords = expand_sensation_keywords("フォアハンドがうまくいった")
    assert "フォアハンド" in keywords
    assert "フォア" in keywords
    assert "forehand" in keywords


def test_expand_sensation_keywords_multiple():
    """複数のキーワードが含まれる場合の展開"""
    keywords = expand_sensation_keywords("ガツンと打てた")
    assert "ガツン" in keywords
    assert "強い" in keywords
    assert "パワー" in keywords


def test_calculate_relevance_score():
    """スコア計算が正しく動作することを確認"""
    # タイトルに含まれる場合
    memo = {
        'title': 'シュッという感覚',
        'body': '今日の練習は良かった',
        'tags': [],
        'date': '2025-11-29'
    }
    score = calculate_relevance_score(memo, "シュッ")
    assert score >= 10  # タイトルマッチで+10

    # 本文に含まれる場合
    memo = {
        'title': '壁打ち練習',
        'body': 'シュッという感覚が掴めた。シュッと振り抜く。',
        'tags': [],
        'date': '2025-11-29'
    }
    score = calculate_relevance_score(memo, "シュッ")
    assert score >= 5  # 本文マッチで+5以上（複数回出現）

    # タグに含まれる場合
    memo = {
        'title': '練習記録',
        'body': '今日の練習',
        'tags': ['フォアハンド', 'シュッ'],
        'date': '2025-11-29'
    }
    score = calculate_relevance_score(memo, "シュッ")
    assert score >= 3  # タグマッチで+3


def test_score_sensation_results():
    """検索結果のスコアリングとソート"""
    results = [
        {
            'title': '壁打ち',
            'body': 'テスト',
            'tags': [],
            'date': '2025-11-29'
        },
        {
            'title': 'シュッという感覚',
            'body': 'シュッシュッと振れた',
            'tags': ['フォアハンド'],
            'date': '2025-11-29'
        },
        {
            'title': '練習記録',
            'body': 'シュッと打てた',
            'tags': [],
            'date': '2025-11-28'
        }
    ]

    scored = score_sensation_results(results, "シュッ")

    # スコアが計算されている
    assert 'relevance_score' in scored[0]

    # スコア順にソートされている
    assert scored[0]['relevance_score'] >= scored[1]['relevance_score']
    assert scored[1]['relevance_score'] >= scored[2]['relevance_score']

    # 最もスコアが高いのは2番目のメモ（タイトル＋本文に複数回出現）
    assert scored[0]['title'] == 'シュッという感覚'


def test_extract_sensation_keywords():
    """テキストから感覚キーワードを抽出"""
    text = "今日はシュッという感覚でガツンと打てた"
    keywords = extract_sensation_keywords(text)

    assert "シュッ" in keywords
    assert "ガツン" in keywords


def test_extract_sensation_keywords_onomatopoeia():
    """オノマトペのパターン抽出"""
    text = "バシッという音がした。グワーンと曲がった。"
    keywords = extract_sensation_keywords(text)

    # パターンマッチしたオノマトペが抽出される
    assert any("ッ" in k for k in keywords)


def test_extract_sensation_keywords_empty():
    """感覚表現がないテキスト"""
    text = "今日は練習を休みました"
    keywords = extract_sensation_keywords(text)

    # 感覚表現がない場合は空リスト
    assert isinstance(keywords, list)
