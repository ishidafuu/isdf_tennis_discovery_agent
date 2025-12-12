#!/bin/bash
# migrate_env_config.sh
# 環境変数を .env と .env.config に分離するための移行スクリプト

set -e

echo "================================================"
echo "環境変数分離移行スクリプト"
echo "================================================"
echo ""
echo "このスクリプトは現在の .env から値を取得して、"
echo "機密情報と非機密情報を分離します。"
echo ""

# dotenvxが利用可能か確認
if ! command -v dotenvx &> /dev/null; then
    echo "❌ エラー: dotenvx が見つかりません。"
    echo "インストール方法: curl -sfS https://dotenvx.sh | sh"
    exit 1
fi

# 現在のディレクトリを保存
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "プロジェクトディレクトリ: $PROJECT_DIR"
echo ""

# .env ファイルが存在するか確認
if [ ! -f ".env" ]; then
    echo "❌ エラー: .env ファイルが見つかりません。"
    exit 1
fi

echo "================================================"
echo "ステップ 1: 現在の環境変数を取得"
echo "================================================"
echo ""

# 非機密情報を取得
echo "非機密情報の値を取得中..."
GITHUB_REPO=$(dotenvx get GITHUB_REPO 2>/dev/null || echo "")
OBSIDIAN_PATH=$(dotenvx get OBSIDIAN_PATH 2>/dev/null || echo "sessions")
ADMIN_USER_ID=$(dotenvx get ADMIN_USER_ID 2>/dev/null || echo "")
DEBUG=$(dotenvx get DEBUG 2>/dev/null || echo "false")

echo "  GITHUB_REPO: ${GITHUB_REPO:-（未設定）}"
echo "  OBSIDIAN_PATH: ${OBSIDIAN_PATH}"
echo "  ADMIN_USER_ID: ${ADMIN_USER_ID:-（未設定）}"
echo "  DEBUG: ${DEBUG}"
echo ""

echo "================================================"
echo "ステップ 2: .env.config に非機密情報を設定"
echo "================================================"
echo ""

# .env.config を更新
if [ -n "$GITHUB_REPO" ]; then
    sed -i.bak "s|^GITHUB_REPO=.*|GITHUB_REPO=$GITHUB_REPO|" .env.config
    echo "✅ GITHUB_REPO を設定しました"
fi

if [ -n "$OBSIDIAN_PATH" ]; then
    sed -i.bak "s|^OBSIDIAN_PATH=.*|OBSIDIAN_PATH=$OBSIDIAN_PATH|" .env.config
    echo "✅ OBSIDIAN_PATH を設定しました"
fi

if [ -n "$ADMIN_USER_ID" ]; then
    sed -i.bak "s|^ADMIN_USER_ID=.*|ADMIN_USER_ID=$ADMIN_USER_ID|" .env.config
    echo "✅ ADMIN_USER_ID を設定しました"
fi

if [ -n "$DEBUG" ]; then
    sed -i.bak "s|^DEBUG=.*|DEBUG=$DEBUG|" .env.config
    echo "✅ DEBUG を設定しました"
fi

# バックアップファイルを削除
rm -f .env.config.bak

echo ""
echo "================================================"
echo "ステップ 3: 新しい .env ファイルを作成"
echo "================================================"
echo ""

# 現在の .env をバックアップ
cp .env .env.backup
echo "✅ 現在の .env を .env.backup にバックアップしました"

# 機密情報のみを含む新しい .env を作成
echo "新しい .env ファイルを作成中..."

# 機密情報を取得
DISCORD_BOT_TOKEN=$(dotenvx get DISCORD_BOT_TOKEN 2>/dev/null || echo "")
GEMINI_API_KEY=$(dotenvx get GEMINI_API_KEY 2>/dev/null || echo "")
GITHUB_TOKEN=$(dotenvx get GITHUB_TOKEN 2>/dev/null || echo "")

# 新しい .env ファイルを作成（平文）
cat > .env << EOF
# .env
# Tennis Discovery Agent - 機密情報用環境変数
# このファイルは dotenvx で暗号化してGitにコミットします

# Discord Bot Token
DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN

# Google Gemini API Key
GEMINI_API_KEY=$GEMINI_API_KEY

# GitHub Personal Access Token
GITHUB_TOKEN=$GITHUB_TOKEN
EOF

echo "✅ 新しい .env ファイルを作成しました（平文）"
echo ""

echo "================================================"
echo "ステップ 4: .env を暗号化"
echo "================================================"
echo ""

# 暗号化を実行
echo "dotenvx で暗号化中..."
dotenvx encrypt -f .env

echo ""
echo "================================================"
echo "✅ 移行完了！"
echo "================================================"
echo ""
echo "次の手順:"
echo "1. .env.config の内容を確認し、必要に応じて調整してください"
echo "2. .env が正しく暗号化されているか確認してください"
echo "3. 動作確認: python check_setup.py"
echo "4. 問題がなければ .env.backup を削除してください"
echo ""
echo "ファイル一覧:"
echo "  .env          - 機密情報（暗号化済み）"
echo "  .env.config   - 非機密情報（平文）"
echo "  .env.backup   - バックアップ（削除推奨）"
echo ""
