# Tennis Discovery Agent - クイックスタートガイド

## 🎯 このガイドについて

Tennis Discovery Agentを**最短で始めるための**ガイドです。

**所要時間: 約2-3時間**（Raspberry Piセットアップ含む）

---

## 📋 事前準備

### 必要なもの

#### ハードウェア
- ✅ Raspberry Pi 3/4/5（推奨: Raspberry Pi 4以上、2GB RAM以上）
- ✅ microSDカード（16GB以上）
- ✅ 電源アダプター（USB-C、5V 3A推奨）
- ✅ PC（セットアップ用）

#### アカウント・APIキー
- ✅ [Discord Developer Portal](https://discord.com/developers/applications) アカウント
- ✅ [Google AI Studio](https://makersuite.google.com/app/apikey) アカウント（Gemini API）
- ✅ [GitHub](https://github.com/) アカウント（オプション）

---

## 🚀 セットアップフロー

```
1. Discord Bot作成（10分）
   ↓
2. Gemini APIキー取得（5分）
   ↓
3. Raspberry Pi準備（30分）
   ↓
4. プロジェクトセットアップ（30分）
   ↓
5. 動作確認（10分）
   ↓
6. Obsidian設定（30分-1時間）
```

---

## 1️⃣ Discord Botの作成

### 1.1 アプリケーション作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. 名前を入力: `Tennis Discovery Agent`
4. 「Create」をクリック

### 1.2 Bot設定

1. 左メニューから「Bot」を選択
2. 「Add Bot」→「Yes, do it!」
3. 「Reset Token」をクリック→トークンをコピー（後で使用）

**重要: トークンは絶対に公開しないこと**

### 1.3 Bot権限の設定

**Privileged Gateway Intents:**
```
✅ MESSAGE CONTENT INTENT（必須）
```

**Bot Permissions:**
```
✅ Send Messages
✅ Read Message History
✅ Attach Files
✅ Add Reactions
```

### 1.4 Botをサーバーに招待

1. 左メニューから「OAuth2」→「URL Generator」
2. **SCOPES:**
   - ✅ `bot`
3. **BOT PERMISSIONS:**
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Attach Files
4. 生成されたURLをコピー→ブラウザで開く
5. サーバーを選択→「認証」

### 1.5 Discordチャンネルの作成

**サーバーで以下のチャンネルを作成:**
```
#壁打ち
#スクール
#試合
#振り返り
```

---

## 2️⃣ Gemini APIキーの取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. 「Create API Key」をクリック
3. APIキーをコピー（後で使用）

---

## 3️⃣ Raspberry Piの準備

### 3.1 OSのインストール

**詳細: [setup/04-raspberry-pi.md](setup/04-raspberry-pi.md) を参照**

**クイック手順:**
1. [Raspberry Pi Imager](https://www.raspberrypi.com/software/)をダウンロード
2. microSDカードを挿入
3. OS選択: `Raspberry Pi OS (64-bit)`
4. 詳細設定（歯車アイコン）:
   - ホスト名: `tennis-bot`
   - SSH有効化
   - ユーザー名: `pi`、パスワード設定
   - Wi-Fi設定（SSID、パスワード）
   - タイムゾーン: `Asia/Tokyo`
5. 書き込み実行
6. Raspberry Piに挿入して起動

### 3.2 SSH接続

```bash
# PCから接続
ssh pi@tennis-bot.local

# パスワードを入力
```

---

## 4️⃣ プロジェクトのセットアップ

### 4.1 システムアップデート

```bash
sudo apt update && sudo apt upgrade -y
```

### 4.2 必要なソフトウェアのインストール

```bash
# Python、Git等
sudo apt install -y python3-pip python3-venv git

# 音声処理（オプション）
sudo apt install -y ffmpeg
```

### 4.3 プロジェクトのクローン

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/tennis-discovery-agent.git
cd tennis-discovery-agent
```

**注: GitHubリポジトリがまだない場合:**
```bash
# ローカルからRaspberry Piに転送（PC側で実行）
scp -r /path/to/tennis-discovery-agent pi@tennis-bot.local:~/
```

### 4.4 仮想環境の作成

```bash
cd ~/tennis-discovery-agent
python3 -m venv venv
source venv/bin/activate
```

### 4.5 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4.6 環境変数の設定

```bash
# .envファイルを作成
nano .env
```

**以下を記入:**
```env
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
OBSIDIAN_VAULT_PATH=/home/pi/obsidian-vault
ENV=production
LOG_LEVEL=INFO
```

**保存: Ctrl+O → Enter、終了: Ctrl+X**

### 4.7 Obsidian Vaultの準備

```bash
mkdir -p ~/obsidian-vault/daily
mkdir -p ~/obsidian-vault/weekly-reviews
mkdir -p ~/obsidian-vault/templates
mkdir -p ~/obsidian-vault/attachments
```

### 4.8 Git LFSのセットアップ

**画像・動画ファイルの管理に必要**

```bash
# Git LFSのインストール
sudo apt install -y git-lfs

# Obsidian Vaultに移動
cd ~/obsidian-vault

# Git初期化（まだの場合）
git init

# Git LFS有効化
git lfs install

# 画像・動画ファイルのトラッキング設定
git lfs track "attachments/**/*.jpg"
git lfs track "attachments/**/*.jpeg"
git lfs track "attachments/**/*.png"
git lfs track "attachments/**/*.gif"
git lfs track "attachments/**/*.mp4"
git lfs track "attachments/**/*.mov"

# .gitattributesをコミット
git add .gitattributes
git commit -m "Setup Git LFS for media files"
```

**重要:**
- Git LFSは画像・動画ファイルを効率的に管理します
- GitHub無料枠: 1GB/月のデータ転送
- 3-6ヶ月で容量オーバーの可能性あり（追加購入: $5/月で50GB）

---

## 5️⃣ 動作確認

### 5.1 手動起動テスト

```bash
cd ~/tennis-discovery-agent
source venv/bin/activate
python3 src/main.py
```

**正常に起動した場合:**
```
Bot起動メッセージが表示される
Discord Botがオンライン状態になる
```

**テスト:**
1. Discord の `#壁打ち` チャンネルで音声メッセージを送信
2. Botが反応すればOK

**停止: Ctrl+C**

### 5.2 自動起動の設定

**詳細: [setup/04-raspberry-pi.md](setup/04-raspberry-pi.md) を参照**

**クイック手順:**

```bash
# サービスファイルを作成
sudo nano /etc/systemd/system/tennis-bot.service
```

**以下を記入:**
```ini
[Unit]
Description=Tennis Discovery Agent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/tennis-discovery-agent
ExecStart=/home/pi/tennis-discovery-agent/venv/bin/python3 /home/pi/tennis-discovery-agent/src/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**保存: Ctrl+O → Enter、終了: Ctrl+X**

**サービスを有効化:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tennis-bot
sudo systemctl start tennis-bot

# 状態確認
sudo systemctl status tennis-bot
```

---

## 6️⃣ Obsidianのセットアップ

### 6.1 Obsidianのインストール

**詳細: [setup/03-obsidian.md](setup/03-obsidian.md)**

1. [Obsidian公式サイト](https://obsidian.md/)からダウンロード
2. 新しいVaultを作成
3. Vaultの場所: 任意（例: `~/Documents/Tennis Notes`）

### 6.2 GitHub同期の設定（推奨）

**Raspberry Pi側:**
```bash
cd ~/obsidian-vault
git init
git remote add origin https://github.com/YOUR_USERNAME/tennis-notes.git
```

**PC（Obsidian）側:**
```bash
# Obsidian Vaultのディレクトリで
git clone https://github.com/YOUR_USERNAME/tennis-notes.git
```

### 6.3 必須プラグインのインストール

**Obsidian内で:**
1. 設定 → コミュニティプラグイン → 閲覧
2. 以下をインストール:
   - **Dataview**: データ集計
   - **Calendar**: カレンダービュー

### 6.4 ダッシュボードの作成

**Obsidian Vaultのルートに `dashboard.md` を作成:**

````markdown
# 🎾 Tennis Dashboard

## 📊 今月の統計

```dataview
TABLE WITHOUT ID
  length(rows) as "練習日数"
FROM "daily"
WHERE date >= date(today) - dur(30 days)
```

## 📅 最近の練習

```dataview
TABLE scene as "シーン", date as "日付"
FROM "daily"
SORT date DESC
LIMIT 5
```
````

---

## ✅ セットアップ完了チェックリスト

### 必須項目

- [ ] Discord Botが作成されている
- [ ] Gemini APIキーが取得されている
- [ ] Raspberry Piが起動している
- [ ] SSH接続ができる
- [ ] プロジェクトがRaspberry Piにある
- [ ] .envファイルが正しく設定されている
- [ ] Git LFSがセットアップされている
- [ ] attachmentsフォルダが作成されている
- [ ] systemdサービスが有効化されている
- [ ] Botが起動している（`sudo systemctl status tennis-bot`で確認）
- [ ] Discord Botがオンラインになっている
- [ ] 音声メッセージをBotが受信できる
- [ ] テキストメッセージをBotが受信できる
- [ ] 画像をBotが受信できる
- [ ] Obsidianがインストールされている
- [ ] Dataviewプラグインがインストールされている

### オプション項目

- [ ] GitHub同期が設定されている
- [ ] 自動バックアップが設定されている
- [ ] UPS（無停電電源装置）が接続されている

---

## 🎮 使い方

### 基本的な使い方

1. **練習メモを記録:**
   ```
   Discord の #壁打ち チャンネルで音声メッセージを送信
   「今日はフォアハンドを30分練習した。トップスピンが安定してきた」
   ```

2. **Botが自動処理:**
   - 音声を文字起こし
   - 構造化データを抽出
   - Obsidian Markdownに保存
   - GitHub Push（設定している場合）

3. **Obsidianで確認:**
   - `daily/YYYY-MM-DD-壁打ち.md` が作成される
   - ダッシュボードで統計確認

### チャンネルの使い分け

| チャンネル | 使用場面 |
|-----------|---------|
| `#壁打ち` | 壁打ち練習の記録 |
| `#スクール` | スクール練習の記録 |
| `#試合` | 試合の記録 |
| `#振り返り` | 後日の追記・補足 |

---

## 🐛 トラブルシューティング

### Botが起動しない

**確認:**
```bash
sudo systemctl status tennis-bot
sudo journalctl -u tennis-bot -n 50
```

**よくある原因:**
- `.env`ファイルの設定ミス
- Discord Bot Tokenが無効
- Gemini APIキーが無効

**解決:**
```bash
# 手動で起動してエラーを確認
cd ~/tennis-discovery-agent
source venv/bin/activate
python3 src/main.py
```

### Botがメッセージを受信しない

**確認項目:**
- Discord Botがオンラインか
- MESSAGE CONTENT INTENTが有効か
- Bot権限が正しいか

**Discord Developer Portalで確認:**
```
Bot → Privileged Gateway Intents → MESSAGE CONTENT INTENT をON
```

---

## 📚 次のステップ

### Phase 1実装後

- [ ] 週次レビュー機能を有効化
- [ ] 前回ログの読み込み機能を実装
- [ ] リマインド機能を設定

### Phase 2以降

- [ ] オプションボタン（深堀質問）の実装
- [ ] #質問 チャンネルでAIに質問
- [ ] ベクトル検索の実装

**詳細: [phases/index.md](phases/index.md)**

---

## 💰 運用コスト

```
電気代: 約50-100円/月
Gemini API: 約150-450円/月

合計: 約200-550円/月（年間2,400-6,600円）
```

**Railwayと比較: 約1/10のコスト**

---

## 🎯 サポート

### ドキュメント

- **全体概要:** [overview/index.md](overview/index.md)
- **実装フェーズ:** [phases/index.md](phases/index.md)
- **技術詳細:** [technical/index.md](technical/index.md)
- **セットアップ:** [setup/index.md](setup/index.md)
- **リファレンス:** [reference/index.md](reference/index.md)

### コマンドリファレンス

```bash
# サービス操作
sudo systemctl start tennis-bot    # 起動
sudo systemctl stop tennis-bot     # 停止
sudo systemctl restart tennis-bot  # 再起動
sudo systemctl status tennis-bot   # 状態確認

# ログ確認
sudo journalctl -u tennis-bot -f   # リアルタイムログ
sudo journalctl -u tennis-bot -n 100  # 最新100行

# コード更新
cd ~/tennis-discovery-agent
git pull origin main
sudo systemctl restart tennis-bot
```

---

**セットアップお疲れ様でした！Tennis Discovery Agentで素晴らしいテニスライフをお楽しみくださいませ！**

---

**最終更新:** 2025-01-27
