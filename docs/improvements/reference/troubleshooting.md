# トラブルシューティング

## 概要

Tennis Discovery Agentでよくある問題と解決方法です。

---

## Bot関連

### Botがオンラインにならない

**症状:** Discordサーバーでbotがオフライン表示

**確認項目:**
1. `DISCORD_BOT_TOKEN` が正しいか
2. Intents（MESSAGE_CONTENT等）が有効か
3. ネットワーク接続

**解決方法:**
```bash
# ログを確認
sudo journalctl -u tennis-bot -n 50

# 手動で起動してエラーを確認
cd ~/tennis-discovery-agent
source venv/bin/activate
python3 src/main.py
```

### メッセージを受信できない

**症状:** 音声/テキストを送信してもbotが反応しない

**確認項目:**
1. MESSAGE CONTENT INTENTが有効か（Discord Developer Portal）
2. Botにチャンネルの読み取り権限があるか

**解決方法:**
1. Developer Portal → Bot → Privileged Gateway Intents
2. `MESSAGE CONTENT INTENT` を有効化
3. Botを再起動

---

## API関連

### Gemini APIエラー

**症状:** 文字起こしや構造化が失敗

**確認項目:**
1. `GEMINI_API_KEY` が正しいか
2. APIのレート制限に達していないか

**解決方法:**
```python
# APIキーのテスト
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('こんにちは')
print(response.text)
```

### レート制限エラー

**症状:** `quota exceeded` または `rate limit` エラー

**確認項目:**
- 無料枠: 15 RPM（リクエスト/分）

**解決方法:**
1. リクエスト間隔を空ける（5秒以上）
2. バッチ処理を検討
3. 有料プランへのアップグレード

---

## ストレージ関連

### Obsidianにファイルが保存されない

**症状:** Discordでは成功メッセージが出るが、Obsidianにファイルがない

**確認項目:**
1. `OBSIDIAN_VAULT_PATH` が正しいパスか
2. 書き込み権限があるか

**解決方法:**
```bash
# パスの確認
ls -la /home/pi/obsidian-vault

# 権限の確認
touch /home/pi/obsidian-vault/test.md
rm /home/pi/obsidian-vault/test.md
```

### GitHub Pushが失敗する

**症状:** ローカルには保存されるが、GitHubにPushされない

**確認項目:**
1. `GITHUB_TOKEN` が有効か
2. `GITHUB_REPO` が正しいか
3. リポジトリへの書き込み権限があるか

**解決方法:**
```bash
# 手動でPushを試行
cd /home/pi/obsidian-vault
git status
git push origin main

# 認証エラーの場合
git remote set-url origin https://<TOKEN>@github.com/<USER>/<REPO>.git
```

---

## Raspberry Pi関連

### サービスが起動しない

**症状:** `systemctl status tennis-bot` がfailed

**確認項目:**
1. サービスファイルの設定
2. Pythonパス
3. 仮想環境

**解決方法:**
```bash
# サービスファイルを確認
sudo cat /etc/systemd/system/tennis-bot.service

# パスが正しいか確認
ls /home/pi/tennis-discovery-agent/venv/bin/python3
ls /home/pi/tennis-discovery-agent/src/main.py

# デーモンをリロード
sudo systemctl daemon-reload
sudo systemctl restart tennis-bot
```

### メモリ不足

**症状:** Botが突然停止する、応答が遅い

**確認項目:**
```bash
free -h
```

**解決方法:**
```bash
# スワップを増やす
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 高温警告

**症状:** Botの動作が不安定

**確認項目:**
```bash
vcgencmd measure_temp
# 正常: 40-70°C
# 警告: 80°C以上
```

**解決方法:**
1. ヒートシンクを装着
2. ファンを追加
3. 負荷の高い処理を見直し

---

## よくある質問

### Q: 音声が長すぎると失敗する

**A:** Discordの音声メッセージは25MB、10分程度が上限です。長い場合は分割して送信してください。

### Q: 特定のチャンネルでだけ動作しない

**A:** チャンネル名が正確に一致しているか確認してください。日本語チャンネル名（`壁打ち`、`スクール`等）の場合、全角/半角の違いに注意。

### Q: Bot復旧後、DMが処理されない

**A:** `ADMIN_USER_ID` が正しく設定されているか確認してください。また、DMの履歴上限（50件）を超えている場合は処理されません。

---

## ログの確認方法

### systemdログ

```bash
# リアルタイム
sudo journalctl -u tennis-bot -f

# 最新100行
sudo journalctl -u tennis-bot -n 100
```

### アプリケーションログ

```bash
# ログファイルがある場合
tail -f /home/pi/tennis-discovery-agent/logs/app.log
```

---

## 次のステップ

- [環境変数](environment-vars.md)
- [セットアップガイド](../setup/index.md)
