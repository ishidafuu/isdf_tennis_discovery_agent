# Tennis Discovery Agent - 実装計画

最終更新: 2025-11-28

---

## Phase 1: 記録の構造化（基礎機能）

**全体進捗: 20/20 タスク完了 (100%)** ✅

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

**全体進捗: 0/6 タスク完了 (0%)**

### 3.1 ベクトル検索
- [ ] 埋め込みベクトル生成（Gemini Embedding）
- [ ] ベクトルデータベース構築（Chroma / Qdrant）
- [ ] 感覚検索UI実装

### 3.2 パターン分析
- [ ] 好調時の共通パターン抽出
- [ ] 不調時の傾向分析
- [ ] 週次・月次トレンド可視化

### 3.3 リマインド機能（高度版）
- [ ] コンテキストベースのリマインド
- [ ] 前回の課題＋関連する過去の成功体験を提示
- [ ] タイミング最適化（練習前、練習後）

---

## Phase 4: 拡張機能（将来構想）

**全体進捗: 0/? タスク完了 (0%)**

### 4.1 マルチユーザー対応
- [ ] ユーザー識別機能
- [ ] プライバシー管理
- [ ] データ分離

### 4.2 外部サービス連携
- [ ] Notion連携
- [ ] Google Calendar連携
- [ ] Apple Health連携（運動データ）

### 4.3 データエクスポート
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
