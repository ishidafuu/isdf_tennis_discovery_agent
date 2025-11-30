# 環境変数と設定ファイル

## 概要

Tennis Discovery Agentの環境変数と設定ファイルの完全なリファレンスです。

---

## .envファイル

### 必須項目

```env
# Discord Bot Token
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Obsidian Vault Path
OBSIDIAN_VAULT_PATH=/path/to/obsidian/vault
```

### 推奨項目

```env
# Admin User ID（DMバックアップ機能用）
ADMIN_USER_ID=123456789012345678

# GitHub設定（バックアップ用）
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=username/tennis-notes
GITHUB_PUSH_ENABLED=true
```

### オプション項目

```env
# 環境設定
ENV=production  # development / production
LOG_LEVEL=INFO  # DEBUG / INFO / WARNING / ERROR
```

---

## 環境別の設定

### 開発環境（development）

```env
ENV=development
LOG_LEVEL=DEBUG
OBSIDIAN_VAULT_PATH=./test-vault
GITHUB_PUSH_ENABLED=false
```

### 本番環境（production）

```env
ENV=production
LOG_LEVEL=INFO
OBSIDIAN_VAULT_PATH=/home/pi/obsidian-vault
GITHUB_PUSH_ENABLED=true
```

---

## 設定の検証コード

```python
# src/config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    discord_token: str
    gemini_api_key: str
    github_token: str
    github_repo: str
    vault_path: str
    env: str
    log_level: str
    github_push_enabled: bool
    admin_user_id: str

    @classmethod
    def from_env(cls) -> 'Config':
        """環境変数から設定を読み込み、検証する"""

        required_vars = [
            'DISCORD_BOT_TOKEN',
            'GEMINI_API_KEY',
            'OBSIDIAN_VAULT_PATH'
        ]

        missing = [v for v in required_vars if not os.getenv(v)]
        if missing:
            raise ValueError(f"必須の環境変数が設定されていません: {', '.join(missing)}")

        return cls(
            discord_token=os.getenv('DISCORD_BOT_TOKEN'),
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            github_token=os.getenv('GITHUB_TOKEN', ''),
            github_repo=os.getenv('GITHUB_REPO', ''),
            vault_path=os.getenv('OBSIDIAN_VAULT_PATH'),
            env=os.getenv('ENV', 'development'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            github_push_enabled=os.getenv('GITHUB_PUSH_ENABLED', 'true').lower() == 'true',
            admin_user_id=os.getenv('ADMIN_USER_ID', '')
        )
```

---

## .env.example

リポジトリにコミットするサンプルファイル：

```env
# Discord Bot Token
# Discord Developer Portalで取得
DISCORD_BOT_TOKEN=

# Gemini API Key
# Google AI Studioで取得
GEMINI_API_KEY=

# Obsidian Vault Path
# Obsidian Vaultのパス
OBSIDIAN_VAULT_PATH=/path/to/obsidian/vault

# Admin User ID（オプション）
# DMバックアップ機能用、Discord Developer Modeで取得
ADMIN_USER_ID=

# GitHub設定（オプション）
GITHUB_TOKEN=
GITHUB_REPO=username/tennis-notes
GITHUB_PUSH_ENABLED=true

# 環境設定
ENV=development
LOG_LEVEL=INFO
```

---

## .gitignore

```gitignore
# 環境変数
.env
.env.local
.env.*.local

# 認証情報
*.pem
*.key
credentials.json

# ログ
*.log
logs/

# Python
__pycache__/
*.pyc
*.pyo
venv/
.venv/
.pytest_cache/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Obsidian（ローカルのみ）
obsidian-vault/
test-vault/
```

---

## APIキーの取得方法

### Discord Bot Token

1. [Discord Developer Portal](https://discord.com/developers/applications) へアクセス
2. アプリケーションを作成
3. Bot → Token → Copy

### Gemini API Key

1. [Google AI Studio](https://aistudio.google.com/) へアクセス
2. Get API key → Create API key

### GitHub Token（オプション）

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Scopeで `repo` を選択

### Admin User ID

1. Discord設定 → 詳細設定 → 開発者モード ON
2. 自分のアイコンを右クリック → IDをコピー

---

## セットアップ完了チェックリスト

- [ ] `.env` ファイルが作成されている
- [ ] `DISCORD_BOT_TOKEN` が設定されている
- [ ] `GEMINI_API_KEY` が設定されている
- [ ] `OBSIDIAN_VAULT_PATH` が正しいパスに設定されている
- [ ] `.env` が `.gitignore` に含まれている
- [ ] 依存関係がインストールされている
- [ ] Botが正常に起動する
