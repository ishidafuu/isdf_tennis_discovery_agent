# システムアーキテクチャ

## 全体フロー

```
Discord Bot (discord.py)
    ↓ 音声/テキスト/画像/動画メッセージ
Gemini AI (文字起こし)
    ↓ テキスト
構造化データ抽出 (Gemini)
    ↓ JSON
ObsidianManager (保存)
    ↓ Markdown
Obsidian Vault (ファイルシステム)
    ↓ Git
GitHub (バックアップ)
```

---

## 主要コンポーネント

### 1. Discord Bot (`src/bot/`)

| ファイル | 責務 |
|---------|------|
| `client.py` | Botクライアントの初期化と起動 |
| `channel_handler.py` | チャンネル別のメッセージ処理 |
| `action_buttons.py` | オプションボタンUI |
| `reminder.py` | リマインド通知 |
| `scheduler.py` | 定期実行タスク |

### 2. AI処理 (`src/ai/`)

| ファイル | 責務 |
|---------|------|
| `transcription.py` | 音声文字起こし（Gemini） |
| `structured_extraction.py` | 構造化データ抽出 |
| `prompts.py` | シーン別プロンプト定義 |
| `question_generation.py` | 追加質問生成 |
| `auto_decision.py` | AIの自動判断ロジック |
| `date_extraction.py` | テキストからの日付抽出 |
| `relation_detection.py` | 前回メモとの関連性判定 |

### 3. ストレージ (`src/storage/`)

| ファイル | 責務 |
|---------|------|
| `obsidian_manager.py` | Obsidian読み書き・検索 |
| `markdown_templates.py` | Markdownテンプレート生成 |
| `auto_linking.py` | 関連メモへの自動リンク生成 |
| `git_manager.py` | Git操作（Push、リトライ） |

### 4. 分析 (`src/analysis/`)

| ファイル | 責務 |
|---------|------|
| `weekly_review.py` | 週次レビュー自動生成 |
| `comparison.py` | 過去との比較分析 |
| `contradiction_detection.py` | 矛盾検出 |
| `statistics.py` | 統計計算 |
| `pattern_analysis.py` | パターン分析 |

### 5. 検索 (`src/search/`)

| ファイル | 責務 |
|---------|------|
| `keyword_search.py` | キーワード検索 |
| `vector_search.py` | ベクトル検索（Phase 4） |

---

## データ管理: Obsidian-Only

### 設計方針

すべてのデータをObsidian Vaultに保存します。**データベースは使用しません。**

### メリット

- **シンプル**: データベースファイルが不要
- **可搬性**: Markdownファイルなのでどこでも使える
- **可視性**: Obsidianで直接確認・編集できる
- **バックアップ**: Git/GitHubで完結
- **柔軟性**: 他のツールとの連携が容易
- **ロックイン回避**: 特定のデータベースに依存しない

### ディレクトリ構造

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

### Frontmatterによるメタデータ管理

```yaml
---
id: uuid-here
date: 2025-01-27
timestamp: 2025-01-27 14:30
scene: 壁打ち
tags: [サーブ, トス]
important: false
---
```

---

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| **言語** | Python 3.10+ |
| **Discord** | discord.py 2.3.2 |
| **AI** | Google Gemini 1.5 Flash |
| **ノート** | Obsidian Markdown |
| **バージョン管理** | Git + GitHub |
| **メディア管理** | Git LFS |
| **スケジューラー** | APScheduler |

---

## 入力タイプ別の処理フロー

### 音声メモ

```
音声メッセージ → Gemini文字起こし → 構造化 → Markdown保存
```

### テキストメモ

```
テキストメッセージ → URL検出 → 構造化 → Markdown保存
```

### 画像メモ

```
画像添付 → ファイル保存 → コメント記録 → Markdown保存
※ 画像解析は行わない
```

### 動画メモ

```
動画添付 → ファイル保存 → コメント記録 → Markdown保存
※ 動画解析は行わない
```

---

## パフォーマンス考慮事項

### Obsidian-Onlyの性能

**個人利用なら十分高速:**
- 年間数百〜数千件のメモ → ファイルシステムで十分
- Obsidianの自動インデックス機能を活用
- Dataviewプラグインのキャッシュで高速化

**将来的な拡張:**
- パフォーマンス問題が出たら、その時に検討
- SQLiteインデックスの追加も可能（オプション）

### API制限

| API | 制限 |
|-----|------|
| **Gemini API** | 無料枠: 1分あたり15リクエスト |
| **Discord** | 音声/画像/動画: 最大25MB |
| **Git LFS** | GitHub無料枠: 1GB/月 |

---

## 次のドキュメント

- [03-success-criteria.md](03-success-criteria.md) - 成功の定義
- [../technical/](../technical/index.md) - 技術詳細
