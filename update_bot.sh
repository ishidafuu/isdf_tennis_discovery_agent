#!/bin/bash

# Tennis Discovery Agent - 更新 & 再起動スクリプト
#
# 機能:
#   1. Gitから最新コードを取得
#   2. Pythonライブラリを更新
#   3. systemdサービスとして動いているBotを再起動
#   4. 起動ログを表示（確認用）
#
# 使い方:
#   ./update_bot.sh
#
# 前提条件:
#   - systemdサービス（tennis-bot.service）が設定済み
#   - sudoパスワードなしでsystemctl restart可能（または手動入力）

PROJECT_DIR="isdf_tennis_discovery_agent"

echo "========================================"
echo "🔄 Tennis Bot の更新を開始します..."
echo "========================================"

# プロジェクトフォルダに移動
cd ~/$PROJECT_DIR || { echo "❌ プロジェクトフォルダが見つかりません"; exit 1; }

# 現在のブランチを確認
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 現在のブランチ: $CURRENT_BRANCH"

# Gitから最新コードを取得
echo ""
echo "📥 Git Pull (最新コードの取得)..."
git pull || { echo "❌ Git Pull に失敗しました"; exit 1; }

# 仮想環境を有効化してライブラリを更新
echo ""
echo "📦 ライブラリの更新チェック..."
source venv/bin/activate
pip install -r requirements.txt --quiet || { echo "❌ ライブラリ更新に失敗しました"; exit 1; }

echo ""
echo "========================================"
echo "🚀 systemd サービスを再起動します..."
echo "========================================"

# サービスを再起動（パスワードが必要な場合は入力を求める）
sudo systemctl restart tennis-bot || { echo "❌ サービスの再起動に失敗しました"; exit 1; }

# 少し待機してからサービスの状態を確認
sleep 2

# サービスの状態を簡潔に表示
echo ""
echo "✅ 再起動完了！サービスの状態:"
sudo systemctl status tennis-bot --no-pager -l | head -n 10

# 直近のログを表示（Ctrl+Cで抜ける）
echo ""
echo "========================================"
echo "📋 直近のログを表示します (Ctrl+C で終了)"
echo "========================================"
sudo journalctl -u tennis-bot -n 30 -f
