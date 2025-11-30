# Discord Botの作成

## 概要

Tennis Discovery Agent用のDiscord Botを作成し、サーバーに追加するガイドです。

---

## 1. Discord Developer Portalでアプリケーション作成

### 1.1 Developer Portalにアクセス

1. [Discord Developer Portal](https://discord.com/developers/applications) を開く
2. Discordアカウントでログイン

### 1.2 新しいアプリケーションを作成

1. 「New Application」をクリック
2. アプリケーション名を入力（例: `Tennis Discovery Agent`）
3. 「Create」をクリック

---

## 2. Botの設定

### 2.1 Bot Tokenの取得

1. 左メニューから「Bot」を選択
2. 「Add Bot」をクリック（まだの場合）
3. 「Token」セクションの「Reset Token」をクリック
4. 表示されたトークンをコピーして安全な場所に保存

**重要:** トークンは一度しか表示されません。紛失した場合は再生成が必要です。

### 2.2 Privileged Gateway Intentsの設定

「Bot」ページの「Privileged Gateway Intents」セクションで以下を有効化：

```
✅ PRESENCE INTENT
✅ SERVER MEMBERS INTENT
✅ MESSAGE CONTENT INTENT
```

---

## 3. 権限の設定

### 3.1 必要な権限

「OAuth2」→「URL Generator」で以下を選択：

**Scopes:**
```
✅ bot
✅ applications.commands
```

**Bot Permissions:**
```
✅ Send Messages
✅ Send Messages in Threads
✅ Embed Links
✅ Attach Files
✅ Read Message History
✅ Add Reactions
✅ Use External Emojis
```

### 3.2 招待URLの生成

1. 上記の権限を選択後、ページ下部にURLが生成される
2. このURLをコピー

---

## 4. サーバーへの追加

### 4.1 Botをサーバーに追加

1. 生成した招待URLをブラウザで開く
2. 追加先のサーバーを選択
3. 「認証」をクリック

### 4.2 サーバーでチャンネルを作成

以下のテキストチャンネルを作成：

```
リアルタイム記録
├── #壁打ち
├── #スクール
├── #試合
├── #フリー練習
└── #振り返り

レビュー
└── #週次レビュー

ナレッジ（Phase 2以降）
├── #質問
└── #分析
```

---

## 5. Admin User IDの取得

### 5.1 Discord開発者モードを有効化

1. Discordの設定を開く
2. 「アプリの設定」→「詳細設定」
3. 「開発者モード」をON

### 5.2 User IDをコピー

1. 自分のアイコンを右クリック
2. 「IDをコピー」をクリック

このIDは `.env` の `ADMIN_USER_ID` に設定します。

---

## 6. 環境変数の設定

取得した情報を `.env` ファイルに設定：

```env
# Discord
DISCORD_BOT_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_user_id_here
```

---

## トラブルシューティング

### Botがオンラインにならない

1. Tokenが正しいか確認
2. Intentsが有効になっているか確認
3. ネットワーク接続を確認

### メッセージを受信できない

1. MESSAGE CONTENT INTENTが有効か確認
2. Botに適切な権限があるか確認
3. チャンネルでBotが発言できるか確認

---

## 次のステップ

- [Gemini API設定](02-gemini-api.md)
