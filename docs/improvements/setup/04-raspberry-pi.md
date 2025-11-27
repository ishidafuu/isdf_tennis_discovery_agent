# Raspberry Pi セットアップ

## 概要

Tennis Discovery AgentをRaspberry Piで常時稼働させるためのセットアップガイドです。

**想定環境:**
- Raspberry Pi 3/4/5（推奨: Raspberry Pi 4以上）
- Raspberry Pi OS（Debian Bookworm推奨）
- メモリ: 2GB以上推奨
- ストレージ: 16GB以上のmicroSD

---

## 1. OSのインストール

### 1.1 Raspberry Pi Imagerを使用

1. [Raspberry Pi Imager](https://www.raspberrypi.com/software/)をダウンロード
2. microSDカードを挿入
3. 設定:

```
デバイス: Raspberry Pi 4
OS: Raspberry Pi OS (64-bit)
```

**詳細設定（歯車アイコン）:**
```
✅ ホスト名: tennis-bot
✅ SSHを有効化
✅ ユーザー名とパスワードを設定
✅ Wi-Fi設定
✅ タイムゾーン: Asia/Tokyo
```

### 1.2 SSH接続

```bash
# ホスト名で接続
ssh pi@tennis-bot.local

# またはIPアドレスで接続
ssh pi@192.168.1.xxx
```

---

## 2. 必要なソフトウェアのインストール

### 2.1 システムアップデート

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### 2.2 Python環境

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

```bash
# プロジェクトをクローン
cd ~
git clone https://github.com/YOUR_USERNAME/tennis-discovery-agent.git

# 仮想環境を作成
cd ~/tennis-discovery-agent
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 3.2 環境変数

```bash
nano .env
```

```env
DISCORD_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
OBSIDIAN_VAULT_PATH=/home/pi/obsidian-vault
ADMIN_USER_ID=your_id
ENV=production
LOG_LEVEL=INFO
```

---

## 4. systemdによる自動起動

### 4.1 サービスファイル作成

```bash
sudo nano /etc/systemd/system/tennis-bot.service
```

```ini
[Unit]
Description=Tennis Discovery Agent Discord Bot
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

### 4.2 サービスの有効化

```bash
# デーモンをリロード
sudo systemctl daemon-reload

# 自動起動を有効化
sudo systemctl enable tennis-bot

# サービスを開始
sudo systemctl start tennis-bot

# 状態確認
sudo systemctl status tennis-bot
```

---

## 5. よく使うコマンド

```bash
# サービス操作
sudo systemctl stop tennis-bot
sudo systemctl restart tennis-bot
sudo systemctl status tennis-bot

# ログ確認
sudo journalctl -u tennis-bot -f      # リアルタイム
sudo journalctl -u tennis-bot -n 100  # 最新100行

# 手動起動（デバッグ）
cd ~/tennis-discovery-agent
source venv/bin/activate
python3 src/main.py
```

---

## 6. メンテナンス

### 6.1 コード更新

```bash
sudo systemctl stop tennis-bot
cd ~/tennis-discovery-agent
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl start tennis-bot
```

### 6.2 バックアップ

```bash
# Obsidian Vaultのバックアップ
cd ~/obsidian-vault
tar -czf ~/obsidian-backup-$(date +%Y%m%d).tar.gz .
```

---

## 7. トラブルシューティング

### Botが起動しない

```bash
# エラーログを確認
sudo journalctl -u tennis-bot -n 50

# 手動で起動してエラーを確認
cd ~/tennis-discovery-agent
source venv/bin/activate
python3 src/main.py
```

### メモリ不足

```bash
# メモリ確認
free -h

# スワップを増やす
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 温度監視

```bash
# CPU温度を確認
vcgencmd measure_temp

# 正常範囲: 40-70°C
# 警告: 80°C以上
```

---

## 8. 運用コスト

```
電力消費: 約3W（平均）
月額電気代: 約58円（27円/kWh計算）
年間コスト: 約700円
```

---

## 次のステップ

- [環境変数と設定ファイル](05-environment.md)
