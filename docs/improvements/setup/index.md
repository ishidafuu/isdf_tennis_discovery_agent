# セットアップガイド

## 概要

Tennis Discovery Agentの環境構築ガイドです。

---

## 内容一覧

| ドキュメント | 説明 |
|-------------|------|
| [01-discord-bot.md](01-discord-bot.md) | Discord Bot作成とAPIキー取得 |
| [02-gemini-api.md](02-gemini-api.md) | Gemini API設定 |
| [03-obsidian.md](03-obsidian.md) | Obsidianセットアップ |
| [04-raspberry-pi.md](04-raspberry-pi.md) | Raspberry Pi環境構築 |
| [05-environment.md](05-environment.md) | 環境変数と設定ファイル |

---

## クイックスタート

### 必要なもの

| 項目 | 必須 | 説明 |
|------|------|------|
| Discord アカウント | ✅ | Bot作成に必要 |
| Google アカウント | ✅ | Gemini API利用に必要 |
| GitHub アカウント | 推奨 | バックアップに使用 |
| Raspberry Pi | 推奨 | 常時稼働用（PCでも可） |

### セットアップの流れ

```
1. Discord Bot作成
   └─ Discord Developer Portalでアプリケーション作成
   └─ Bot Tokenを取得

2. Gemini API設定
   └─ Google AI Studioでキーを取得
   └─ 無料枠で十分

3. Obsidianセットアップ
   └─ Vaultを作成
   └─ プラグインをインストール

4. 実行環境の準備
   └─ Raspberry Pi または PC
   └─ 依存関係のインストール

5. 起動・テスト
   └─ Botを起動
   └─ Discordから音声メモを送信
```

---

## 想定コスト

### 初期費用

| 項目 | 費用 | 備考 |
|------|------|------|
| Raspberry Pi 4 | ¥8,000〜 | 常時稼働する場合 |
| microSD (32GB) | ¥1,000〜 | 16GB以上推奨 |
| 電源アダプター | ¥1,500〜 | 5V/3A推奨 |

**PCで運用する場合:** 初期費用なし

### 月額費用

| 項目 | 費用 | 備考 |
|------|------|------|
| 電気代（Raspberry Pi） | ¥50〜100 | 3W×24h |
| Gemini API | 無料 | 無料枠で十分 |
| Discord | 無料 | |
| GitHub | 無料 | プライベートリポジトリ |

**合計:** 月額¥50〜100程度

---

## 次のステップ

1. [Discord Bot作成](01-discord-bot.md) から始めてください
