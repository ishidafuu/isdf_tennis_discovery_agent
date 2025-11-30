# Gemini API 設定

## 概要

Google Gemini APIを使用して、音声の文字起こしとテキストの構造化を行います。

---

## 1. Google AI Studioでキーを取得

### 1.1 AI Studioにアクセス

1. [Google AI Studio](https://aistudio.google.com/) を開く
2. Googleアカウントでログイン

### 1.2 APIキーの作成

1. 左メニューの「Get API key」をクリック
2. 「Create API key」をクリック
3. プロジェクトを選択（または新規作成）
4. 生成されたAPIキーをコピー

---

## 2. 無料枠の確認

### Gemini 1.5 Flash（推奨モデル）

| 項目 | 無料枠 |
|------|--------|
| リクエスト数 | 15 RPM（リクエスト/分） |
| トークン数 | 100万トークン/日 |
| 入力 | $0.075 / 100万トークン |
| 出力 | $0.30 / 100万トークン |

**個人利用なら無料枠で十分です。**

### 月間使用量の目安

```
想定:
- 音声メモ: 30回/月
- テキストメモ: 20回/月
- 週次レビュー: 4回/月

トークン消費:
- 音声文字起こし: 約500トークン/回
- 構造化: 約300トークン/回
- 週次レビュー: 約2,000トークン/回

合計: 約30,000トークン/月
→ 無料枠（100万トークン/日）の1%未満
```

---

## 3. 環境変数の設定

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 4. 動作確認

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# テスト
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('こんにちは')
print(response.text)
```

正常に動作すれば、挨拶への返答が表示されます。

---

## 5. レート制限対策

無料枠のレート制限（15 RPM）を超えないための対策：

```python
import asyncio

async def safe_api_call(func, *args, **kwargs):
    """レート制限を考慮したAPI呼び出し"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            # レート制限に達した場合、待機して再試行
            await asyncio.sleep(5)
            return await func(*args, **kwargs)
        raise e
```

---

## トラブルシューティング

### APIキーが無効

1. キーが正しくコピーされているか確認
2. Google AI Studioでキーの状態を確認
3. 必要に応じて新しいキーを生成

### レート制限エラー

1. リクエスト間隔を空ける（5秒以上）
2. バッチ処理を検討
3. 有料プランへのアップグレードを検討

---

## 次のステップ

- [Obsidianセットアップ](03-obsidian.md)
