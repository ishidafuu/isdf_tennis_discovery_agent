# Tennis Discovery Agent - 機能一覧

最終更新: 2025-11-29

このドキュメントは、現在実装されている全機能を整理したものです。

---

## 📋 目次

- [Phase 1: 記録の構造化](#phase-1-記録の構造化)
- [Phase 2: 対話の深化](#phase-2-対話の深化)
- [Phase 3: 資産の活用](#phase-3-資産の活用)
- [Phase 4: 高度な分析](#phase-4-高度な分析)
- [利用可能なDiscordチャンネル](#利用可能なdiscordチャンネル)
- [ファイル構成](#ファイル構成)

---

## Phase 1: 記録の構造化

**目的**: 音声・テキスト・画像・動画から構造化された練習記録を生成

### 1.1 マルチモーダル入力

| 入力形式 | 処理内容 | 実装ファイル |
|---------|---------|------------|
| **音声メモ** | Gemini 2.5 Flashで文字起こし → 構造化データ抽出 | `src/bot/handlers/message_handler.py` |
| **テキストメモ** | URL自動検出、構造化データ抽出 | `src/bot/handlers/message_handler.py` |
| **画像** | 20MB制限、Obsidian埋め込み (`![[画像]]`) | `src/bot/handlers/message_handler.py` |
| **動画** | 20MB制限、Git LFS管理、Obsidian埋め込み | `src/bot/handlers/message_handler.py` |

### 1.2 シーン別処理

各チャンネルごとに異なるプロンプトと構造化抽出を実行：

| シーン | 抽出データ | プロンプト |
|--------|----------|-----------|
| **壁打ち** | 練習メニュー、感覚、課題、次回テーマ | `src/ai/prompts.py` |
| **スクール** | コーチ指導、練習内容、気づき | `src/ai/prompts.py` |
| **試合** | 対戦相手、戦術、勝因/敗因、メンタル | `src/ai/prompts.py` |
| **フリー練習** | 練習相手、練習内容、発見 | `src/ai/prompts.py` |

**実装**: `src/ai/structured_extraction.py`

### 1.3 サイクル追跡

- **前回ログ自動読み込み**: 同一シーンの最新メモを自動取得
- **Discord応答に表示**: `🔄 サイクル`セクションで前回の課題を表示
- **継続性の可視化**: 前回 → 今回 → 次回の流れを管理

**実装**: `src/bot/helpers/previous_log.py`

### 1.4 振り返り機能

`#振り返り`チャンネルで過去メモに追記：

- **日付抽出**: 「11月27日」「先週の水曜日」などを自動検出
- **キーワード検索**: 「サーブ」「壁打ち」などで関連メモを検索
- **あいまい検索**: 複数候補がある場合はリスト表示
- **追記**: 選択したメモに「## 振り返り」セクションを追加

**実装**: `src/storage/obsidian_manager.py`, `src/bot/handlers/message_handler.py`

### 1.5 DM処理

Bot停止時に送信された音声・画像・動画を後で処理：

- **未読DM検出**: Bot起動時に未処理DMをチェック
- **バックアップ処理**: ✅リアクションで処理済みマーク
- **シーン指定**: DMの本文に「壁打ち」等を記載

**実装**: `src/bot/handlers/dm_handler.py`

### 1.6 ファイル管理

- **命名規則**: `YYYY-MM-DD-HHMMSS-シーン名.md` (タイムスタンプで一意性保証)
- **画像・動画**: `attachments/{date}/YYYY-MM-DD_シーン名_HHMMSS.ext`
- **Git LFS**: 画像・動画を自動管理 (`.gitattributes`)
- **GitHub連携**: Markdownファイルを自動コミット&プッシュ

**実装**: `src/storage/github_manager.py`, `src/bot/helpers/markdown_helpers.py`

---

## Phase 2: 対話の深化

**目的**: 単なる記録ではなく、気づきを引き出す対話

### 2.1 ソクラテス式問答

答えを教えるのではなく、問いかけによって気づきを促す：

- **質問生成**: 練習内容から深掘りする質問を自動生成
- **感覚の言語化**: 「どう感じたか」「身体のどこを意識したか」を引き出す
- **シーン別質問**: 各シーンに適した質問テンプレート

**実装**: `src/ai/question_generation.py`

### 2.2 ボタンインターフェース

Discord Botのボタンで対話を継続：

| ボタン | 機能 | 実装 |
|--------|------|------|
| **🔍 もっと詳しく** | 成功パターンや失敗の詳細を深掘り | `src/bot/action_buttons.py` |
| **📊 過去と比較** | 類似の過去メモと比較分析 | `src/analysis/comparison.py` |
| **💾 記録を保存** | 現在の対話内容をObsidianに保存 | `src/bot/action_buttons.py` |

### 2.3 AIの自動判断

ユーザーの入力に応じて、AIが次のアクションを自動判断：

- **深掘り**: 曖昧な表現や重要な気づきがある場合
- **比較**: 過去の類似体験と比較すべき場合
- **保存**: 十分な情報が集まった場合

**実装**: `src/ai/auto_decision.py`

### 2.4 #質問チャンネル

過去の記録から質問に回答：

- **キーワード検索**: タグ、日付、シーンから関連メモを検索
- **要約・回答**: Geminiが過去メモを要約して回答
- **コンテキスト考慮**: ユーザーの練習履歴を考慮した回答

**実装**: `src/bot/question_handler.py`

### 2.5 矛盾・変化の検出

練習記録の変化や矛盾を自動検出：

- **意見の変化**: 以前と異なる見解を検出
- **技術の進化**: 同じ技術への言及の変化を追跡
- **気づきの提示**: 変化をユーザーに通知

**実装**: `src/analysis/contradiction_detection.py`

---

## Phase 3: 資産の活用

**目的**: 蓄積されたデータを活用し、価値を引き出す

### 3.1 感覚検索

類義語辞書を使った柔軟な検索：

| 感覚表現 | 類義語 |
|---------|--------|
| シュッ | サッ、スパッ、バシッ |
| ガツン | ドン、バン、ズシッ |
| ふわっ | ポワン、フワリ、ソフト |

**実装**: `src/search/sensation_search.py`

### 3.2 自動リンク生成

Obsidian内でメモを自動的に関連付け：

- **タグベースリンク**: 同じタグを持つメモを自動リンク
- **日付ベースリンク**: 前後の練習メモへのリンク
- **バックリンク管理**: 既存メモへのリンク追加

**実装**: `src/storage/auto_linking.py`

### 3.3 統計・グラフ機能

Obsidian Chartsプラグインと連携したグラフ生成：

- **月次統計**: 練習頻度、シーン別、タグ別
- **週次統計**: 7日間の練習トレンド
- **トレンド分析**: 増加・減少・安定を自動判定

**実装**: `src/analysis/statistics.py`

### 3.4 課題進捗確認

未解決の課題を自動追跡：

- **課題検出**: `next_actions`や`issues`から抽出
- **解決判定**: 後続メモから自動判定
- **リマインド**: 未解決課題をDMで通知

**実装**: `src/scheduler/reminders.py`

### 3.5 #分析チャンネル

期間を指定してAI分析レポートを生成：

- **期間検出**: 「今週」「今月」「3ヶ月」等を自動認識
- **メモ集計**: 指定期間のメモを収集
- **AI分析**: Geminiが成長分析レポートを生成
- **Markdown出力**: 整形されたレポートを返信

**実装**: `src/bot/analysis_handler.py`

---

## Phase 4: 高度な分析

**目的**: AIの真価を発揮し、意味的な分析と予測を実現

### 4.1 Embedding生成

テキストをベクトル化して意味を数値表現：

| 機能 | 説明 | API |
|------|------|-----|
| **get_embedding()** | テキスト → ベクトル変換 | Gemini text-embedding-004 |
| **batch_embed_texts()** | 複数テキストの一括変換 | レート制限対応 |
| **embed_memo_content()** | メモデータ → ベクトル | 要約・タグ・課題を統合 |

**実装**: `src/search/embedding.py`

**コスト**: 月100メモで約1円（非常に安価）

### 4.2 ベクトル検索

キーワードではなく、意味で検索：

| 機能 | 説明 |
|------|------|
| **search_similar_memos()** | 意味的類似性で検索 |
| **メタデータフィルタ** | シーン・日付・タグで絞り込み |
| **コサイン類似度** | 類似度スコア付きで結果を返す |

**実装**: `src/search/vector_search.py`

**技術**: ChromaDB (ローカル、無料)

### 4.3 パターン分析

AIによる自動パターン発見：

| 機能 | 説明 |
|------|------|
| **extract_condition_patterns()** | 好調時と不調時のパターンを抽出 |
| **analyze_time_series()** | 時系列でのトレンド分析 |
| **find_turning_points()** | 成長のターニングポイントを検出 |
| **analyze_correlations()** | 2つの指標の相関を分析 |

**実装**: `src/analysis/pattern_analysis.py`

### 4.4 予測・提案

将来の成長を予測し、提案を生成：

| 機能 | 説明 |
|------|------|
| **predict_growth()** | 今後の成長を予測 |
| **suggest_practice_menu()** | 練習メニューを自動生成 |
| **predict_condition()** | コンディションを予測 |
| **recommend_next_skill()** | 次に取り組むべき技術を推奨 |

**実装**: `src/analysis/prediction.py`

### 4.5 バッチ処理

既存の全メモをベクトル化：

```bash
python scripts/batch_embed_memos.py
```

- Obsidian Vaultの全Markdownファイルをスキャン
- メタデータを自動抽出（日付、シーン、タグ）
- Embeddingを生成してChromaDBに保存

**実装**: `scripts/batch_embed_memos.py`

---

## 利用可能なDiscordチャンネル

| チャンネル | 用途 | 主な機能 |
|-----------|------|---------|
| **#壁打ち** | 壁打ち練習の記録 | 音声・テキスト・画像・動画メモ |
| **#スクール** | スクール練習の記録 | コーチの指導内容を記録 |
| **#試合** | 試合の記録 | 対戦相手、戦術、勝因/敗因 |
| **#フリー練習** | フリー練習の記録 | 練習相手との自由練習 |
| **#振り返り** | 過去メモへの追記 | 日付・キーワードで検索して追記 |
| **#質問** | 過去記録からの質問応答 | 蓄積データを検索・要約 |
| **#分析** | 期間指定でAI分析 | 今週/今月/3ヶ月の成長分析 |

---

## ファイル構成

### コアモジュール

```
src/
├── ai/                          # AI処理
│   ├── gemini_client.py         # Gemini API クライアント
│   ├── structured_extraction.py # 構造化データ抽出
│   ├── prompts.py               # シーン別プロンプト
│   ├── question_generation.py   # ソクラテス式質問生成
│   └── auto_decision.py         # AI自動判断
│
├── bot/                         # Discord Bot
│   ├── client.py                # Bot メインクライアント
│   ├── channel_handler.py       # チャンネル別ルーティング
│   ├── question_handler.py      # #質問チャンネル処理
│   ├── analysis_handler.py      # #分析チャンネル処理
│   ├── action_buttons.py        # ボタンインターフェース
│   ├── handlers/
│   │   ├── message_handler.py   # メッセージ処理（音声・テキスト・画像・動画）
│   │   └── dm_handler.py        # DM処理
│   └── helpers/
│       ├── media_utils.py       # メディアファイル判定
│       ├── markdown_helpers.py  # Markdown生成・GitHub push
│       └── previous_log.py      # 前回ログ取得
│
├── storage/                     # ストレージ管理
│   ├── obsidian_manager.py      # Obsidian Vault管理
│   ├── github_manager.py        # GitHub連携
│   └── auto_linking.py          # 自動リンク生成
│
├── search/                      # 検索機能
│   ├── sensation_search.py      # 感覚検索（類義語）
│   ├── embedding.py             # Embedding生成
│   └── vector_search.py         # ベクトル検索（ChromaDB）
│
├── analysis/                    # 分析機能
│   ├── comparison.py            # 過去メモ比較
│   ├── contradiction_detection.py # 矛盾・変化検出
│   ├── statistics.py            # 統計・グラフ
│   ├── pattern_analysis.py      # パターン分析
│   └── prediction.py            # 予測・提案
│
├── scheduler/                   # スケジューラー
│   ├── weekly_review.py         # 週次レビュー自動生成
│   └── reminders.py             # 課題リマインド
│
└── models/                      # データモデル
    └── session.py               # PracticeSession モデル
```

### スクリプト

```
scripts/
└── batch_embed_memos.py         # 既存メモの一括Embedding化
```

### テスト

```
tests/
├── ai/                          # AI機能のテスト
├── bot/                         # Bot機能のテスト
├── storage/                     # ストレージのテスト
├── search/                      # 検索機能のテスト
├── analysis/                    # 分析機能のテスト
└── scheduler/                   # スケジューラーのテスト
```

---

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| **AI処理** | Google Gemini 2.5 Flash |
| **Embedding** | Gemini text-embedding-004 |
| **ベクトルDB** | ChromaDB (ローカル) |
| **フロントエンド** | Discord Bot (discord.py) |
| **ストレージ** | Obsidian Vault (Markdown) |
| **バージョン管理** | GitHub (Git LFS対応) |
| **言語** | Python 3.11+ |
| **インフラ** | Raspberry Pi (本番環境) |

---

## 完了状況

| Phase | タスク数 | 進捗 |
|-------|---------|------|
| Phase 1: 記録の構造化 | 20 | ✅ 100% |
| Phase 2: 対話の深化 | 8 | ✅ 100% |
| Phase 3: 資産の活用 | 10 | ✅ 100% |
| Phase 4: 高度な分析 | 10 | ✅ 100% |
| **合計** | **48** | **✅ 100%** |

---

## 参考ドキュメント

- **実装計画**: `docs/plan.md`
- **セッションログ**: `docs/session-log.md`
- **セットアップガイド**: `SETUP.md`
- **プロジェクト管理**: `CLAUDE.md`
- **Phase別詳細**: `docs/improvements/phases/*/`
