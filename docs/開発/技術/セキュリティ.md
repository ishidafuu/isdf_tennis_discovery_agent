# セキュリティ考慮事項

## 認証情報の管理

- **環境変数を直接コミットしない**: `.env`ファイルは必ず`.gitignore`に追加
- **トークンのローテーション**: 定期的にAPIキーを更新（推奨: 3ヶ月ごと）
- **最小権限の原則**: Discord Botには必要最低限の権限のみを付与

---

## Discord Bot の権限設定

```
必須権限:
✅ Send Messages
✅ Read Message History
✅ Attach Files
✅ Add Reactions

不要な権限（付与しない）:
❌ Administrator
❌ Manage Server
❌ Manage Channels
❌ Manage Messages
```

---

## データプライバシー

- **ローカルファーストの設計**: データはObsidian Vault（ローカル）に保存
- **GitHubリポジトリ**: プライベートリポジトリを推奨
- **Gemini APIへの送信データ**: 音声とテキストのみ、個人情報は最小限に

---

## 入力のバリデーション

```python
def validate_channel_name(channel_name: str) -> bool:
    """チャンネル名のバリデーション"""
    allowed_channels = [
        "壁打ち", "スクール", "試合",
        "フリー練習", "振り返り", "質問", "分析"
    ]
    return channel_name in allowed_channels

def sanitize_filename(filename: str) -> str:
    """ファイル名のサニタイズ（パストラバーサル対策）"""
    import re
    # 危険な文字を除去
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # パストラバーサル対策
    sanitized = sanitized.replace('..', '')
    return sanitized

def validate_file_size(size: int, max_mb: int = 20) -> bool:
    """ファイルサイズのバリデーション"""
    max_bytes = max_mb * 1024 * 1024
    return size <= max_bytes
```

---

## APIキーの漏洩対策

- **ログにAPIキーを出力しない**: ログレベルがDEBUGでも秘匿
- **エラーメッセージにキーを含めない**
- **定期的なキー使用量の監視**: Gemini ConsoleとDiscord Developer Portalで確認

---

## 環境変数の検証

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

## .gitignore の設定

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

# キャッシュ
__pycache__/
*.pyc
.pytest_cache/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## エラーハンドリング

```python
import logging

# ロガーの設定（APIキーをマスク）
class SecureFormatter(logging.Formatter):
    """APIキーをマスクするフォーマッター"""

    SENSITIVE_PATTERNS = [
        (r'AIza[A-Za-z0-9_-]{35}', '[GEMINI_API_KEY]'),
        (r'[A-Za-z0-9]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}', '[DISCORD_TOKEN]'),
    ]

    def format(self, record):
        message = super().format(record)
        import re
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message)
        return message

# 使用例
handler = logging.StreamHandler()
handler.setFormatter(SecureFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger = logging.getLogger('tennis_bot')
logger.addHandler(handler)
```

---

## セキュリティチェックリスト

### 開発時
- [ ] `.env`が`.gitignore`に含まれている
- [ ] APIキーがコードにハードコードされていない
- [ ] ログにAPIキーが出力されない

### デプロイ時
- [ ] GitHubリポジトリがプライベートに設定されている
- [ ] Discord Botの権限が最小限に設定されている
- [ ] 環境変数が正しく設定されている

### 運用時
- [ ] APIキーの使用量を定期的に確認
- [ ] 不審なアクセスがないか監視
- [ ] 定期的にAPIキーをローテーション

---

## 次のドキュメント

- [../setup/index.md](../setup/index.md) - セットアップガイド
