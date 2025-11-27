# Discord Bot セットアップ完全ガイド

このガイドでは、Discord Botを作成してサーバーに招待する手順を説明します。

## 📋 前提条件

- Discordアカウント（無料）
- 管理者権限を持つDiscordサーバー（テスト用に新規作成推奨）

---

## ステップ1: Discord Developer Portal にアクセス

1. ブラウザで https://discord.com/developers/applications を開く
2. Discordアカウントでログイン

## ステップ2: 新しいアプリケーションを作成

1. 右上の **「New Application」** ボタンをクリック
2. 名前を入力（例：`Tennis Discovery Agent`）
3. 利用規約に同意 → **「Create」**

## ステップ3: Bot を追加

1. 左メニュー → **「Bot」**
2. **「Add Bot」** → **「Yes, do it!」**

## ステップ4: Bot Token を取得

⚠️ **重要**: トークンは秘密情報です。誰にも共有しないでください！

1. **「TOKEN」** セクション → **「Reset Token」**
2. **「Yes, do it!」** で確認
3. 表示されたトークンを **コピー**
4. プロジェクトの `.env` ファイルに保存：

```bash
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.AbCdEf.GhIjKlMnOpQrStUvWxYz1234567890
```

**注意**: 上記は例です。実際のトークンを貼り付けてください。

## ステップ5: Privileged Gateway Intents を有効化

⚠️ **必須**: この設定をしないとメッセージを受信できません！

1. Botページを下にスクロール
2. **「Privileged Gateway Intents」** セクション
3. 以下を **ON（青色）** にする：
   - ✅ **MESSAGE CONTENT INTENT**
4. **「Save Changes」** をクリック

## ステップ6: 招待URL を生成

1. 左メニュー → **「OAuth2」** → **「URL Generator」**

2. **SCOPES** で以下をチェック：
   ```
   ✅ bot
   ```

3. **BOT PERMISSIONS** で以下をチェック：
   ```
   ✅ Send Messages
   ✅ Send Messages in Threads
   ✅ Embed Links
   ✅ Attach Files
   ✅ Read Message History
   ✅ Add Reactions
   ✅ Use Slash Commands
   ```

4. ページ下部の **「GENERATED URL」** をコピー

## ステップ7: Botをサーバーに招待

1. コピーしたURLをブラウザで開く
2. **招待先サーバー** を選択
   - 管理者権限が必要
   - テスト用に新しいサーバーを作成してもOK
3. **「認証」** をクリック
4. 権限を確認 → **「認証」**
5. reCAPTCHA認証を完了

## ステップ8: 確認

1. Discordアプリでサーバーを開く
2. 右側のメンバーリストに **「Tennis Discovery Agent」** が表示される
3. まだ **オフライン（灰色）** 状態

---

## 🚀 次のステップ

Botを起動してオンラインにする：

```bash
# 仮想環境がまだの場合
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt

# Botを起動
python main.py
```

正常に起動すると：
- ターミナルに `✅ Bot is ready!` と表示される
- DiscordでBotが **オンライン（緑）** になる

---

## 🎤 テスト方法

1. **テキストメッセージを送信**
   - Discordのチャンネルで `こんにちは` と送信
   - Botは反応しません（音声メッセージのみ処理）

2. **音声メッセージを送信（スマホ推奨）**
   - Discordアプリを開く
   - メッセージ入力欄の **マイクボタンを長押し**
   - 「今日はサーブの練習をしました」と話す
   - 手を離して送信
   - Botが処理を開始します！

---

## ❌ トラブルシューティング

### Botがオフラインのまま

**原因**:
- Botトークンが正しくない
- インターネット接続の問題

**対処**:
```bash
# .envファイルを確認
cat .env | grep DISCORD_BOT_TOKEN

# トークンの前後にスペースがないか確認
# 正しい形式: DISCORD_BOT_TOKEN=MTIzNDU...
```

### 音声メッセージに反応しない

**原因**:
- MESSAGE CONTENT INTENT が無効

**対処**:
1. Developer Portal → Bot
2. MESSAGE CONTENT INTENT を ON
3. Save Changes
4. Botを再起動

### 403 Forbidden エラー

**原因**:
- Bot権限が不足

**対処**:
1. Botをサーバーから削除（キック）
2. OAuth2 URL Generatorで権限を再確認
3. 新しいURLで再招待

---

## 🔐 セキュリティ

- ✅ Botトークンは `.env` ファイルにのみ保存
- ✅ `.env` は `.gitignore` に含まれている
- ❌ Botトークンをコードに直接書かない
- ❌ Botトークンをスクリーンショットで共有しない
- ❌ GitHubにトークンをコミットしない

トークンが漏洩した場合：
1. Developer Portal → Bot
2. **「Reset Token」** で新しいトークンを発行
3. `.env` を更新

---

## 📚 参考リンク

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Bot Guide](https://discord.com/developers/docs/intro)
