# Raspberry Pi セットアップ

## 概要

Tennis Discovery AgentをRaspberry Piで常時稼働させるためのセットアップガイドです。

**動作環境:**
- Raspberry Pi 4 Model B
- Raspberry Pi OS (64-bit)
- ユーザー名: `ishidafuu`
- ホスト名: `isdf-pi`
- プロジェクト名: `isdf_tennis_discovery_agent`

---

## 1. OSのインストール

### 1.1 Raspberry Pi Imagerを使用

1. [Raspberry Pi Imager](https://www.raspberrypi.com/software/)をPCで起動
2. microSDカードを挿入
3. 設定:

```
デバイス: Raspberry Pi 4
OS: Raspberry Pi OS (64-bit)
```

**詳細設定（歯車アイコン）:**
重要: キーボード設定を誤ると記号が打てなくなるため注意してください。

```
✅ ホスト名: isdf-pi
✅ SSHを有効化（パスワード認証）
✅ ユーザー名: ishidafuu
✅ パスワード: （任意のパスワード）
✅ Wi-Fi設定: （SSIDとパスワードを入力）
✅ タイムゾーン: Asia/Tokyo
✅ キーボードレイアウト: us （※英字配列として設定推奨）
```

### 1.2 SSH接続

PCのターミナルから接続します。

```bash
# ホスト名で接続
ssh ishidafuu@isdf-pi.local
```

※ 初回接続時は `yes` を入力し、設定したパスワードを入力します。

---

## 2. 必要なソフトウェアのインストール

### 2.1 システムアップデート

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### 2.2 Python環境とGit

```bash
# Python3とpip
sudo apt install -y python3-pip python3-venv

# Git
sudo apt install -y git

# Git LFS（画像・動画管理）
sudo apt install -y git-lfs
git lfs install
```

---

## 3. プロジェクトのセットアップ

### 3.1 クローンと仮想環境

GitHubの認証にはパーソナルアクセストークン（PAT）が必要です。

```bash
# ホームディレクトリへ移動
cd ~

# プロジェクトをクローン
git clone https://github.com/ishidafuu/isdf_tennis_discovery_agent.git

# ディレクトリへ移動
cd isdf_tennis_discovery_agent

# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 3.2 環境変数 (.env)

```bash
nano .env
```

以下の内容を編集・保存（`Ctrl+O` -> `Enter` -> `Ctrl+X`）します。

```env
DISCORD_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here
# パスはユーザー名に合わせて変更
OBSIDIAN_VAULT_PATH=/home/ishidafuu/obsidian-vault
ADMIN_USER_ID=your_discord_user_id
ENV=production
LOG_LEVEL=INFO
```

### 3.3 データ保存用ディレクトリ作成

```bash
mkdir -p /home/ishidafuu/obsidian-vault
```

---

## 4. systemdによる自動起動

### 4.1 サービスファイル作成

```bash
sudo nano /etc/systemd/system/tennis-bot.service
```

以下の内容を保存します。

```ini
[Unit]
Description=Tennis Discovery Agent Discord Bot
After=network.target

[Service]
Type=simple
User=ishidafuu
WorkingDirectory=/home/ishidafuu/isdf_tennis_discovery_agent
ExecStart=/home/ishidafuu/isdf_tennis_discovery_agent/venv/bin/python3 /home/ishidafuu/isdf_tennis_discovery_agent/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4.2 サービスの有効化と起動

```bash
# 設定を読み込み
sudo systemctl daemon-reload

# 自動起動を有効化
sudo systemctl enable tennis-bot

# サービスを開始
sudo systemctl start tennis-bot

# 状態確認（active (running) なら成功）
sudo systemctl status tennis-bot
```

---

## 5. 運用・メンテナンス

### 5.1 簡単アップデート用スクリプト

Botの更新と再起動をワンコマンドで行うスクリプトを作成します。

**スクリプト作成:**
```bash
cd ~
nano update_bot.sh
```

**内容:**
```bash
#!/bin/bash

PROJECT_DIR="isdf_tennis_discovery_agent"

echo "========================================"
echo "🔄 Botの更新を開始します..."
echo "========================================"

cd ~/$PROJECT_DIR

echo "📥 Git Pull..."
git pull

echo "📦 ライブラリ更新..."
source venv/bin/activate
pip install -r requirements.txt

echo "========================================"
echo "🚀 サービスを再起動します..."
echo "========================================"

sudo systemctl restart tennis-bot
echo "✅ 再起動完了。直近のログを表示します（Ctrl+Cで終了）"
sudo journalctl -u tennis-bot -n 20 -f
```

**実行権限の付与:**
```bash
chmod +x update_bot.sh
```

**使い方:**
今後、Botを最新版にしたいときは以下を実行するだけです。
```bash
./update_bot.sh
```

### 5.2 よく使うコマンド一覧

| 操作 | コマンド |
|---|---|
| **Botの状態確認** | `sudo systemctl status tennis-bot` |
| **ログのリアルタイム表示** | `sudo journalctl -u tennis-bot -f` |
| **Botの停止** | `sudo systemctl stop tennis-bot` |
| **Botの再起動** | `sudo systemctl restart tennis-bot` |
| **手動起動（デバッグ用）** | `source venv/bin/activate` → `python3 main.py` |

---

## 6. トラブルシューティング

### サービスが見つからない・起動しない
- サービスファイルのパスやファイル名を確認 (`/etc/systemd/system/tennis-bot.service`)
- ファイル内のパス（User名やフォルダ名）が間違っていないか確認
- `sudo systemctl daemon-reload` を実行したか確認

### ログにエラーが出る場合
```bash
# 詳細なログを確認
sudo journalctl -u tennis-bot -n 50 --no-pager
```

### アップデートスクリプトが動かない
- `Permission denied` と出る場合 → `chmod +x update_bot.sh` を実行してください。

---