"""
Statistical analysis and graph generation for practice memos.

練習記録の統計分析とグラフ生成機能。月次/週次の統計を計算し、
Obsidian Chartsプラグインと連携したデータ可視化を提供する。
"""
from typing import List, Dict, Any, Tuple
from collections import Counter
from datetime import datetime, timedelta


def calculate_monthly_stats(memos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    月次統計を計算する。

    Args:
        memos: メモのリスト

    Returns:
        月次統計データ
    """
    if not memos:
        return {
            "total_practices": 0,
            "by_scene": {},
            "by_week": {},
            "total_duration": 0,
            "tags": {},
            "average_duration": 0,
        }

    # 基本統計
    total_duration = sum(m.get('duration', 0) for m in memos)
    stats = {
        "total_practices": len(memos),
        "by_scene": Counter(m.get('scene', '不明') for m in memos),
        "by_week": {},
        "total_duration": total_duration,
        "average_duration": total_duration / len(memos) if memos else 0,
        "tags": Counter(),
    }

    # 週別の集計
    for memo in memos:
        date_str = memo.get('date', '')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                week = date.isocalendar()[1]
                stats["by_week"][week] = stats["by_week"].get(week, 0) + 1
            except ValueError:
                pass

        # タグの集計
        for tag in memo.get('tags', []):
            stats["tags"][tag] += 1

    return stats


def calculate_weekly_stats(memos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    週次統計を計算する。

    Args:
        memos: メモのリスト

    Returns:
        週次統計データ
    """
    if not memos:
        return {
            "total_practices": 0,
            "by_scene": {},
            "by_day": {},
            "total_duration": 0,
            "tags": {},
        }

    # 基本統計
    stats = {
        "total_practices": len(memos),
        "by_scene": Counter(m.get('scene', '不明') for m in memos),
        "by_day": {},
        "total_duration": sum(m.get('duration', 0) for m in memos),
        "tags": Counter(),
    }

    # 曜日別の集計
    weekday_names = ['月', '火', '水', '木', '金', '土', '日']
    for memo in memos:
        date_str = memo.get('date', '')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = weekday_names[date.weekday()]
                stats["by_day"][weekday] = stats["by_day"].get(weekday, 0) + 1
            except ValueError:
                pass

        # タグの集計
        for tag in memo.get('tags', []):
            stats["tags"][tag] += 1

    return stats


def generate_stats_markdown(stats: Dict[str, Any], period: str = "月次") -> str:
    """
    統計データからMarkdownレポートを生成する。

    Args:
        stats: 統計データ
        period: 期間（"月次"、"週次"など）

    Returns:
        Markdownフォーマットの統計レポート
    """
    md = f"""## {period}統計サマリー

| 指標 | 値 |
|------|-----|
| **総練習回数** | {stats['total_practices']}回 |
| **合計時間** | {stats['total_duration']}分 |
"""

    # 平均時間（月次統計の場合のみ）
    if 'average_duration' in stats:
        md += f"| **平均時間** | {stats['average_duration']:.1f}分/回 |\n"

    md += "\n### シーン別\n\n| シーン | 回数 |\n|--------|------|\n"

    for scene, count in stats['by_scene'].most_common():
        md += f"| {scene} | {count}回 |\n"

    # 頻出テーマ
    if stats['tags']:
        md += "\n### 頻出テーマ\n\n"
        for tag, count in stats['tags'].most_common(10):
            md += f"- **{tag}** ({count}回)\n"

    return md


def generate_chart_data(
    memos: List[Dict[str, Any]],
    chart_type: str = "weekly"
) -> str:
    """
    Obsidian Charts用のデータを生成する。

    Args:
        memos: メモのリスト
        chart_type: チャートの種類（"weekly", "monthly", "scene"）

    Returns:
        Obsidian Chart記法のMarkdown
    """
    if chart_type == "weekly":
        return generate_weekly_chart(memos)
    elif chart_type == "monthly":
        return generate_monthly_chart(memos)
    elif chart_type == "scene":
        return generate_scene_chart(memos)
    else:
        return ""


def generate_weekly_chart(memos: List[Dict[str, Any]]) -> str:
    """
    週別の練習回数チャートを生成する。

    Args:
        memos: メモのリスト

    Returns:
        Obsidian Chart記法のMarkdown
    """
    # 週別にデータを集計
    weekly_data = {}
    for memo in memos:
        date_str = memo.get('date', '')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                # 週の開始日（月曜日）を取得
                week_start = date - timedelta(days=date.weekday())
                week_str = week_start.strftime('%m/%d')
                weekly_data[week_str] = weekly_data.get(week_str, 0) + 1
            except ValueError:
                pass

    if not weekly_data:
        return ""

    # ソート
    sorted_weeks = sorted(weekly_data.items(), key=lambda x: x[0])

    labels = [week for week, _ in sorted_weeks]
    data = [count for _, count in sorted_weeks]

    chart_md = f"""```chart
type: bar
labels: [{", ".join(f'"{label}"' for label in labels)}]
series:
  - title: 練習回数
    data: [{", ".join(str(d) for d in data)}]
```"""

    return chart_md


def generate_monthly_chart(memos: List[Dict[str, Any]]) -> str:
    """
    月別の練習回数チャートを生成する。

    Args:
        memos: メモのリスト

    Returns:
        Obsidian Chart記法のMarkdown
    """
    # 月別にデータを集計
    monthly_data = {}
    for memo in memos:
        date_str = memo.get('date', '')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                month_str = date.strftime('%Y-%m')
                monthly_data[month_str] = monthly_data.get(month_str, 0) + 1
            except ValueError:
                pass

    if not monthly_data:
        return ""

    # ソート
    sorted_months = sorted(monthly_data.items(), key=lambda x: x[0])

    labels = [month for month, _ in sorted_months]
    data = [count for _, count in sorted_months]

    chart_md = f"""```chart
type: line
labels: [{", ".join(f'"{label}"' for label in labels)}]
series:
  - title: 練習回数
    data: [{", ".join(str(d) for d in data)}]
```"""

    return chart_md


def generate_scene_chart(memos: List[Dict[str, Any]]) -> str:
    """
    シーン別の練習回数チャート（円グラフ）を生成する。

    Args:
        memos: メモのリスト

    Returns:
        Obsidian Chart記法のMarkdown
    """
    # シーン別にデータを集計
    scene_data = Counter(m.get('scene', '不明') for m in memos)

    if not scene_data:
        return ""

    labels = list(scene_data.keys())
    data = list(scene_data.values())

    chart_md = f"""```chart
type: pie
labels: [{", ".join(f'"{label}"' for label in labels)}]
series:
  - title: シーン別
    data: [{", ".join(str(d) for d in data)}]
```"""

    return chart_md


def generate_dataview_queries() -> str:
    """
    Obsidian Dataviewプラグイン用のクエリ集を生成する。

    Returns:
        Dataviewクエリのコレクション（Markdown）
    """
    queries = r"""## Dataviewクエリ集

### 今週の練習

```dataview
TABLE scene AS シーン, duration AS 時間, tags AS タグ
FROM "sessions"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```

### 今月の練習

```dataview
TABLE scene AS シーン, duration AS 時間
FROM "sessions"
WHERE date >= date(today) - dur(30 days)
SORT date DESC
```

### 技術別の練習回数（トップ10）

```dataview
TABLE WITHOUT ID
  tag AS 技術,
  length(rows) AS 回数
FROM "sessions"
FLATTEN tags AS tag
WHERE tag != "tennis"
GROUP BY tag
SORT length(rows) DESC
LIMIT 10
```

### シーン別の練習時間

```dataview
TABLE WITHOUT ID
  scene AS シーン,
  sum(rows.duration) AS 合計時間,
  length(rows) AS 回数
FROM "sessions"
GROUP BY scene
SORT sum(rows.duration) DESC
```

### 最近の改善点

```dataview
TABLE date AS 日付, scene AS シーン, improvement AS 改善点
FROM "sessions"
WHERE improvement != null AND improvement != ""
SORT date DESC
LIMIT 10
```

### 未解決の課題

```dataview
TABLE date AS 日付, scene AS シーン, issue AS 課題
FROM "sessions"
WHERE issue != null AND issue != ""
SORT date DESC
LIMIT 10
```
"""
    return queries


def analyze_practice_trends(memos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    練習トレンドを分析する。

    Args:
        memos: メモのリスト

    Returns:
        トレンド分析結果
    """
    if not memos:
        return {
            "trend": "no_data",
            "message": "データがありません",
        }

    # 直近30日と前30日を比較
    now = datetime.now()
    recent_start = now - timedelta(days=30)
    older_start = now - timedelta(days=60)

    recent_memos = [
        m for m in memos
        if recent_start <= datetime.strptime(m.get('date', '2000-01-01'), '%Y-%m-%d') <= now
    ]

    older_memos = [
        m for m in memos
        if older_start <= datetime.strptime(m.get('date', '2000-01-01'), '%Y-%m-%d') < recent_start
    ]

    recent_count = len(recent_memos)
    older_count = len(older_memos)

    # トレンド判定
    if recent_count > older_count * 1.2:
        trend = "increasing"
        message = f"練習頻度が増加傾向です（前月: {older_count}回 → 今月: {recent_count}回）"
    elif recent_count < older_count * 0.8:
        trend = "decreasing"
        message = f"練習頻度が減少傾向です（前月: {older_count}回 → 今月: {recent_count}回）"
    else:
        trend = "stable"
        message = f"練習頻度は安定しています（前月: {older_count}回 → 今月: {recent_count}回）"

    return {
        "trend": trend,
        "message": message,
        "recent_count": recent_count,
        "older_count": older_count,
    }
