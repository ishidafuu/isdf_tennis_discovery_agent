#!/bin/bash
# Tennis Discovery Agent - Mac側デプロイスクリプト
# Mac側で実行し、ラズパイに最新コードをデプロイします

set -e  # エラーが発生したら即座に終了

APP_NAME="tennis-bot"
RASPBERRY_PI_HOST="${RASPBERRY_PI_HOST:-pi@raspberrypi.local}"
APP_DIR="isdf_tennis_discovery_agent"

echo "=========================================="
echo "Tennis Discovery Agent - Deploy to Raspberry Pi"
echo "=========================================="
echo "Target: $RASPBERRY_PI_HOST"
echo "App: $APP_NAME"
echo "=========================================="
echo

# 1. ローカルの変更をGitにプッシュ
echo "📤 Pushing changes to Git..."

# 未コミットの変更があるか確認
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Uncommitted changes detected"
    read -p "Do you want to commit and push these changes? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " commit_msg
        git add .
        git commit -m "$commit_msg"
        git push origin main
        echo "✓ Changes committed and pushed"
    else
        echo "⚠️  Deploying without committing local changes"
        echo "⚠️  Only committed changes will be deployed to Raspberry Pi"
    fi
else
    # 変更がない場合もプッシュ（リモートとの同期確認）
    git push origin main 2>/dev/null || echo "✓ Already up to date"
fi

# 2. ラズパイにSSH接続してデプロイ
echo
echo "🚀 Deploying to Raspberry Pi..."
ssh "$RASPBERRY_PI_HOST" bash <<EOF
    set -e

    echo "📥 Pulling latest changes..."
    cd ~/$APP_DIR
    git pull origin main

    echo "🐍 Updating Python dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt --quiet

    echo "🔑 Checking .env.keys..."
    if [ ! -f .env.keys ]; then
        echo "⚠️  ERROR: .env.keys not found on Raspberry Pi!"
        echo "Please copy the key file:"
        echo "  scp .env.keys $RASPBERRY_PI_HOST:~/$APP_DIR/"
        exit 1
    fi

    echo "🔍 Verifying encrypted .env..."
    if ! head -n 1 .env | grep -q "DOTENV_PUBLIC_KEY"; then
        echo "⚠️  WARNING: .env file appears to be unencrypted"
    fi

    echo "🔄 Restarting service..."
    sudo systemctl restart $APP_NAME

    # 少し待ってからステータス確認
    sleep 2

    echo
    echo "=========================================="
    echo "✅ Deployment Complete!"
    echo "=========================================="
    echo
    echo "Service Status:"
    sudo systemctl status $APP_NAME --no-pager -l

    echo
    echo "Recent Logs (last 20 lines):"
    sudo journalctl -u $APP_NAME -n 20 --no-pager
EOF

echo
echo "=========================================="
echo "✅ Deploy script finished"
echo "=========================================="
echo
echo "To view live logs:"
echo "  ssh $RASPBERRY_PI_HOST 'sudo journalctl -u $APP_NAME -f'"
echo
