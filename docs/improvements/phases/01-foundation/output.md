# Phase 1: 出力機能

## 概要

出力フェーズでは、処理された情報をどのように保存・表示するかを定義します。

**主要な出力先:**
- Obsidian Markdown（メイン）
- Discord通知（リマインド、レビュー）
- GitHub（バージョン管理）

---

## Obsidian Markdown の構造

### シーン別テンプレート

各シーンに最適化されたMarkdown構造を定義します。

---

### 壁打ち用テンプレート

```markdown
---
date: 2025-01-15
scene: 壁打ち
duration: 60
tags: [tennis, wall-practice, forehand, backhand]
---

# 壁打ち練習 - 2025-01-15

## 練習内容

| ドリル | 時間 | 気づき |
|--------|------|--------|
| フォアハンドストローク | 20分 | スピンが安定してきた |
| バックハンドストローク | 20分 | フォロースルーを意識 |

## 今日の焦点

フォアハンドのトップスピンを安定させる

## 身体感覚の気づき

> [!note] リアルタイムメモ（18:30）
> 手首の使い方を変えたら、スピンが安定した。
> 以前より「パチン」という感触が少なく、「シュッ」という感じ。

## 改善した点

- トップスピンの安定性が向上
- ミスが減った

## 課題として残った点

- バックハンドのスライスがまだ不安定
- 連続で打つと疲れてフォームが崩れる

## 次回やること

- [ ] バックハンドのスライスを練習
- [ ] 持久力を意識したドリル

## 前回との関連

前回（1/10）の課題：「フォアハンドのスピンを安定させる」
→ 改善！手首の使い方を変えたのが効果的だった

## 関連メモ

- [[2025-01-10 壁打ち]] - フォアハンド練習
- [[フォアハンド トップスピン]] - 技術ノート
```

---

### スクール用テンプレート

```markdown
---
date: 2025-01-15
scene: スクール
duration: 90
coach_feedback: true
tags: [tennis, school, backhand, slice]
---

# スクール練習 - 2025-01-15

## コーチからの指摘

> [!warning] コーチのアドバイス
> 「バックハンドスライス、もっと低い位置でインパクトして」
> 「ラケット面を開きすぎないように」

## 新しく学んだ技術

**バックハンドスライス**
- ラケットを高い位置から低い位置へ
- インパクトは膝の高さ
- フォロースルーは前方へ

## 練習内容

1. バックハンドスライスのフォーム確認（20分）
2. クロスコート練習（30分）
3. ダウンザライン練習（20分）
4. ゲーム形式（20分）

## 自分の気づき

> [!note] リアルタイムメモ（19:00）
> スライスは「切る」イメージより「押し出す」イメージの方がうまくいく。
> コーチの言う「低い位置」が最初わからなかったけど、膝の高さと理解した。

## 次回までの課題

> [!todo] 宿題
> - [ ] 壁打ちでスライスを100本練習
> - [ ] ラケット面の角度を意識
> - [ ] 次回までに動画を撮って確認

## 次回やること

- バックハンドスライスの精度向上
- ダウンザラインのコントロール

## 前回との関連

前回（1/10）: バックハンドの基礎を確認
→ 今回: スライスという新しい技術に挑戦

## 関連メモ

- [[バックハンド スライス]] - 技術ノート
- [[2025-01-10 スクール]] - 前回のスクール
```

---

### 試合用テンプレート

```markdown
---
date: 2025-01-15
scene: 試合
opponent: 田中さん
opponent_level: 中級
score: 6-4, 6-3
result: 勝ち
tags: [tennis, match, win, serve]
---

# 試合 - 2025-01-15

## 試合結果

| 項目 | 内容 |
|------|------|
| **対戦相手** | 田中さん |
| **相手レベル** | 中級 |
| **スコア** | 6-4, 6-3 |
| **結果** | 勝ち |

## 良かったプレー

> [!success] うまくいったこと
> **サーブ:**
> トスを前に上げたら威力が増した。ファーストサーブの確率も高かった。
>
> **フォアハンド:**
> クロスのストロークが安定していた。

## 課題となったプレー

> [!warning] 改善が必要
> **バックハンド:**
> ミスが多かった。特にダウンザラインが入らない。
>
> **リターン:**
> セカンドサーブのリターンで攻め切れなかった。

## メンタル面

> [!note] 心理状態
> 第1セットの序盤、焦りがあった。
> 「落ち着け」と自分に言い聞かせたら、ペースを取り戻せた。

## 戦術・戦略

**相手の特徴:**
- フォアハンドが強い
- バックハンドは普通
- ネットプレーは少ない

**自分の戦術:**
- 相手のバックハンドを攻める
- サーブ&ボレーは控えめに
- クロスラリーで粘る

## 次回への課題

- [ ] バックハンドの精度向上（特にダウンザライン）
- [ ] セカンドサーブのリターンを攻撃的に
- [ ] 試合の序盤でペースを掴む練習

## 前回との関連

前回の試合（1/8）: 負け（4-6, 3-6）
→ サーブの改善が今回の勝因！

## 関連メモ

- [[2025-01-08 試合]] - 前回の試合
- [[サーブ トス位置]] - 技術ノート
```

---

### 振り返り・追記の構造

```markdown
> [!tip] 振り返り・追記（2025-01-16 22:00）
> 実は、サーブのトス改善は前日のコーチのアドバイスがきっかけだった。
> 「トスをもう少し前に」と言われていて、それを試合で意識した。
> 次回は、トスの高さも意識してみよう。
```

---

## Markdown生成の実装

```python
from datetime import datetime
from pathlib import Path

def generate_wall_practice_markdown(data: dict) -> str:
    """壁打ちメモのMarkdown生成"""

    return f"""---
date: {data['date']}
scene: 壁打ち
duration: {data.get('duration', '')}
tags: {data.get('tags', ['tennis', 'wall-practice'])}
---

# 壁打ち練習 - {data['date']}

## 今日の焦点

{data.get('focus', '')}

## 身体感覚の気づき

> [!note] リアルタイムメモ（{data['timestamp'].split(' ')[1]}）
> {data.get('body_sensation', '')}

## 改善した点

{data.get('improvement', '')}

## 課題として残った点

{data.get('issue', '')}

## 次回やること

{data.get('next_action', '')}
"""

def generate_school_markdown(data: dict) -> str:
    """スクールメモのMarkdown生成"""

    return f"""---
date: {data['date']}
scene: スクール
duration: {data.get('duration', 90)}
coach_feedback: true
tags: {data.get('tags', ['tennis', 'school'])}
---

# スクール練習 - {data['date']}

## コーチからの指摘

> [!warning] コーチのアドバイス
> {data.get('coach_feedback', '')}

## 新しく学んだ技術

{data.get('new_technique', '')}

## 練習内容

{data.get('practice_content', '')}

## 自分の気づき

> [!note] リアルタイムメモ（{data['timestamp'].split(' ')[1]}）
> {data.get('realization', '')}

## 次回までの課題

{data.get('homework', '')}

## 次回やること

{data.get('next_action', '')}
"""

def generate_match_markdown(data: dict) -> str:
    """試合メモのMarkdown生成"""

    return f"""---
date: {data['date']}
scene: 試合
opponent: {data.get('opponent', '不明')}
opponent_level: {data.get('opponent_level', '不明')}
score: {data.get('score', '不明')}
result: {data.get('result', '不明')}
tags: {data.get('tags', ['tennis', 'match'])}
---

# 試合 - {data['date']}

## 試合結果

| 項目 | 内容 |
|------|------|
| **対戦相手** | {data.get('opponent', '不明')} |
| **相手レベル** | {data.get('opponent_level', '不明')} |
| **スコア** | {data.get('score', '不明')} |
| **結果** | {data.get('result', '不明')} |

## 良かったプレー

{data.get('good_plays', '')}

## 課題となったプレー

{data.get('bad_plays', '')}

## メンタル面

{data.get('mental', '')}

## 戦術・戦略

{data.get('strategy', '')}

## 次回への課題

{data.get('next_action', '')}
"""

def generate_media_markdown(data: dict, media_type: str) -> str:
    """画像・動画メモのMarkdown生成"""

    media_embed = f"![[{data['file_path']}]]" if media_type == 'image' else f"![[{data['file_path']}]]"

    return f"""---
date: {data.get('date', datetime.now().strftime('%Y-%m-%d'))}
scene: {data['scene']}
input_type: {media_type}
tags: [tennis, {data['scene']}, {media_type}]
---

# {data['scene']} - {data.get('date', datetime.now().strftime('%Y-%m-%d'))}

## 添付ファイル

{media_embed}

## メモ

{data.get('user_comment', '')}
"""
```

---

## 週次レビューの自動生成

### 目的

- 1週間の活動を振り返る
- 成長を実感させる
- 次週の目標を設定

### 生成タイミング

- 毎週日曜日の夜（21:00）
- または `/weekly-review` コマンド

### テンプレート

```markdown
---
date: 2025-01-19
type: weekly-review
week: 2025-W03
tags: [review, weekly]
---

# 週次レビュー（1/13 - 1/19）

## 今週の練習サマリー

| 指標 | 値 |
|------|-----|
| **練習日数** | 3日 |
| **合計時間** | 4時間 |
| **壁打ち** | 1回 |
| **スクール** | 1回 |
| **試合** | 1回 |

### 日別の活動

| 日付 | シーン | 時間 | 概要 |
|------|--------|------|------|
| 1/15 | スクール | 90分 | バックハンドスライス習得 |
| 1/17 | 壁打ち | 60分 | フォアハンド練習 |
| 1/18 | 試合 | 90分 | 田中さんと練習試合（勝ち） |

## 今週の成長

### 改善した課題

1. **サーブのトス位置**
   - 1/15に発見（スクール）
   - 1/18の試合で実践
   - 結果: サーブの威力向上、勝利に貢献

2. **フォアハンドのトップスピン**
   - 1/17の壁打ちで改善
   - 手首の使い方を変更

### 継続中の課題

1. **バックハンドの精度**
   - 1/15でスライスを学習
   - 1/18の試合でまだミスが多い
   - 次週も継続練習が必要

## 頻出キーワード

今週よく出てきたテーマ:

1. **サーブ**（5回）
2. **トス**（4回）
3. **バックハンド**（4回）
4. **スライス**（3回）

## 次週の目標

> [!todo] 次週やること
> - [ ] バックハンドスライスの精度向上
> - [ ] サーブのトス、再現性を高める
> - [ ] 壁打ちで基礎固め

## AIからの提案

> [!tip] 分析・提案
> **素晴らしい成長:**
> サーブが大きく改善しました。1週間で「学習→実践→成功」のサイクルを回せています。
>
> **次のステップ:**
> 好調な時の「身体感覚」をもっと言語化すると、再現性が高まります。
>
> **継続のコツ:**
> バックハンドは焦らず、基礎練習を積み重ねましょう。

## 今週のメモ一覧

- [[2025-01-15 スクール]]
- [[2025-01-17 壁打ち]]
- [[2025-01-18 試合]]

---

**次回レビュー:** 2025-01-26
```

### 実装コード

```python
from datetime import datetime, timedelta
from collections import Counter

async def generate_weekly_review(obsidian_manager: ObsidianManager) -> str:
    """週次レビューを自動生成"""

    # 今週の範囲を計算
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # 月曜日
    week_end = week_start + timedelta(days=6)  # 日曜日

    # 今週のメモを取得
    memos = obsidian_manager.get_memos_in_range(week_start, week_end)

    if len(memos) == 0:
        return "今週の練習記録がありません。"

    # 統計を計算
    stats = calculate_stats(memos)

    # 頻出キーワードを抽出
    keywords = extract_frequent_keywords(memos)

    # 改善した課題を分析
    improvements = analyze_improvements(memos)

    # AIの提案を生成
    ai_suggestion = await generate_ai_suggestion(memos, stats)

    # Markdownを生成
    markdown = render_weekly_review(
        week_start=week_start,
        week_end=week_end,
        memos=memos,
        stats=stats,
        keywords=keywords,
        improvements=improvements,
        ai_suggestion=ai_suggestion
    )

    return markdown

def calculate_stats(memos: list) -> dict:
    """統計を計算"""
    return {
        "practice_days": len(set(m.get('date', '') for m in memos)),
        "total_duration": sum(m.get('duration', 0) for m in memos),
        "by_scene": {
            scene: len([m for m in memos if m.get('scene') == scene])
            for scene in ["壁打ち", "スクール", "試合", "フリー練習"]
        }
    }

def extract_frequent_keywords(memos: list) -> list:
    """頻出キーワードを抽出"""
    all_keywords = []
    for memo in memos:
        all_keywords.extend(memo.get('tags', []))

    counter = Counter(all_keywords)
    return counter.most_common(10)
```

---

## リマインド・通知機能

### 練習開始時のリマインド

```python
async def send_practice_start_reminder(user_id: int, scene_type: str):
    """練習開始時に前回の課題をリマインド"""

    obsidian_manager = ObsidianManager(VAULT_PATH)
    last_memo = obsidian_manager.get_latest_memo(scene_type)

    if not last_memo:
        return

    next_action = last_memo.get('next_action')

    if next_action:
        message = f"""
おはようございます！{scene_type}の練習ですね。

**前回の課題:**
{next_action}

今日はこれを意識してみますか？
それとも別のテーマで練習しますか？

練習後に気づきを音声で送信してください！
"""
        await send_discord_dm(user_id, message)
```

### スケジューラー設定

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

def setup_scheduler(bot):
    """スケジューラーを設定"""

    scheduler = AsyncIOScheduler()

    # 週次レビュー: 毎週日曜日21:00
    scheduler.add_job(
        generate_and_send_weekly_review,
        CronTrigger(day_of_week='sun', hour=21, minute=0),
        id='weekly_review'
    )

    scheduler.start()
    return scheduler

async def generate_and_send_weekly_review():
    """週次レビューを生成してDiscordに送信"""

    obsidian_manager = ObsidianManager(VAULT_PATH)
    review = await generate_weekly_review(obsidian_manager)

    # Markdownファイルとして保存
    week_str = datetime.now().strftime('%Y-W%W')
    file_path = Path(VAULT_PATH) / "weekly-reviews" / f"{week_str}.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(review)

    # Git commit & push
    await git_commit_and_push(f"週次レビュー: {week_str}")

    # Discordに通知
    await send_to_discord_channel("週次レビュー", review[:1500])
```

---

## ファイル構成

```
obsidian-vault/
├── daily/
│   ├── 2025-01-15-スクール.md
│   ├── 2025-01-17-壁打ち.md
│   └── 2025-01-18-試合.md
├── weekly-reviews/
│   ├── 2025-W02.md
│   └── 2025-W03.md
├── attachments/
│   └── 2025-01-27/
│       ├── 2025-01-27_壁打ち_143000.jpg
│       └── 2025-01-27_壁打ち_150000.mp4
└── templates/
    ├── wall-practice.md
    ├── school.md
    └── match.md
```

---

## 自動リンク生成

```python
async def generate_auto_links(memo: dict, obsidian_manager: ObsidianManager) -> str:
    """関連メモへのリンクを自動生成"""

    links = []

    # 前後のメモを取得
    scene = memo.get('scene')
    date = datetime.strptime(memo['date'], '%Y-%m-%d')

    all_memos = obsidian_manager.get_memos_in_range(
        date - timedelta(days=30),
        date + timedelta(days=30)
    )

    # 同じシーンの前後
    same_scene = [m for m in all_memos if m.get('scene') == scene]
    for m in same_scene:
        if m['date'] < memo['date']:
            links.append(f"- [[{m['date']} {scene}]] - 前回")
        elif m['date'] > memo['date']:
            links.append(f"- [[{m['date']} {scene}]] - 次回")

    return "\n".join(links[:5])  # 最大5件
```

---

## 次のドキュメント

- [../02-dialogue/index.md](../02-dialogue/index.md) - Phase 2: 対話の深化
- [../../technical/index.md](../../technical/index.md) - 技術詳細
