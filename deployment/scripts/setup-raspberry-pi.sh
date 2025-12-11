#!/bin/bash
# Tennis Discovery Agent - Raspberry Pi Setup Script
# このスクリプトはラズパイ側で1回だけ実行します

set -e  # エラーが発生したら即座に終了

APP_NAME="tennis-bot"
APP_DIR="$HOME/isdf_tennis_discovery_agent"
REPO_URL="https://github.com/ishidafuu/isdf_tennis_discovery_agent.git"

echo "=========================================="
echo "Tennis Discovery Agent - Raspberry Pi Setup"
echo "=========================================="
echo

# 1. システムアップデート
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. 必要なパッケージをインストール
echo "📦 Installing required packages..."
sudo apt-get install -y git python3 python3-pip python3-venv

# 3. Node.jsとdotenvxをインストール
echo "📦 Installing Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "✓ Node.js already installed"
fi

echo "📦 Installing dotenvx..."
if ! command -v dotenvx &> /dev/null; then
    sudo npm install -g @dotenvx/dotenvx
else
    echo "✓ dotenvx already installed"
fi

# dotenvxのバージョン確認
echo "dotenvx version: $(dotenvx --version)"

# 4. リポジトリをクローン（まだない場合）
if [ ! -d "$APP_DIR" ]; then
    echo "📥 Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
else
    echo "✓ Repository already exists"
    echo "📥 Pulling latest changes..."
    cd "$APP_DIR"
    git pull origin main
fi

cd "$APP_DIR"

# 5. Python仮想環境を作成
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# 6. 依存関係をインストール
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. .env.keysファイルの配置を確認
echo "🔑 Checking for .env.keys file..."
if [ ! -f ".env.keys" ]; then
    echo "⚠️  WARNING: .env.keys file not found!"
    echo "Please copy the .env.keys file from your Mac:"
    echo "  scp .env.keys pi@raspberrypi.local:$APP_DIR/"
    echo
    read -p "Do you want to paste the .env.keys content now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Paste the content of .env.keys below (press Ctrl+D when done):"
        cat > .env.keys
        chmod 600 .env.keys
        echo "✓ .env.keys file created"
    else
        echo "⚠️  Please copy .env.keys manually before starting the service"
    fi
else
    echo "✓ .env.keys file already exists"
    chmod 600 .env.keys
fi

# 8. .envファイルの存在確認
echo "🔍 Checking for .env file..."
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Please ensure the encrypted .env file is in the repository"
    echo "Run 'git pull' to get the latest version"
else
    echo "✓ .env file found"
    # 暗号化されているか確認
    if head -n 1 .env | grep -q "DOTENV_PUBLIC_KEY"; then
        echo "✓ .env file is encrypted"
    else
        echo "⚠️  WARNING: .env file appears to be unencrypted"
        echo "Please run 'dotenvx encrypt -f .env' on your Mac and push to Git"
    fi
fi

# 9. systemdサービスファイルをインストール
echo "⚙️  Installing systemd service..."
# ユーザー名、ホームディレクトリ、dotenvxパスを自動検出
CURRENT_USER=$(whoami)
CURRENT_HOME=$(eval echo ~$CURRENT_USER)
DOTENVX_PATH=$(which dotenvx)

echo "Detected configuration:"
echo "  User: $CURRENT_USER"
echo "  Home: $CURRENT_HOME"
echo "  dotenvx: $DOTENVX_PATH"

# テンプレートファイルのプレースホルダーを実際の値に置換
sed -e "s|USER_NAME|$CURRENT_USER|g" \
    -e "s|HOME_DIR|$CURRENT_HOME|g" \
    -e "s|DOTENVX_PATH|$DOTENVX_PATH|g" \
    deployment/systemd/tennis-bot.service > /tmp/tennis-bot.service

# 置換後のファイルをsystemdディレクトリにコピー
sudo mv /tmp/tennis-bot.service /etc/systemd/system/tennis-bot.service

sudo systemctl daemon-reload
sudo systemctl enable tennis-bot

# 10. サービスを起動
echo "🚀 Starting tennis-bot service..."
sudo systemctl start tennis-bot

# 11. ステータス確認
echo
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo
echo "Service Status:"
sudo systemctl status tennis-bot --no-pager -l
echo
echo "Useful Commands:"
echo "  sudo systemctl status tennis-bot       # Check status"
echo "  sudo systemctl restart tennis-bot      # Restart service"
echo "  sudo journalctl -u tennis-bot -f       # View logs"
echo
echo "To deploy updates from Mac:"
echo "  ~/bin/pi-deploy-tennis-bot"
echo
