"""
Sensation-based search with synonym expansion.

感覚表現での検索機能。類義語辞書を使用してキーワードを展開し、
より柔軟な検索を実現する。
"""
from typing import List, Dict, Any, Optional
from collections import Counter
import re


# 感覚表現の類義語辞書
SENSATION_SYNONYMS = {
    "シュッ": ["シュッ", "すっ", "スッ", "滑らか", "スムーズ", "流れる"],
    "パチン": ["パチン", "ぱちん", "弾く", "はじく", "カチッ", "当たり"],
    "ふわっ": ["ふわっ", "ふわり", "軽い", "柔らかい", "浮く", "ふんわり"],
    "ガツン": ["ガツン", "がつん", "強い", "パワー", "厚い当たり", "重い"],
    "ピタッ": ["ピタッ", "ぴたっ", "止まる", "安定", "コントロール", "ピタリ"],
    "ズバッ": ["ズバッ", "ずばっ", "ずばん", "鋭い", "切れる", "シャープ"],
    "ドンッ": ["ドンッ", "どんっ", "踏み込む", "体重", "沈む"],
    "スパーン": ["スパーン", "すぱーん", "抜ける", "突き抜ける", "伸びる"],
}

# 技術キーワードの類義語辞書
TECHNIQUE_SYNONYMS = {
    "サーブ": ["サーブ", "サービス", "serve"],
    "フォアハンド": ["フォアハンド", "フォア", "forehand", "FH"],
    "バックハンド": ["バックハンド", "バック", "backhand", "BH"],
    "ボレー": ["ボレー", "volley", "前衛"],
    "スマッシュ": ["スマッシュ", "smash", "オーバーヘッド"],
    "ストローク": ["ストローク", "stroke", "グラウンドストローク"],
    "スライス": ["スライス", "slice", "カット"],
    "トップスピン": ["トップスピン", "topspin", "スピン", "回転"],
    "フラット": ["フラット", "flat", "平ら"],
}


def expand_sensation_keywords(query: str) -> List[str]:
    """
    感覚表現のクエリを類義語で展開する。

    Args:
        query: 検索クエリ

    Returns:
        展開されたキーワードリスト
    """
    keywords = [query]

    # 感覚表現の類義語を追加
    for key, synonyms in SENSATION_SYNONYMS.items():
        if key in query:
            keywords.extend(synonyms)

    # 技術キーワードの類義語を追加
    for key, synonyms in TECHNIQUE_SYNONYMS.items():
        if key in query:
            keywords.extend(synonyms)

    # 重複を削除
    return list(set(keywords))


def score_sensation_results(
    results: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """
    検索結果をスコアリングして関連度順にソートする。

    Args:
        results: 検索結果のリスト
        query: 元のクエリ

    Returns:
        スコア順にソートされた検索結果
    """
    scored = []

    for result in results:
        score = calculate_relevance_score(result, query)
        scored.append({
            **result,
            'relevance_score': score
        })

    # スコアの高い順にソート
    return sorted(scored, key=lambda x: x['relevance_score'], reverse=True)


def calculate_relevance_score(memo: Dict[str, Any], query: str) -> float:
    """
    メモの関連度スコアを計算する。

    スコアリング基準:
    - タイトルにクエリが含まれる: +10
    - 本文にクエリが含まれる: +5
    - タグにクエリが含まれる: +3
    - 複数回出現: +1 per occurrence

    Args:
        memo: メモデータ
        query: 検索クエリ

    Returns:
        関連度スコア（高いほど関連性が高い）
    """
    score = 0.0
    query_lower = query.lower()

    # タイトルでの出現
    title = memo.get('title', '').lower()
    if query_lower in title:
        score += 10
        score += title.count(query_lower) - 1  # 追加出現

    # 本文での出現
    body = memo.get('body', '').lower()
    body_count = body.count(query_lower)
    if body_count > 0:
        score += 5 + (body_count - 1)

    # タグでの出現
    tags = memo.get('tags', [])
    for tag in tags:
        if query_lower in tag.lower():
            score += 3

    # 日付の新しさを考慮（最新のメモに若干の優先度）
    try:
        from datetime import datetime
        memo_date = datetime.strptime(memo.get('date', '2000-01-01'), '%Y-%m-%d')
        days_old = (datetime.now() - memo_date).days

        # 最新30日は+2、それ以降は徐々に減少
        if days_old <= 30:
            score += 2
        elif days_old <= 90:
            score += 1
    except Exception:
        pass

    return score


async def search_sensation(
    query: str,
    obsidian_manager,
    limit: int = 5,
    scene_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    感覚表現で検索を実行する。

    Args:
        query: 検索クエリ（感覚表現）
        obsidian_manager: ObsidianManagerインスタンス
        limit: 最大結果数
        scene_name: シーン名でフィルタ（オプション）

    Returns:
        関連度順にソートされた検索結果
    """
    # 類義語を展開
    expanded_keywords = expand_sensation_keywords(query)

    # 各キーワードで検索
    all_results = []
    seen_paths = set()

    for keyword in expanded_keywords:
        keyword_results = obsidian_manager.search_by_keyword(
            keyword=keyword,
            scene_name=scene_name,
            max_results=limit * 2  # 多めに取得してスコアリング
        )

        # 重複を避けるためfile_pathでチェック
        for result in keyword_results:
            file_path = result.get('file_path')
            if file_path not in seen_paths:
                all_results.append(result)
                seen_paths.add(file_path)

    # スコアリングしてソート
    scored_results = score_sensation_results(all_results, query)

    # 上位N件を返す
    return scored_results[:limit]


def extract_sensation_keywords(text: str) -> List[str]:
    """
    テキストから感覚表現のキーワードを抽出する。

    Args:
        text: 抽出元のテキスト

    Returns:
        抽出された感覚表現キーワードのリスト
    """
    found_keywords = []

    # 感覚表現辞書から検索
    for key in SENSATION_SYNONYMS.keys():
        if key in text:
            found_keywords.append(key)

    # オノマトペの一般的なパターンを抽出
    # カタカナ2-4文字 + 促音・長音
    onomatopoeia_pattern = r'[ァ-ヴー]{2,4}[ッー]+'
    onomatopoeia_matches = re.findall(onomatopoeia_pattern, text)
    found_keywords.extend(onomatopoeia_matches)

    # 重複を削除
    return list(set(found_keywords))
