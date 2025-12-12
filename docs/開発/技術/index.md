# 技術詳細

## 概要

このセクションでは、実装に必要な技術的詳細を定義します。

---

## 内容一覧

| ドキュメント | 説明 |
|-------------|------|
| [data-structures.md](data-structures.md) | データ構造とモデル定義 |
| [discord-bot.md](discord-bot.md) | Discord Bot実装 |
| [ai-processing.md](ai-processing.md) | AI処理（文字起こし・構造化） |
| [obsidian-storage.md](obsidian-storage.md) | Obsidianストレージ管理 |
| [knowledge-rag.md](knowledge-rag.md) | ナレッジ統合（RAG） |
| [security.md](security.md) | セキュリティ考慮事項 |

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

## ディレクトリ構成

```
tennis-discovery-agent/
├── src/
│   ├── __init__.py
│   ├── main.py                 # エントリーポイント
│   ├── config.py               # 設定管理
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── client.py           # Discord Botクライアント
│   │   ├── channel_handler.py  # チャンネル処理
│   │   ├── action_buttons.py   # ボタンUI
│   │   ├── reminder.py         # リマインド機能
│   │   └── scheduler.py        # スケジューラー
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── transcription.py    # 音声文字起こし
│   │   ├── prompts.py          # プロンプト定義
│   │   ├── structured_extraction.py  # 構造化データ抽出
│   │   ├── question_generation.py    # 質問生成
│   │   ├── auto_decision.py    # AI自動判断
│   │   ├── date_extraction.py  # 日付抽出
│   │   └── relation_detection.py     # 関連性判定
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── obsidian_manager.py       # Obsidian読み書き・検索
│   │   ├── markdown_templates.py     # Markdownテンプレート
│   │   ├── auto_linking.py     # 自動リンク生成
│   │   └── git_manager.py      # Git操作
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── weekly_review.py    # 週次レビュー
│   │   ├── comparison.py       # 過去と比較
│   │   ├── contradiction_detection.py # 矛盾検出
│   │   ├── statistics.py       # 統計
│   │   └── pattern_analysis.py # パターン分析
│   ├── search/
│   │   ├── __init__.py
│   │   ├── keyword_search.py   # キーワード検索
│   │   └── vector_search.py    # ベクトル検索（Phase 4）
│   └── models/
│       ├── __init__.py
│       ├── memo.py             # Memoモデル
│       └── user.py             # Userモデル
├── tests/
│   ├── test_bot/
│   ├── test_ai/
│   ├── test_storage/
│   └── test_analysis/
├── docs/
│   └── improvements/           # このドキュメント群
├── obsidian-vault/             # Obsidian Vault（出力先）
├── .env                        # 環境変数
├── .env.example                # 環境変数のサンプル
├── requirements.txt
└── README.md
```

---

## requirements.txt

```txt
# Discord
discord.py==2.3.2

# Google Gemini
google-generativeai==0.3.2

# HTTP
aiohttp==3.9.1

# スケジューラー
apscheduler==3.10.4

# Markdown/YAML処理
python-dotenv==1.0.0
pyyaml==6.0.1
```

---

## 次のドキュメント

- [data-structures.md](data-structures.md) - データ構造
