# dotenvx セットアップガイド

## 概要

Tennis Discovery Agentのデプロイに**dotenvx**を導入し、環境変数の暗号化管理とラズパイへのシームレスなデプロイを実現します。

## dotenvxとは

- 環境変数（.env）を暗号化してGitリポジトリに安全にコミット可能
- 共通鍵方式で複数環境（Mac開発環境 + ラズパイ本番環境）で同じ.envを共有
- systemdサービスと統合し、デプロイ時に自動的に復号化して起動

## アーキテクチャ

```
Mac（開発環境）                    Raspberry Pi（本番環境）
┌─────────────────┐              ┌─────────────────┐
│ .env（平文）    │              │                 │
│ ↓ dotenvx encrypt│              │                 │
│ .env（暗号化）  │─ git push ─→│ .env（暗号化）  │
│ .env.keys（鍵） │   コピー     │ .env.keys（鍵） │
└─────────────────┘              └─────────────────┘
                                         ↓
                                  systemdサービス起動
                                  dotenvx run -- python main.py
                                         ↓
                                  自動復号化＆実行
```

## セットアップ手順

### 1. Mac側の初期設定（1回のみ）

```bash
# dotenvxインストール（Node.jsが必要）
# Node.jsがない場合は先にインストール: brew install node
npm install -g @dotenvx/dotenvx

# プロジェクトディレクトリで環境変数を暗号化
cd ~/path/to/isdf_tennis_discovery_agent

# 既存の.envファイルを暗号化（鍵を自動生成）
dotenvx encrypt -f .env

# 生成された.env.keysファイルを確認
cat .env.keys
```

**重要**: `.env.keys`ファイルは暗号化鍵なので**絶対にGitにコミットしない**（`.gitignore`で除外済み）

### 2. ラズパイ側の初期設定（1回のみ）

#### 2.1 dotenvxをインストール

```bash
# Node.jsインストール
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# dotenvxインストール
sudo npm install -g @dotenvx/dotenvx

# インストール確認
dotenvx --version
```

#### 2.2 共通鍵をラズパイに配置

Mac側で生成した`.env.keys`ファイルをラズパイにコピー：

**方法1: scpでコピー**
```bash
# Mac側で実行
scp .env.keys pi@raspberrypi.local:~/isdf_tennis_discovery_agent/
```

**方法2: 手動でコピー**
```bash
# Mac側で鍵の内容を表示
cat .env.keys

# ラズパイ側で作成
nano ~/isdf_tennis_discovery_agent/.env.keys
# 上記の内容を貼り付けて保存
```

#### 2.3 鍵のパーミッション設定

```bash
# ラズパイ側で実行
cd ~/isdf_tennis_discovery_agent
chmod 600 .env.keys  # 所有者のみ読み書き可能に
```

### 3. systemdサービスの設定

#### 3.1 サービステンプレートを配置

**自動セットアップスクリプトを使用した場合**（推奨）:
- セットアップスクリプトが自動的にユーザー名とホームディレクトリを置換してインストールします
- この場合、手動での編集は不要です

**手動でインストールする場合**:
```bash
# ラズパイ側で実行
# ユーザー名とホームディレクトリを自動検出
CURRENT_USER=$(whoami)
CURRENT_HOME=$(eval echo ~$CURRENT_USER)

# プレースホルダーを実際の値に置換してコピー
sed -e "s|USER_NAME|$CURRENT_USER|g" \
    -e "s|HOME_DIR|$CURRENT_HOME|g" \
    ~/isdf_tennis_discovery_agent/deployment/systemd/tennis-bot.service \
    | sudo tee /etc/systemd/system/tennis-bot.service > /dev/null

# または手動で編集
sudo nano /etc/systemd/system/tennis-bot.service
# USER_NAME を実際のユーザー名に置換
# HOME_DIR を実際のホームディレクトリ（例: /home/ishidafuu）に置換
```

#### 3.2 サービスを有効化＆起動

```bash
# systemdに変更を認識させる
sudo systemctl daemon-reload

# サービスを有効化（起動時に自動起動）
sudo systemctl enable tennis-bot

# サービスを起動
sudo systemctl start tennis-bot

# ステータス確認
sudo systemctl status tennis-bot

# ログをリアルタイム表示
sudo journalctl -u tennis-bot -f
```

## デプロイワークフロー

### 日常的な開発フロー

#### Mac側での開発

```bash
# 1. コード修正
vim src/bot/client.py

# 2. 環境変数を変更した場合のみ暗号化
# （.envを編集した場合）
dotenvx encrypt -f .env

# 3. Gitにコミット＆プッシュ
git add .
git commit -m "Update bot logic"
git push origin main
```

#### ラズパイへのデプロイ

**自動デプロイスクリプトを使用**（推奨）:
```bash
# Mac側で実行
~/bin/pi-deploy-tennis-bot
```

**手動デプロイ**:
```bash
# ラズパイ側で実行
cd ~/isdf_tennis_discovery_agent
git pull origin main

# 依存関係を更新（requirements.txtが変更された場合）
source venv/bin/activate
pip install -r requirements.txt

# サービス再起動
sudo systemctl restart tennis-bot

# ステータス確認
sudo systemctl status tennis-bot
```

## 環境変数の管理

### 新しい環境変数を追加する

1. **Mac側で`.env`を編集**
```bash
echo "NEW_API_KEY=secret_value_here" >> .env
```

2. **再暗号化**
```bash
dotenvx encrypt -f .env
```

3. **Gitにコミット**
```bash
git add .env
git commit -m "Add NEW_API_KEY to environment"
git push
```

4. **ラズパイ側でデプロイ**
```bash
~/bin/pi-deploy-tennis-bot  # Mac側から実行
# または
cd ~/isdf_tennis_discovery_agent && git pull  # ラズパイ側で実行
sudo systemctl restart tennis-bot
```

### 環境変数を確認する

```bash
# 暗号化された.envの内容を確認
dotenvx get

# 特定の変数を確認
dotenvx get DISCORD_BOT_TOKEN
```

## トラブルシューティング

### サービスが起動しない

```bash
# 詳細ログを確認
sudo journalctl -u tennis-bot -n 50

# サービスファイルの文法チェック
sudo systemd-analyze verify /etc/systemd/system/tennis-bot.service

# 手動で起動してエラーを確認
cd ~/isdf_tennis_discovery_agent
dotenvx run -- python3 main.py
```

### ユーザー名エラー（status=217/USER）

**症状**: `Failed to determine user credentials: No such process`

これはサービスファイルで指定されたユーザー名が実際のユーザー名と異なる場合に発生します。

```bash
# 現在のユーザー名を確認
whoami
# 例: ishidafuu

# サービスファイルを修正
sudo nano /etc/systemd/system/tennis-bot.service

# User=USER_NAME の USER_NAME を実際のユーザー名に変更
# WorkingDirectory と ExecStart のパスも修正
# 例:
#   User=ishidafuu
#   WorkingDirectory=/home/ishidafuu/isdf_tennis_discovery_agent
#   ExecStart=/usr/local/bin/dotenvx run -- /home/ishidafuu/isdf_tennis_discovery_agent/venv/bin/python main.py

# 保存後、再読み込みして再起動
sudo systemctl daemon-reload
sudo systemctl restart tennis-bot
sudo systemctl status tennis-bot
```

### dotenvxが見つからないエラー

```bash
# dotenvxのパスを確認
which dotenvx

# パスが /usr/local/bin/dotenvx でない場合
# サービスファイルのExecStartを修正
sudo nano /etc/systemd/system/tennis-bot.service
# ExecStart=/actual/path/to/dotenvx run -- ...

sudo systemctl daemon-reload
sudo systemctl restart tennis-bot
```

### .env.keysが見つからないエラー

```bash
# 鍵ファイルが存在するか確認
ls -la ~/isdf_tennis_discovery_agent/.env.keys

# 存在しない場合はMac側からコピー
scp .env.keys pi@raspberrypi.local:~/isdf_tennis_discovery_agent/
```

### 環境変数が読み込まれない

```bash
# .envファイルが暗号化されているか確認
head ~/isdf_tennis_discovery_agent/.env
# "#/---BEGIN DOTENV_PUBLIC_KEY---" で始まっていればOK

# 復号化テスト
cd ~/isdf_tennis_discovery_agent
dotenvx run -- env | grep DISCORD_BOT_TOKEN
```

## セキュリティのベストプラクティス

### やるべきこと ✅

- `.env.keys`を**絶対にGitにコミットしない**
- `.env.keys`のパーミッションを`600`に設定
- 暗号化された`.env`のみをGitにコミット
- 定期的に鍵をローテーション（年1回程度）

### やってはいけないこと ❌

- `.env.keys`をSlack/Discord等で送信しない
- `.env.keys`をパブリックな場所に保存しない
- 平文の`.env`をGitにコミットしない

## よく使うコマンド一覧

```bash
# サービス管理
sudo systemctl status tennis-bot       # ステータス確認
sudo systemctl restart tennis-bot      # 再起動
sudo systemctl stop tennis-bot         # 停止
sudo systemctl start tennis-bot        # 起動
sudo journalctl -u tennis-bot -f       # ログをリアルタイム表示

# 環境変数管理
dotenvx encrypt -f .env                # 暗号化
dotenvx get                            # 全変数表示
dotenvx get VARIABLE_NAME              # 特定変数表示
dotenvx run -- python3 main.py         # 復号化して実行

# デバッグ
dotenvx run -- env                     # 全環境変数を表示
dotenvx run -- python3 -c "import os; print(os.getenv('DISCORD_BOT_TOKEN'))"  # Python経由で確認
```

## 参考リンク

- [dotenvx公式ドキュメント](https://dotenvx.com/docs)
- [dotenvx GitHub](https://github.com/dotenvx/dotenvx)
- [systemd公式ドキュメント](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
