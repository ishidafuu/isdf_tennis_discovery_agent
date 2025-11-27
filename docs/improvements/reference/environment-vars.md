# 環境変数リファレンス

## 概要

Tennis Discovery Agentで使用する環境変数の一覧です。

---

## 必須項目

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `DISCORD_BOT_TOKEN` | Discord Bot Token | `MTIz...abc` |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIza...xyz` |
| `OBSIDIAN_VAULT_PATH` | Obsidian Vaultのパス | `/home/pi/obsidian-vault` |

---

## 推奨項目

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `ADMIN_USER_ID` | 管理者のDiscord User ID | なし |
| `GITHUB_TOKEN` | GitHub Personal Access Token | なし |
| `GITHUB_REPO` | GitHubリポジトリ名 | なし |
| `GITHUB_PUSH_ENABLED` | GitHub Pushを有効化 | `true` |

---

## オプション項目

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `ENV` | 環境（development/production） | `development` |
| `LOG_LEVEL` | ログレベル | `INFO` |

---

## .envファイル例

### 開発環境

```env
# Discord
DISCORD_BOT_TOKEN=your_token_here

# AI
GEMINI_API_KEY=your_api_key_here

# Storage
OBSIDIAN_VAULT_PATH=./test-vault

# Settings
ENV=development
LOG_LEVEL=DEBUG
GITHUB_PUSH_ENABLED=false
```

### 本番環境（Raspberry Pi）

```env
# Discord
DISCORD_BOT_TOKEN=your_token_here
ADMIN_USER_ID=123456789012345678

# AI
GEMINI_API_KEY=your_api_key_here

# Storage
OBSIDIAN_VAULT_PATH=/home/pi/obsidian-vault

# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=username/tennis-notes
GITHUB_PUSH_ENABLED=true

# Settings
ENV=production
LOG_LEVEL=INFO
```

---

## 取得方法

### DISCORD_BOT_TOKEN

1. [Discord Developer Portal](https://discord.com/developers/applications)
2. アプリケーション → Bot → Token → Copy

### GEMINI_API_KEY

1. [Google AI Studio](https://aistudio.google.com/)
2. Get API key → Create API key

### ADMIN_USER_ID

1. Discord設定 → 詳細設定 → 開発者モード ON
2. 自分のアイコン右クリック → IDをコピー

### GITHUB_TOKEN

1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token → `repo` スコープを選択

---

## セキュリティ注意事項

- `.env` ファイルは `.gitignore` に必ず追加
- トークンは絶対に公開しない
- 本番環境では `ENV=production` を設定

---

## 次のステップ

- [トラブルシューティング](troubleshooting.md)
- [セットアップガイド](../setup/index.md)
