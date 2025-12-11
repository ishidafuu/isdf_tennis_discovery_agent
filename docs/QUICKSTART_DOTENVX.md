# dotenvx クイックスタートガイド

このガイドでは、Tennis Discovery Agentにdotenvxを導入し、Raspberry Piにデプロイするまでの手順を説明します。

## 前提条件

- Mac（開発環境）
- Raspberry Pi（本番環境）
- GitHub リポジトリへのアクセス権
- SSH経由でRaspberry Piにアクセス可能

## 📋 手順の概要

1. **Mac側**: dotenvxをインストールして.envを暗号化
2. **Raspberry Pi側**: 初期セットアップを実行
3. **Mac側**: デプロイスクリプトでコードをデプロイ

---

## 1️⃣ Mac側の初期セットアップ

### 1.1 dotenvxをインストール

```bash
# Node.jsがない場合は先にインストール
brew install node

# dotenvxをグローバルインストール
npm install -g @dotenvx/dotenvx

# バージョン確認
dotenvx --version
```

### 1.2 環境変数ファイルを作成

```bash
# プロジェクトディレクトリに移動
cd ~/path/to/isdf_tennis_discovery_agent

# .env.exampleをコピーして.envを作成
cp .env.example .env

# .envを編集して実際の値を設定
nano .env
```

`.env`に以下の値を設定：
```bash
DISCORD_BOT_TOKEN=your_actual_discord_token
GEMINI_API_KEY=your_actual_gemini_api_key
GITHUB_TOKEN=your_actual_github_token
GITHUB_REPO=your_username/tennis-vault
OBSIDIAN_PATH=sessions
OBSIDIAN_VAULT_PATH=./obsidian_vault
ADMIN_USER_ID=your_discord_user_id
DEBUG=false
```

### 1.3 .envを暗号化

```bash
# .envファイルを暗号化（鍵が自動生成される）
dotenvx encrypt -f .env

# 成功すると以下のファイルが生成/更新される：
# - .env（暗号化された状態に上書き）
# - .env.keys（暗号化鍵）

# 鍵ファイルの内容を確認（後でラズパイにコピーするため）
cat .env.keys
```

**重要**: `.env.keys`の内容をメモ帳などに一時的にコピーしておいてください。

### 1.4 暗号化された.envをGitにコミット

```bash
# .env.keysは.gitignoreで除外されているので、.envのみコミット
git add .env
git commit -m "Add encrypted environment variables"
git push origin main
```

---

## 2️⃣ Raspberry Pi側の初期セットアップ

### 2.1 Raspberry Piにログイン

```bash
# Mac側から実行
ssh pi@raspberrypi.local
```

### 2.2 セットアップスクリプトを取得して実行

```bash
# リポジトリをクローン（まだの場合）
git clone https://github.com/ishidafuu/isdf_tennis_discovery_agent.git
cd isdf_tennis_discovery_agent

# セットアップスクリプトを実行
bash deployment/scripts/setup-raspberry-pi.sh
```

このスクリプトは以下を自動実行します：
- システムパッケージの更新
- Node.js、dotenvxのインストール
- Python仮想環境の作成
- 依存関係のインストール
- systemdサービスの登録（ユーザー名とホームディレクトリを自動検出）

### 2.3 .env.keysファイルを配置

セットアップスクリプト中に.env.keysの入力を求められます。

**方法1: 対話的に入力**
スクリプト中に「Do you want to paste the .env.keys content now?」と聞かれるので、`y`を入力し、Mac側でコピーした`.env.keys`の内容を貼り付けます。

**方法2: 後からscpでコピー**
セットアップ後、Mac側から以下を実行：
```bash
# Mac側で実行
scp .env.keys pi@raspberrypi.local:~/isdf_tennis_discovery_agent/
```

### 2.4 サービスの動作確認

```bash
# サービスのステータス確認
sudo systemctl status tennis-bot

# ログをリアルタイム表示
sudo journalctl -u tennis-bot -f
```

「Active: active (running)」と表示されていれば成功です！

---

## 3️⃣ Mac側からのデプロイ

### 3.1 デプロイスクリプトをMacのPATHに追加（推奨）

```bash
# Mac側で実行
mkdir -p ~/bin

# プロジェクトのスクリプトをコピー
cp ~/path/to/isdf_tennis_discovery_agent/deployment/scripts/pi-deploy-tennis-bot.sh ~/bin/pi-deploy-tennis-bot

# 実行権限を付与
chmod +x ~/bin/pi-deploy-tennis-bot

# PATHに追加（.zshrcまたは.bashrcに追記）
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 3.2 コードを修正してデプロイ

```bash
# コードを修正
vim src/bot/client.py

# デプロイスクリプトを実行
pi-deploy-tennis-bot
```

デプロイスクリプトは以下を自動実行します：
1. ローカルの変更をGitにコミット＆プッシュ
2. Raspberry PiでGitプル
3. Python依存関係の更新
4. サービスの再起動
5. ステータス確認

---

## 4️⃣ 環境変数の更新

環境変数を追加・変更する場合：

```bash
# Mac側で.envを編集
# （まず復号化）
dotenvx run -- cat .env.example > .env.tmp
# または直接編集

# .envに新しい変数を追加
echo "NEW_VARIABLE=new_value" >> .env

# 再暗号化
dotenvx encrypt -f .env

# Gitにコミット
git add .env
git commit -m "Add NEW_VARIABLE to environment"
git push

# デプロイ
pi-deploy-tennis-bot
```

---

## 🔍 トラブルシューティング

### サービスが起動しない

```bash
# 詳細ログを確認
sudo journalctl -u tennis-bot -n 50

# 手動で起動してエラーを確認
cd ~/isdf_tennis_discovery_agent
source venv/bin/activate
dotenvx run -- python main.py
```

### ユーザー名エラー（status=217/USER）

**症状**: ログに`Failed to determine user credentials: No such process`と表示される

**原因**: systemdサービスファイルのユーザー名が実際のユーザー名と異なる

**対処法**:
```bash
# 現在のユーザー名を確認
whoami

# サービスファイルを修正
sudo nano /etc/systemd/system/tennis-bot.service
# User=USER_NAME を実際のユーザー名に変更
# WorkingDirectory と ExecStart のパスも修正

# 例: ユーザー名が ishidafuu の場合
#   User=ishidafuu
#   WorkingDirectory=/home/ishidafuu/isdf_tennis_discovery_agent
#   ExecStart=/usr/local/bin/dotenvx run -- /home/ishidafuu/isdf_tennis_discovery_agent/venv/bin/python main.py

# 保存後、再起動
sudo systemctl daemon-reload
sudo systemctl restart tennis-bot
sudo systemctl status tennis-bot
```

### .env.keysが見つからない

```bash
# ラズパイ側で確認
ls -la ~/isdf_tennis_discovery_agent/.env.keys

# 存在しない場合はMac側からコピー
# Mac側で実行:
scp .env.keys pi@raspberrypi.local:~/isdf_tennis_discovery_agent/
```

### dotenvxが見つからない

```bash
# ラズパイ側でパスを確認
which dotenvx

# /usr/local/bin/dotenvx にない場合
# サービスファイルのExecStartを修正
sudo nano /etc/systemd/system/tennis-bot.service
# ExecStartの/usr/local/bin/dotenvxを実際のパスに変更

sudo systemctl daemon-reload
sudo systemctl restart tennis-bot
```

---

## 📚 次のステップ

- [詳細なdotenvxセットアップガイド](./DOTENVX_SETUP.md)
- [プロジェクト全体のドキュメント](../CLAUDE.md)
- [セットアップガイド](../SETUP.md)

---

## 🎉 完了！

これでdotenvxを使った安全な環境変数管理とシームレスなデプロイが可能になりました。

```bash
# よく使うコマンドまとめ

# Mac側
pi-deploy-tennis-bot                    # デプロイ
dotenvx encrypt -f .env                 # 環境変数暗号化
dotenvx get VARIABLE_NAME               # 環境変数確認

# Raspberry Pi側
sudo systemctl status tennis-bot        # ステータス確認
sudo systemctl restart tennis-bot       # 再起動
sudo journalctl -u tennis-bot -f        # ログ表示
```
