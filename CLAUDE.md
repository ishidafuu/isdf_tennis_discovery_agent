# Tennis Discovery Agent

## 概要

自律的な上達を支援する「第2の脳」。Discord + Gemini AI + Obsidianを連携し、音声メモから構造化された練習記録を生成。「仮説・実行・検証」のサイクルを回し、ユーザーの上達を支援する。

## 技術スタック

- **フロントエンド**: Discord Bot（音声入力）
- **AI処理**: Google Gemini 2.5 Flash API（文字起こし・構造化抽出）
- **ストレージ**: Obsidian Vault（Markdown形式）、GitHub（バージョン管理）
- **言語**: Python 3
- **主要ライブラリ**: discord.py, google-generativeai
- **インフラ**: Raspberry Pi（本番環境）

## ディレクトリ構造

- `src/bot/` - Discord Bot メインロジック、チャンネル・シーン検出
- `src/ai/` - Gemini API処理、プロンプト、構造化データ抽出
- `src/storage/` - Markdown生成、GitHub連携、Obsidian管理
- `src/models/` - データモデル（PracticeSession）
- `docs/` - プロジェクトドキュメント（3カテゴリ：開発・セットアップ・使い方）
  - `docs/開発/` - 要件・仕様・技術詳細（開発者向け）
  - `docs/セットアップ/` - 初回セットアップ手順
  - `docs/使い方/` - エンドユーザー向けガイド
- `tests/` - テストコード

## 重要なコマンド

```bash
# 開発環境（Mac）
source venv/bin/activate
python main.py

# セットアップ確認
python check_setup.py

# dotenvx関連（Mac）
dotenvx encrypt -f .env                 # 環境変数を暗号化
dotenvx get VARIABLE_NAME               # 環境変数を確認
dotenvx run -- python main.py           # 復号化して実行

# デプロイ（Mac → Raspberry Pi）
pi-deploy-tennis-bot                    # デプロイスクリプト実行

# サービス管理（Raspberry Pi本番環境）
sudo systemctl start tennis-bot         # サービス起動
sudo systemctl status tennis-bot        # ステータス確認
sudo systemctl restart tennis-bot       # 再起動
sudo journalctl -u tennis-bot -f        # ログをリアルタイム表示

# GitHub同期
cd ~/obsidian-vault
git add .
git commit -m "Update practice logs"
git push origin main
```

## Discordチャンネル構成

- `#壁打ち` - 壁打ち練習の記録
- `#スクール` - スクール練習の記録
- `#試合` - 試合の記録
- `#フリー練習` - フリー練習の記録
- `#振り返り` - 後日の追記・補足（あいまい検索で過去メモに追記）

## コーディング規約

- **型ヒント必須**: 関数シグネチャに型アノテーションを使用
- **エラーハンドリング徹底**: try-exceptでAPIエラー、ファイル操作エラーを捕捉
- **ログ出力**: 重要な処理には logging を使用（本番環境でのデバッグ用）
- **非同期処理**: Discord Bot関連は async/await パターン
- **環境変数**: 機密情報（APIキー等）は .env で管理、絶対にコミットしない

## アーキテクチャ原則

### コアフィロソフィー
1. **Voice First**: 練習現場でのUXを最優先、手入力ではなく音声中心
2. **Cycle Oriented**: 前回→今回→次回の「線」の管理
3. **No Teaching, But Coaching**: 答えを教えず、問いかけで気づきを引き出す

### ファイル命名規則
- **練習メモ**: `YYYY-MM-DD-HHMMSS-シーン名.md`（タイムスタンプで一意性保証）
- **画像・動画**: `attachments/{date}/YYYY-MM-DD_シーン名_HHMMSS.ext`

### Git LFS管理対象
- 画像: jpg, jpeg, png, gif
- 動画: mp4, mov, avi, webm
- 音声: ogg, mp3, wav, m4a, opus

---

## ★ 自律行動ルール（重要）

### タスク完了時（自動実行）

実装・修正・テストが完了したと判断したら、**指示を待たずに以下を実行**：

1. **`docs/plan.md` の該当タスクを `[x]` に更新**
2. **`docs/session-log.md` に追記**（フォーマット例は下記）
3. **重要な設計判断・アーキテクチャ変更**があれば `CLAUDE.md` の「最近の変更」セクションに追記
4. **完了報告**と「`/clear` → `/start` で次へ」を提案

#### session-log.md への記録フォーマット

```markdown
## YYYY-MM-DD HH:MM
**完了**: [タスク名]
**変更ファイル**: src/xxx/yyy.py, tests/test_zzz.py
**次回の作業**: [次に取り組むべきタスク]
**備考**: [技術的な決定事項、制約、重要なコンテキスト]
```

### 完了の判断基準

以下をすべて満たす場合、タスクを完了とみなす：
- 要求機能が実装された
- 関連するテストが通った（または手動で動作確認済み）
- エラーなく動作確認済み
- コードレビュー可能な状態（型ヒント、エラーハンドリング、ログ出力が適切）

### 終了の兆候を検知した場合

ユーザーが以下のようなメッセージを送信したら、**終了処理を実行**：
- 「ありがとう」「OK」「了解」「おつかれさま」
- 「今日はここまで」「一旦終了」
- その他、明確に終了を示唆する発言

**終了処理内容:**
1. 上記の「タスク完了時」処理を実行
2. 現在の進捗状況をサマリーとして報告
3. 次回セッションで取り組むべきタスクを提案
4. 「次回 `/start` で再開できます」と明示

### 中断時（未完了のまま終了する場合）

タスクが完了していない状態で中断する場合は、`docs/session-log.md` に以下を記録：

```markdown
## YYYY-MM-DD HH:MM （中断）
**作業中**: [タスク名]
**現在の状態**: [どこまで進んだか、何が完了/未完了か]
**次回再開時のポイント**: [続きから再開するための重要な情報]
**ブロッカー**: [あれば。待ちが発生している要因など]
```

---

## 最近の変更

### 2025-11-27
- **ObsidianManager実装**: ファイル検索・あいまい検索・追記機能を追加（`src/storage/obsidian_manager.py`）
- **振り返りチャンネル機能**: `#振り返り`チャンネルで過去メモに追記可能に（日付・キーワード抽出）
- **前回ログ読み込み**: 同一シーンの最新メモを自動取得し、Discord応答に「🔄 サイクル」セクション表示
- **画像・動画メモ機能**: 20MB制限、Git LFS管理、Obsidian埋め込み（`![[filepath]]`）
- **Git LFS セットアップ**: `.gitattributes` でメディアファイルを管理

### 2025-11-28
- **プロジェクト管理構造の導入**: CLAUDE.md、docs/plan.md、docs/session-log.md、カスタムコマンド（/start, /status）を追加し、大規模プロジェクトの管理効率を向上

### 2025-12-11
- **dotenvx導入**: 環境変数の暗号化管理を実装。`.env`を暗号化してGitにコミット可能に
- **デプロイメント構造**: `deployment/scripts/`にラズパイセットアップとデプロイスクリプトを追加
- **systemdサービステンプレート**: dotenvxと統合したサービスファイルを`deployment/systemd/`に配置
- **ドキュメント整備**: `docs/DOTENVX_SETUP.md`、`docs/QUICKSTART_DOTENVX.md`を追加
- **.gitignore更新**: `.env.keys`を除外リストに追加してセキュリティ強化

### 2025-12-12
- **ドキュメント構造の大幅再編成**: 3カテゴリ（開発・セットアップ・使い方）に分類
  - `docs/開発/` - 開発者向け要件・仕様・技術詳細
  - `docs/セットアップ/` - 初回セットアップ手順
  - `docs/使い方/` - エンドユーザー向けガイド
- **ファイル名の日本語化**: ドキュメントファイルを日本語名に統一（例: `使い方ガイド.md` → `基本的な使い方.md`）
- **インデックスファイル更新**: `docs/index.md`、各カテゴリの`index.md`を新構造に対応
- **README.md更新**: 新しいドキュメント構造へのリンクを更新
- **環境変数の分離**: 機密情報（`.env`）と非機密情報（`.env.config`）を分離
  - `.env` - 機密情報のみ（dotenvxで暗号化）
  - `.env.config` - 非機密情報（平文でGitコミット可能）
  - `src/config.py` - 両ファイルを読み込むように更新
  - `scripts/migrate_env_config.sh` - 移行スクリプトを追加

---

## 技術的制約・既知の問題

### Git LFS容量制限
- GitHub無料枠: 1GB/月のデータ転送
- 画像・動画を頻繁に投稿すると3-6ヶ月で容量オーバーの可能性
- 対策: Git LFS追加購入（$5/月で50GB）または画像圧縮

### Gemini API制限
- Gemini 2.5 Flash: 無料枠 1,500リクエスト/日
- 音声文字起こし + 構造化抽出で2リクエスト/メモ
- 1日750メモまで処理可能（実運用では十分）

### Raspberry Pi性能
- Raspberry Pi 3: 1GB RAM、処理速度やや遅い
- 推奨: Raspberry Pi 4以上（2GB RAM以上）
- ネットワーク経由のAPI呼び出しがボトルネック（ローカル処理は軽量）

---

## セキュリティ注意事項

### dotenvx導入後の環境変数管理

#### ファイル構成
- **`.env`** - 機密情報のみ（dotenvxで暗号化してGitにコミット）
  - `DISCORD_BOT_TOKEN`
  - `GEMINI_API_KEY`
  - `GITHUB_TOKEN`
- **`.env.config`** - 非機密情報（平文でGitにコミット可能）
  - `GITHUB_REPO`
  - `OBSIDIAN_PATH`
  - `OBSIDIAN_VAULT_PATH`
  - `ADMIN_USER_ID`
  - `DEBUG`
  - その他アプリケーション設定
- **`.env.keys`** - 暗号化キー（**絶対にコミット禁止**、`.gitignore`で除外済み）

#### セキュリティルール
- **暗号化された `.env`** をGitにコミット（平文の.envはコミット禁止）
- **`.env.keys` ファイル**を絶対にGitにコミットしない
- **`.env.keys`のパーミッション**を`600`に設定（所有者のみ読み書き可能）
- **プライベートリポジトリ**で運用（練習内容は個人情報）
- **Obsidian Vault**の GitHub リポジトリもプライベート推奨
- **鍵のローテーション**: 年1回程度、新しい鍵で再暗号化を推奨

---

## 参考ドキュメント

### 開発者向け
- **ドキュメント索引**: `docs/index.md`
- **Phase 1全体**: `docs/開発/フェーズ/01-基盤強化/index.md`
- **実装ステータス**: `docs/開発/実装状況.md`
- **プロジェクト計画**: `docs/開発/plan.md`
- **開発ログ**: `docs/開発/session-log.md`
- **アーキテクチャ**: `docs/開発/概要/アーキテクチャ.md`
- **技術詳細**: `docs/開発/技術/`

### セットアップ
- **セットアップガイド**: `SETUP.md`
- **クイックスタート**: `docs/セットアップ/クイックスタート.md`
- **dotenvxクイックスタート**: `docs/セットアップ/dotenvxクイックスタート.md`
- **dotenvx詳細ガイド**: `docs/セットアップ/dotenvx設定.md`
- **Discordボット設定**: `docs/セットアップ/Discordボット.md`
- **Raspberry Pi設定**: `docs/セットアップ/RaspberryPi.md`

### ユーザー向け
- **基本的な使い方**: `docs/使い方/基本的な使い方.md`
- **ストーリーガイド**: `docs/使い方/ストーリーガイド.md`
- **機能一覧**: `docs/使い方/機能一覧.md`
- **コマンドリファレンス**: `docs/使い方/リファレンス/コマンド.md`
