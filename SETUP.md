# 🎾 Tennis Discovery Agent - セットアップガイド

## 📋 事前準備

### 1. APIキーとトークンの取得

以下の3つが必要です：

#### ✅ Gemini API Key（取得済み）
- [Google AI Studio](https://aistudio.google.com/app/apikey)
- モデル: Gemini 1.5 Flash

#### 🤖 Discord Bot Token（未取得の場合）
1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. アプリケーション名を入力（例：Tennis Discovery Agent）
4. 左メニューから「Bot」を選択
5. 「Add Bot」をクリック
6. 「Token」セクションで「Reset Token」→ トークンをコピー
7. **重要**: 「Privileged Gateway Intents」で以下を有効化：
   - ✅ MESSAGE CONTENT INTENT（メッセージ内容の読み取り）
8. 左メニューから「OAuth2」→「URL Generator」
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Messages/View Channels`, `Attach Files`, `Use Slash Commands`
   - 生成されたURLをブラウザで開いてBotを招待

#### 🔐 GitHub Personal Access Token（未取得の場合）
1. [GitHub Settings > Personal access tokens](https://github.com/settings/tokens)
2. 「Generate new token (classic)」をクリック
3. Note: `Tennis Discovery Agent`
4. Expiration: 任意（`No expiration`推奨）
5. Scopes: ✅ `repo`（Full control of private repositories）
6. 「Generate token」→ トークンをコピー

---

## 🔧 環境変数の設定

### ステップ1: .envファイルの作成

**⚠️ 重要: APIキーは絶対にGitにコミットしないでください**

ターミナルで以下を実行（Mac/Linux）：
```bash
cp .env.example .env
```

Windows（PowerShell）の場合：
```powershell
Copy-Item .env.example .env
```

### ステップ2: 実際の値を入力

`.env`ファイルをテキストエディタで開き、以下のように実際の値に置き換えます：

```bash
# Discord Bot Token
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.AbCdEf.GhIjKlMnOpQrStUvWxYz1234567890

# Google Gemini API Key
GEMINI_API_KEY=AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq

# GitHub Personal Access Token
GITHUB_TOKEN=ghp_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

# GitHub Repository（Obsidian Vault用のリポジトリを指定）
GITHUB_REPO=ishidafuu/tennis-vault

# Obsidian保存先ディレクトリ
OBSIDIAN_PATH=sessions

# デバッグモード
DEBUG=true
```

### ステップ3: 確認

`.env`ファイルが`.gitignore`に含まれていることを確認：
```bash
git status
```

→ `.env`が**表示されない**ことを確認（表示される場合は設定ミス）

---

## 📦 依存パッケージのインストール

仮想環境を作成してパッケージをインストール：

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化（Mac/Linux）
source venv/bin/activate

# 仮想環境の有効化（Windows）
venv\Scripts\activate

# パッケージのインストール
pip install -r requirements.txt
```

---

## ✅ 動作確認（Phase 1実装後）

Phase 1の実装が完了したら、以下で起動：

```bash
python main.py
```

期待される動作：
1. Discordボットがオンラインになる
2. ボイスメッセージを送信すると、Geminiが処理
3. Obsidian形式のMarkdownがGitHubにPushされる

---

## 🔍 トラブルシューティング

### Discordボットが起動しない
- `.env`のトークンが正しいか確認
- Developer PortalでMESSAGE CONTENT INTENTが有効か確認

### Gemini APIエラー
- APIキーが有効か[AI Studio](https://aistudio.google.com/)で確認
- 無料枠の制限に達していないか確認

### GitHub Pushが失敗する
- Personal Access Tokenの権限に`repo`が含まれているか確認
- リポジトリ名が`username/repo-name`形式で正しいか確認

---

## 📚 次のステップ

環境設定が完了したら、Phase 1の実装を開始します！
