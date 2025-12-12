# 🎾 Tennis Discovery Agent

**自律的な上達を支援する「第2の脳」**

Discord + Gemini AI + Obsidianを連携し、音声メモから構造化された練習記録を生成。意味的検索、パターン分析、成長予測により、テニスの上達を科学的にサポートします。

## ✨ 主な機能

- 🎤 **音声・画像・動画メモ**: Discordから音声を送信するだけで、Gemini AIが自動文字起こし・構造化
- 🔄 **サイクル追跡**: 前回の課題 → 今回の実行 → 次回のテーマを自動管理
- 💬 **ソクラテス式対話**: 答えを教えず、問いかけで気づきを引き出す
- 🔍 **意味検索**: キーワードではなく、意味で過去の記録を検索（ベクトル検索）
- 📊 **AI分析**: 好調/不調パターン、成長トレンド、ターニングポイントを自動検出
- 🎯 **予測・提案**: 成長予測、練習メニュー生成、コンディション予測

## 🎯 プロジェクトの目的

単なる練習記録の保存ではなく、「仮説・実行・検証」のサイクルを回し、ユーザーの自律的な上達を支援する。特に「身体感覚（Somatic Marker）」の言語化と蓄積に重点を置き、スランプやイップス時の回復の拠り所となる「第2の脳」を構築する。

## 💡 コア・フィロソフィー

- **No Teaching, But Coaching**: 答えを教えるのではなく、問いかけによってユーザー自身の気づきを引き出す（ソクラテス式問答）
- **Voice First**: 練習現場でのUXを最優先し、手入力ではなく「会話（音声）」を中心にする
- **Cycle Oriented**: 前回の課題を今回のテーマにし、今回の発見を次回へつなげる「線」の管理を行う

## 🚀 クイックスタート

### 1. セットアップ

#### 開発環境（Mac/Linux）

```bash
# リポジトリをクローン（既に完了している場合はスキップ）
git clone https://github.com/ishidafuu/isdf_tennis_discovery_agent.git
cd isdf_tennis_discovery_agent

# 環境変数の設定
# 機密情報（.env）と非機密情報（.env.config）を分離して管理
cp .env.template .env
# .env ファイルを編集して、APIキー等の機密情報を設定
# .env.config ファイルを編集して、リポジトリ名等の非機密情報を設定

# 依存パッケージのインストール
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# セットアップ確認（推奨）
python check_setup.py
```

#### Raspberry Pi本番環境（dotenvx使用）

dotenvxを使用することで、環境変数を暗号化してGitに安全にコミット可能です。

```bash
# dotenvxクイックスタート
# Mac側: 環境変数を暗号化
npm install -g @dotenvx/dotenvx
dotenvx encrypt -f .env

# Raspberry Pi側: 自動セットアップ
bash deployment/scripts/setup-raspberry-pi.sh
```

詳細ガイド：
- **全体の流れ**: [SETUP.md](./SETUP.md)
- **Discord Bot作成**: [docs/セットアップ/Discordボット.md](./docs/セットアップ/Discordボット.md)
- **dotenvxクイックスタート**: [docs/セットアップ/dotenvxクイックスタート.md](./docs/セットアップ/dotenvxクイックスタート.md) 🔐
- **dotenvx詳細ガイド**: [docs/セットアップ/dotenvx設定.md](./docs/セットアップ/dotenvx設定.md)

### 2. 実行

```bash
python main.py
```

ボットが起動したら、Discordで音声メッセージを送信してください。

### 3. 更新 & 再起動（Raspberry Pi本番環境）

Raspberry Piでsystemdサービスとして動かしている場合、以下のコマンドでBotを最新版に更新できます。

```bash
# スクリプトに実行権限を付与（初回のみ）
chmod +x update_bot.sh

# Botを更新して再起動
./update_bot.sh
```

このスクリプトは以下の処理を自動実行します：
1. Git Pullで最新コードを取得
2. `pip install -r requirements.txt`でライブラリを更新
3. `sudo systemctl restart tennis-bot`でサービスを再起動
4. 起動ログを表示（動作確認用）

**注意**: systemdサービスが設定されていない場合は、[SETUP.md](./SETUP.md)の「自動起動設定」を参照してください。

### 4. 使い方

1. **Discordボットを招待**
   - [SETUP.md](./SETUP.md) の手順に従ってボットを作成し、サーバーに招待

2. **音声メッセージを送信**
   - スマホのDiscordアプリでマイク長押し → 練習内容を話す
   - 例：「今日はサーブの練習をしました。トスを上げる時に左手を脱力すると、自然な回旋が生まれることに気づきました...」

3. **自動処理**
   - ボットが音声を文字起こし
   - Gemini AIが構造化データを抽出
   - Obsidian形式のMarkdownを生成
   - GitHubリポジトリに自動Push

4. **結果確認**
   - Discordに処理結果が表示される
   - GitHubリポジトリで詳細を確認
   - Obsidianでノートを閲覧

## 📁 プロジェクト構成

```
isdf_tennis_discovery_agent/
├── src/
│   ├── bot/              # Discordボット
│   │   ├── handlers/     # メッセージ・DM処理
│   │   └── helpers/      # ユーティリティ
│   ├── ai/               # Gemini AI処理
│   ├── storage/          # Obsidian・GitHub管理
│   ├── search/           # 感覚検索・ベクトル検索
│   ├── analysis/         # 統計・パターン分析・予測
│   ├── scheduler/        # リマインダー・週次レビュー
│   └── models/           # データモデル
├── scripts/              # バッチ処理スクリプト
├── tests/                # テストコード（30+件）
├── docs/                 # ドキュメント
│   ├── FEATURES.md       # 機能一覧（詳細）
│   ├── plan.md           # 実装計画
│   └── session-log.md    # 開発ログ
├── .env.template         # 機密情報テンプレート
├── .env.config           # 非機密情報（平文）
├── requirements.txt      # 依存パッケージ
├── SETUP.md              # セットアップガイド
└── main.py               # エントリーポイント
```

## 📋 実装状況

### Phase 1: 記録の構造化 ✅ **完了** (20/20タスク)
- ✅ マルチモーダル入力（音声・テキスト・画像・動画）
- ✅ シーン別処理（#壁打ち、#スクール、#試合、#フリー練習、#振り返り）
- ✅ 前回ログ自動読み込み（サイクル追跡）
- ✅ Git LFS管理、DM処理

### Phase 2: 対話の深化 ✅ **完了** (8/8タスク)
- ✅ ソクラテス式問答（気づきを促す質問生成）
- ✅ Discordボタンインターフェース（もっと詳しく、比較、保存）
- ✅ AIの自動判断（深掘り・比較・保存の選択）
- ✅ #質問チャンネル（過去記録から質問応答）
- ✅ 矛盾・変化の検出

### Phase 3: 資産の活用 ✅ **完了** (10/10タスク)
- ✅ 感覚検索（類義語辞書：シュッ、ガツン、ふわっ等）
- ✅ 自動リンク生成（タグ・日付ベース）
- ✅ 統計・グラフ機能（Obsidian Charts連携）
- ✅ 課題進捗確認・リマインド
- ✅ #分析チャンネル（期間指定でAI分析）

### Phase 4: 高度な分析 ✅ **完了** (10/10タスク)
- ✅ Embedding生成（Gemini text-embedding-004）
- ✅ ベクトル検索（ChromaDB、意味的類似性）
- ✅ パターン分析（好調/不調、時系列、ターニングポイント）
- ✅ 予測・提案（成長予測、練習メニュー、コンディション予測）
- ✅ バッチ処理スクリプト

**✅ Phase 1-4 全完了！（48/48タスク 100%）**

詳細は [`docs/使い方/機能一覧.md`](./docs/使い方/機能一覧.md) を参照してください。

## 🔧 技術スタック

| カテゴリ | 技術 |
|---------|------|
| AI処理 | Google Gemini 2.5 Flash |
| Embedding | Gemini text-embedding-004 |
| ベクトルDB | ChromaDB (ローカル) |
| フロントエンド | Discord Bot (discord.py) |
| ストレージ | Obsidian Vault (Markdown) |
| バージョン管理 | GitHub (Git LFS対応) |
| 言語 | Python 3.11+ |
| インフラ | Raspberry Pi (本番環境) |

## 📚 ドキュメント

### ユーザー向け
- **[ドキュメント索引](./docs/index.md)** 📖 - すべてのドキュメントの入り口
- **[ストーリーガイド](./docs/使い方/ストーリーガイド.md)** 🌟 - 3ヶ月で上達するまでの物語（おすすめ！）
- **[基本的な使い方](./docs/使い方/基本的な使い方.md)** - チャンネル別の使い方、Tips
- **[セットアップガイド](./SETUP.md)** - 環境構築手順

### 開発者向け
- **[機能一覧](./docs/使い方/機能一覧.md)** - 全機能の詳細説明
- **[アーキテクチャ](./docs/開発/概要/アーキテクチャ.md)** - システム構成図・データフロー
- **[詳細アーキテクチャ](./docs/開発/技術/詳細アーキテクチャ.md)** - 技術詳細
- **[実装計画](./docs/開発/plan.md)** - Phase 1-4のタスクリスト
- **[開発ログ](./docs/開発/session-log.md)** - 実装履歴
- **[プロジェクト管理](./CLAUDE.md)** - コーディング規約・自律行動ルール

## 💰 コスト試算

- **Gemini API**: 月100メモで約10円（文字起こし + 構造化抽出）
- **Embedding生成**: 月100メモで約1円
- **GitHub LFS**: 無料枠1GB/月（超過時: $5/月で50GB）
- **合計**: 月間100メモで**約11円**（非常に安価）

## 🛡️ セキュリティ

### dotenvx導入後の環境変数管理

環境変数は2つのファイルに分離して管理します：
- **`.env`** - 機密情報のみ（dotenvxで暗号化してGitにコミット）
  - `DISCORD_BOT_TOKEN`、`GEMINI_API_KEY`、`GITHUB_TOKEN`
- **`.env.config`** - 非機密情報（平文でGitにコミット可能）
  - `GITHUB_REPO`、`OBSIDIAN_PATH`、`ADMIN_USER_ID`等

セキュリティルール：
- **暗号化された`.env`**をGitにコミット（平文の`.env`はコミット禁止）
- **`.env.keys`（暗号化鍵）**は絶対にGitにコミットしない（`.gitignore`で除外済み）
- `.env.keys`のパーミッションを`600`に設定（所有者のみ読み書き可能）
- プライベートリポジトリで管理
- 年1回程度、鍵をローテーション推奨

詳細は [docs/セットアップ/dotenvxクイックスタート.md](./docs/セットアップ/dotenvxクイックスタート.md) を参照してください。

## 📄 ライセンス

MIT License

---

**✅ Phase 1-4 全実装完了**: 音声メモからAI分析・予測まで、すべての機能が利用可能です。

詳細な機能説明は [`docs/使い方/機能一覧.md`](./docs/使い方/機能一覧.md) をご覧ください。
