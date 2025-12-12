# Phase 3: データ活用の機能詳細

## 感覚検索（シンプル版）

### 概要

「あの時の感覚」を言葉で検索できる機能。

**例:**
- 「シュッという感覚」
- 「ふわっとしたボールが飛んでいく」
- 「手首がパチンと鳴る」

### 実装コード

```python
async def search_sensation(query: str, user_id: str, limit: int = 5) -> list:
    """感覚表現で検索"""

    # 類義語を展開
    expanded_keywords = expand_sensation_keywords(query)

    # Obsidianから検索
    results = []
    for keyword in expanded_keywords:
        keyword_results = await obsidian_manager.search_by_keyword(keyword, limit=limit)
        results.extend(keyword_results)

    # 重複を削除してスコアリング
    scored_results = score_sensation_results(results, query)

    return scored_results[:limit]

def expand_sensation_keywords(query: str) -> list:
    """感覚表現の類義語を展開"""

    # 感覚表現の類義語辞書
    sensation_synonyms = {
        "シュッ": ["シュッ", "すっ", "スッ", "滑らか", "スムーズ"],
        "パチン": ["パチン", "ぱちん", "弾く", "はじく", "カチッ"],
        "ふわっ": ["ふわっ", "ふわり", "軽い", "柔らかい", "浮く"],
        "ガツン": ["ガツン", "がつん", "強い", "パワー", "厚い当たり"],
        "ピタッ": ["ピタッ", "ぴたっ", "止まる", "安定", "コントロール"],
    }

    keywords = [query]

    for key, synonyms in sensation_synonyms.items():
        if key in query:
            keywords.extend(synonyms)

    return list(set(keywords))
```

---

## 自動リンク生成

### 目的

- 関連するメモを自動で繋ぐ
- Obsidianのグラフビューで可視化
- ナレッジの構造化

### 実装コード

```python
async def generate_auto_links(memo: dict, obsidian_manager) -> str:
    """関連メモへのリンクを自動生成"""

    links = []

    # 1. タグベースのリンク
    tags = memo.get('tags', [])
    for tag in tags:
        related = await obsidian_manager.search_by_tag(tag, limit=3)
        for r in related:
            if r['file_path'] != memo.get('file_path'):
                links.append(f"- [[{r['date']} {r['scene']}]] - {tag}")

    # 2. 日付ベースの前後リンク
    scene = memo.get('scene')
    date = datetime.strptime(memo['date'], '%Y-%m-%d')

    prev_memo = await obsidian_manager.get_previous_memo(date, scene)
    next_memo = await obsidian_manager.get_next_memo(date, scene)

    if prev_memo:
        links.insert(0, f"- [[{prev_memo['date']} {scene}]] - 前回")
    if next_memo:
        links.append(f"- [[{next_memo['date']} {scene}]] - 次回")

    # 3. 重複を削除
    unique_links = list(dict.fromkeys(links))

    return "\n".join(unique_links[:10])

async def update_backlinks(new_memo: dict, obsidian_manager):
    """既存メモにバックリンクを追加"""

    # 新しいメモに関連するメモを検索
    tags = new_memo.get('tags', [])
    related_memos = []

    for tag in tags:
        results = await obsidian_manager.search_by_tag(tag, limit=5)
        related_memos.extend(results)

    # 各関連メモにバックリンクを追加
    for related in related_memos:
        if related['file_path'] != new_memo.get('file_path'):
            await obsidian_manager.add_backlink(
                target_file=related['file_path'],
                link_text=f"[[{new_memo['date']} {new_memo['scene']}]]"
            )
```

---

## 統計・グラフ

### 統計計算

```python
from collections import Counter
from datetime import datetime, timedelta

def calculate_monthly_stats(memos: list) -> dict:
    """月次統計を計算"""

    stats = {
        "total_practices": len(memos),
        "by_scene": Counter(m.get('scene', '不明') for m in memos),
        "by_week": {},
        "total_duration": sum(m.get('duration', 0) for m in memos),
        "tags": Counter(),
    }

    # 週別の集計
    for memo in memos:
        date = datetime.strptime(memo['date'], '%Y-%m-%d')
        week = date.isocalendar()[1]
        stats["by_week"][week] = stats["by_week"].get(week, 0) + 1

        # タグの集計
        for tag in memo.get('tags', []):
            stats["tags"][tag] += 1

    return stats

def generate_stats_markdown(stats: dict) -> str:
    """統計のMarkdownを生成"""

    md = f"""## 統計サマリー

| 指標 | 値 |
|------|-----|
| **総練習回数** | {stats['total_practices']}回 |
| **合計時間** | {stats['total_duration']}分 |

### シーン別

| シーン | 回数 |
|--------|------|
"""

    for scene, count in stats['by_scene'].most_common():
        md += f"| {scene} | {count}回 |\n"

    md += "\n### 頻出テーマ\n\n"

    for tag, count in stats['tags'].most_common(10):
        md += f"- **{tag}** ({count}回)\n"

    return md
```

### Obsidian Chartsとの連携

```python
def generate_chart_data(memos: list) -> str:
    """Obsidian Charts用のデータを生成"""

    # 週別の練習回数
    weekly_data = {}
    for memo in memos:
        date = datetime.strptime(memo['date'], '%Y-%m-%d')
        week_start = date - timedelta(days=date.weekday())
        week_str = week_start.strftime('%m/%d')
        weekly_data[week_str] = weekly_data.get(week_str, 0) + 1

    # Chart記法で出力
    chart_md = """```chart
type: bar
labels: [""" + ", ".join(f'"{k}"' for k in weekly_data.keys()) + """]
series:
  - title: 練習回数
    data: [""" + ", ".join(str(v) for v in weekly_data.values()) + """]
```"""

    return chart_md
```

### Dataviewクエリ

```markdown
# Obsidianで使用するDataviewクエリの例

## 今週の練習

```dataview
TABLE scene AS シーン, duration AS 時間
FROM "daily"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```

## 技術別の練習回数

```dataview
TABLE WITHOUT ID
  tag AS 技術,
  length(rows) AS 回数
FROM "daily"
FLATTEN tags AS tag
WHERE tag != "tennis"
GROUP BY tag
SORT length(rows) DESC
LIMIT 10
```
```

---

## リマインド機能強化

### 未練習リマインド

```python
async def check_inactive_and_remind():
    """練習していないユーザーにリマインド"""

    users = await get_all_users()
    now = datetime.now()

    for user in users:
        last_practice = await obsidian_manager.get_latest_memo(user_id=user.id)

        if not last_practice:
            continue

        last_date = datetime.strptime(last_practice['date'], '%Y-%m-%d')
        days_since = (now - last_date).days

        if days_since >= 3:
            message = f"""
こんにちは！

最後の練習から{days_since}日経ちました。
そろそろ練習しませんか？

**前回の課題:**
{last_practice.get('next_action', 'なし')}

今日時間があれば、軽く壁打ちでもいかがですか？
"""
            await send_discord_dm(user.id, message)
```

### 課題進捗リマインド

```python
async def check_issue_progress():
    """課題の進捗を確認"""

    users = await get_all_users()

    for user in users:
        # 最近の課題を取得
        recent_memos = await obsidian_manager.get_memos_in_range(
            start_date=datetime.now() - timedelta(days=14),
            end_date=datetime.now()
        )

        # 未解決の課題を抽出
        unresolved_issues = []
        for memo in recent_memos:
            issue = memo.get('next_action') or memo.get('issue')
            if issue:
                # 後続のメモで解決されていないか確認
                is_resolved = await check_if_resolved(issue, recent_memos, memo['date'])
                if not is_resolved:
                    unresolved_issues.append({
                        "date": memo['date'],
                        "issue": issue
                    })

        if unresolved_issues:
            message = f"""
**課題の進捗確認**

以下の課題はまだ取り組み中ですか？

"""
            for item in unresolved_issues[:3]:
                message += f"- {item['date']}: {item['issue']}\n"

            message += "\n取り組んだら、メモで報告してください！"

            await send_discord_dm(user.id, message)
```

### スケジューラー設定

```python
def setup_reminder_scheduler(bot):
    """リマインドスケジューラーを設定"""

    scheduler = AsyncIOScheduler()

    # 未練習リマインド: 毎日18:00
    scheduler.add_job(
        check_inactive_and_remind,
        CronTrigger(hour=18, minute=0),
        id='inactive_reminder'
    )

    # 課題進捗リマインド: 毎週水曜日19:00
    scheduler.add_job(
        check_issue_progress,
        CronTrigger(day_of_week='wed', hour=19, minute=0),
        id='issue_progress_reminder'
    )

    scheduler.start()
    return scheduler
```

---

## #分析チャンネル

### 使用例

```
#分析 チャンネルで音声送信
「今月の成長を分析して」
「3ヶ月でどのくらい成長した？」
```

### 実装コード

```python
async def handle_analysis(message: discord.Message):
    """#分析 チャンネルでの分析リクエストに対応"""

    # 分析中メッセージ
    analyzing_msg = await message.channel.send("📊 分析中...")

    # 音声またはテキストを取得
    if message.attachments:
        audio_url = message.attachments[0].url
        request = await transcribe_audio(audio_url)
    else:
        request = message.content

    # 期間を判定
    period = detect_period_from_text(request)

    # メモを取得
    start_date = datetime.now() - timedelta(days=period['days'])
    memos = await obsidian_manager.get_memos_in_range(
        start_date=start_date,
        end_date=datetime.now()
    )

    if len(memos) == 0:
        await analyzing_msg.edit(content=f"{period['label']}のメモがありません。")
        return

    # AI で分析
    analysis = await analyze_memos(memos, period['label'])

    await analyzing_msg.edit(content=analysis)

def detect_period_from_text(text: str) -> dict:
    """テキストから期間を判定"""

    if "今週" in text or "週" in text:
        return {"days": 7, "label": "今週"}
    elif "今月" in text or "月" in text:
        return {"days": 30, "label": "今月"}
    elif "3ヶ月" in text:
        return {"days": 90, "label": "3ヶ月"}
    elif "半年" in text:
        return {"days": 180, "label": "半年"}
    else:
        return {"days": 30, "label": "今月"}

async def analyze_memos(memos: list, period: str) -> str:
    """メモを分析"""

    memo_text = ""
    for memo in memos:
        memo_text += f"""
{memo['date']} ({memo.get('scene', '不明')}):
{memo.get('raw_text', memo.get('body', ''))}
改善: {memo.get('improvement', 'なし')}
課題: {memo.get('issue', 'なし')}

"""

    prompt = f"""
以下は、ユーザーの過去{period}の練習メモです。
成長を分析してください。

【メモ】
{memo_text}

【分析項目】
1. 改善した点（具体的に）
2. 継続中の課題
3. 頻繁に出てくるテーマ
4. 次に取り組むべきこと
5. 全体的な評価とアドバイス

【分析結果】
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text
```

---

## 次のドキュメント

- [../04-advanced-analysis/index.md](../04-advanced-analysis/index.md) - Phase 4: 高度な分析
