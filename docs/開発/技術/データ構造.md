# データ構造

## メモのデータ構造

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Memo:
    """メモのデータ構造"""

    # 基本情報
    id: str  # UUID
    date: datetime
    timestamp: datetime
    scene: str  # "壁打ち", "スクール", "試合", etc.

    # 音声・テキスト
    audio_url: Optional[str]
    raw_text: str  # 文字起こしテキスト

    # 構造化データ（シーン別に異なる）
    structured_data: dict

    # メタデータ
    tags: List[str]
    important: bool = False

    # 関連性
    previous_memo_id: Optional[str]
    next_memo_id: Optional[str]
    related_memo_ids: List[str]

    # ファイルパス
    markdown_path: str
    obsidian_vault_path: str

    # GitHub
    github_commit_hash: Optional[str]
```

---

## シーン別の構造化データ

### 壁打ち

```python
@dataclass
class WallPracticeData:
    drill: str  # 実施したドリル
    duration: int  # 時間（分）
    focus: str  # 今日の焦点
    body_sensation: str  # 身体感覚
    improvement: Optional[str]  # 改善した点
    issue: Optional[str]  # 課題
    next_action: Optional[str]  # 次回やること
```

### スクール

```python
@dataclass
class SchoolData:
    coach_feedback: Optional[str]  # コーチの指摘
    new_technique: Optional[str]  # 新しく学んだ技術
    practice_content: str  # 練習内容
    realization: Optional[str]  # 自分の気づき
    homework: Optional[str]  # 宿題
    next_action: Optional[str]  # 次回やること
```

### 試合

```python
@dataclass
class MatchData:
    opponent: Optional[str]  # 対戦相手
    opponent_level: Optional[str]  # 相手のレベル
    score: Optional[str]  # スコア（例: "6-4, 6-3"）
    result: Optional[str]  # "勝ち", "負け", "不明"
    good_plays: Optional[str]  # 良かったプレー
    bad_plays: Optional[str]  # 課題となったプレー
    mental: Optional[str]  # メンタル面
    strategy: Optional[str]  # 戦術・戦略
    next_action: Optional[str]  # 次回への課題
```

---

## Frontmatterによるメタデータ管理

各Markdownファイルの先頭にYAML Frontmatterでメタデータを記録：

```yaml
---
id: uuid-here
date: 2025-01-27
timestamp: 2025-01-27 14:30
scene: 壁打ち
tags: [サーブ, トス]
important: false
---

# 2025-01-27 壁打ち練習

## メモ
今日はサーブのトスを重点的に練習した...
```

---

## Obsidian Vault構造

```
obsidian-vault/
├── daily/
│   ├── 2025-01-27-壁打ち.md
│   ├── 2025-01-27-スクール.md
│   └── 2025-01-28-試合.md
├── weekly-reviews/
│   └── 2025-W04.md
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

## Obsidian Dataviewによるクエリ

Dataviewプラグインを使用して、Markdownファイルをデータベースのようにクエリできます：

```dataview
TABLE scene as "シーン", tags as "タグ"
FROM "daily"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```

**パフォーマンス:**
- 個人利用（年間数百〜数千件）なら十分高速
- Obsidianが自動的にインデックスを管理
- 必要に応じてDataviewがキャッシュを活用

---

## 次のドキュメント

- [discord-bot.md](discord-bot.md) - Discord Bot実装
