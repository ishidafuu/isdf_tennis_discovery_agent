# Tennis Discovery Agent - 実装計画

最終更新: 2025-12-11

---

## Phase 1: 記録の構造化（基礎機能）

**全体進捗: 32/32 タスク完了 (100%)** ✅

### 1.1 基礎機能
- [x] チャンネル分け機能（#壁打ち、#スクール、#試合、#フリー練習、#振り返り）
- [x] シーン別プロンプト・構造化データ抽出
- [x] シーン別Markdownテンプレート
- [x] ファイル名重複バグ修正（タイムスタンプ追加）

### 1.2 マルチモーダル入力
- [x] 音声メモ機能（Gemini 2.5 Flash文字起こし）
- [x] テキストメモ機能（URL自動検出、コマンド除外）
- [x] 画像メモ機能（20MB制限、Obsidian埋め込み）
- [x] 動画メモ機能（20MB制限、Git LFS管理）

### 1.3 ファイル管理
- [x] ObsidianManager実装
  - [x] get_latest_memo() - 最新メモ取得
  - [x] get_memos_in_range() - 期間内メモ取得
  - [x] search_by_keyword() - キーワード検索
  - [x] search_by_date() - 日付検索
  - [x] get_memo_by_tags() - タグ検索
  - [x] find_memo_by_fuzzy_criteria() - あいまい検索
  - [x] append_to_memo() - メモ追記
- [x] Git LFSセットアップ（.gitattributes）

### 1.4 サイクル追跡機能
- [x] 前回ログ読み込み機能（同一シーンの最新メモ自動取得）
- [x] Discord応答に「🔄 サイクル」セクション表示

### 1.5 振り返り機能
- [x] #振り返りチャンネル実装（あいまい検索・自動追記）

### 1.6 環境設定
- [x] 環境変数追加（OBSIDIAN_VAULT_PATH、ADMIN_USER_ID）

### 1.7 スケジューラー・テスト機能
- [x] Discord DM処理（Bot停止時バックアップ）
- [x] Phase 1全機能の統合テスト
- [x] 週次レビュー自動生成機能
- [x] 練習開始時リマインド機能

### 1.8 Discord返信による追記機能
- [x] AI解析・整形機能（`src/ai/deepening_analysis.py`）
- [x] 返信ハンドラー（`src/bot/handlers/reply_handler.py`）
- [x] MessageID記録機能（全メモにdiscord_message_idを記録）
- [x] ObsidianManager拡張（`find_memo_by_discord_id()`, `update_memo_frontmatter()`）
- [x] client.py統合（返信検知の優先処理）

### 1.9 まとめページ自動生成機能
- [x] データ収集モジュール（`src/storage/summary_generator.py`）
- [x] AI生成用プロンプト（`src/ai/summary_prompts.py`）
- [x] スケジューラー統合（毎日深夜3時に自動実行）
- [x] 6種類のまとめページ生成
  - [x] まとめ_総合.md（練習前チェック用）
  - [x] まとめ_最近.md（直近2週間）
  - [x] まとめ_1ヶ月.md（過去1ヶ月）
  - [x] まとめ_フォアハンド.md（フォアハンド全記録）
  - [x] まとめ_バックハンド.md（バックハンド全記録）
  - [x] まとめ_サーブ.md（サーブ全記録）

---

## Phase 2: 対話の深化

**全体進捗: 8/8 タスク完了 (100%)** ✅

### 2.1 質問生成機能
- [x] ソクラテス式問答の実装 (`src/ai/question_generation.py`)
- [x] シーン別質問テンプレート
- [x] ユーザー応答の解析

### 2.2 深堀り機能
- [x] ボタンインターフェース実装（「もっと詳しく」等） (`src/bot/action_buttons.py`)
- [x] 対話履歴の管理 (`ConversationManager`)
- [x] 感覚の言語化支援

### 2.3 コーチング機能
- [x] 気づきを促す質問生成
- [x] 過去の成功体験の提示 (`src/analysis/comparison.py`)
- [x] 課題の明確化サポート (`src/analysis/contradiction_detection.py`)

### 2.4 #質問チャンネル
- [x] 自由な質問への応答 (`src/bot/question_handler.py`)
- [x] 過去メモの検索・要約
- [x] コンテキストを考慮した回答生成

---

## Phase 3: 資産の活用

**全体進捗: 10/10 タスク完了 (100%)** ✅

### 3.1 感覚検索機能
- [x] 感覚表現の類義語辞書（シュッ、ガツン、ふわっなど）
- [x] キーワード展開検索（類義語による柔軟な検索）
- [x] 検索結果のスコアリング（関連度順にソート）

### 3.2 自動リンク生成
- [x] タグベースのリンク生成（関連メモを自動接続）
- [x] 日付ベースの前後リンク（練習の流れを可視化）
- [x] バックリンク管理（既存メモへのリンク追加）

### 3.3 統計・グラフ機能
- [x] 月次・週次統計計算（練習頻度、シーン別、タグ別）
- [x] Obsidian Charts連携（週別・月別・シーン別グラフ）
- [x] 練習トレンド分析（増加・減少・安定の判定）

### 3.4 リマインド機能強化
- [x] 課題進捗確認機能（未解決の課題を検出）
- [x] 課題の解決判定（後続メモから自動判定）

### 3.5 #分析チャンネル
- [x] 期間検出機能（今週、今月、3ヶ月など）
- [x] メモ分析機能（AI による成長分析）
- [x] 分析レポート生成（整形されたMarkdown出力）

---

## Phase 4: 高度な分析

**全体進捗: 10/10 タスク完了 (100%)** ✅

### 4.1 Embedding生成機能
- [x] Gemini Embedding APIの統合 (`src/search/embedding.py`)
- [x] get_embedding() - テキストのEmbedding化
- [x] batch_embed_texts() - バッチ処理
- [x] embed_memo_content() - メモからのEmbedding生成

### 4.2 ベクトルDB統合
- [x] Chromaのセットアップ (`src/search/vector_search.py`)
- [x] add_memo() / update_memo() / delete_memo()
- [x] search_similar_memos() - 意味検索
- [x] メタデータフィルタリング

### 4.3 パターン分析機能
- [x] 好調/不調パターンの抽出 (`src/analysis/pattern_analysis.py`)
- [x] 時系列分析（月次トレンド）
- [x] ターニングポイントの特定
- [x] 相関分析

### 4.4 予測・提案機能
- [x] 成長予測 (`src/analysis/prediction.py`)
- [x] 練習メニュー生成
- [x] コンディション予測
- [x] 次の技術推奨

### 4.5 バッチ処理スクリプト
- [x] 既存メモのバッチEmbedding処理 (`scripts/batch_embed_memos.py`)

### 4.6 テストコード
- [x] tests/search/test_embedding.py（8件のテスト）
- [x] tests/search/test_vector_search.py（7件のテスト）
- [x] tests/analysis/test_pattern_analysis.py（7件のテスト）
- [x] tests/analysis/test_prediction.py（8件のテスト）

---

## Phase 5: 拡張機能（将来構想）

**全体進捗: 0/? タスク完了 (0%)**

### 5.1 マルチユーザー対応
- [ ] ユーザー識別機能
- [ ] プライバシー管理
- [ ] データ分離

### 5.2 外部サービス連携
- [ ] Notion連携
- [ ] Google Calendar連携
- [ ] Apple Health連携（運動データ）

### 5.3 データエクスポート
- [ ] PDF出力機能
- [ ] CSV/JSON出力
- [ ] 分析レポート生成

---

## 優先順位付きタスクリスト（次に取り組むべきもの）

### 🔴 高優先度（Phase 1完了に必須）
1. **Discord DM処理の実装** `docs/improvements/phases/01-foundation/input.md:362-421`
   - Bot停止時の音声・画像・動画メッセージをバックアップ
   - ✅リアクションで処理済みマーク
   - シーン情報をメッセージ本文から抽出

2. **Phase 1統合テスト** `tests/integration/test_phase1.py`（新規作成）
   - 音声・テキスト・画像・動画メモの動作確認
   - 前回ログ表示の検証
   - 振り返りチャンネルのテスト
   - Git LFS動作確認

### 🟡 中優先度（Phase 1オプション）
3. **週次レビュー自動生成** `src/scheduler/weekly_review.py`（新規作成）
   - APScheduler導入
   - 毎週日曜日夜に過去1週間のメモを集約
   - Geminiで週次サマリー生成

### 🟢 低優先度（Phase 2以降でも可）
4. **練習開始時リマインド機能** `src/scheduler/reminders.py`（新規作成）
   - 曜日・時間ベースのリマインダー
   - 前回の課題を含めたリマインド

---

## 完了基準

### Phase 1完了条件
- ✅ マルチモーダル入力（音声・テキスト・画像・動画）
- ✅ シーン別処理（壁打ち・スクール・試合・フリー練習）
- ✅ サイクル追跡（前回→今回→次回）
- ✅ 振り返り機能
- ✅ DM処理（Bot停止時バックアップ）
- ✅ 統合テスト完了
- ✅ 週次レビュー
- ✅ リマインダー

**現状: Phase 1 完了！🎉 全機能100%実装済み**

---

## 参考ドキュメント

- **実装ステータス**: `docs/improvements/IMPLEMENTATION_STATUS.md`
- **Phase 1全体**: `docs/improvements/phases/01-foundation/index.md`
- **入力機能**: `docs/improvements/phases/01-foundation/input.md`
- **処理機能**: `docs/improvements/phases/01-foundation/processing.md`
- **出力機能**: `docs/improvements/phases/01-foundation/output.md`
- **クイックスタート**: `docs/improvements/QUICKSTART.md`
