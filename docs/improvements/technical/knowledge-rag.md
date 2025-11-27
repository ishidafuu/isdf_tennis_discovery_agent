# ナレッジ統合（RAG）

## 概要

Obsidianに蓄積されたメモをAIのナレッジとして活用し、過去の経験に基づいた回答を生成する機能です。

**目的:**
- 過去のメモを参照しながら質問に答える
- パターン分析で成長を可視化
- 好調時の感覚を思い出させる

---

## 実装方法

### 方法1: キーワード検索 + RAG（Phase 2-3 推奨）

シンプルで実装が容易、コスト効率が良い方法です。

```python
async def search_related_memos(question: str, limit: int = 5):
    """質問から関連メモを検索"""

    # キーワード抽出
    keywords = await extract_keywords(question)

    # Obsidianから検索
    results = []
    for keyword in keywords:
        keyword_results = await obsidian.search_by_keyword(keyword, limit=limit)
        results.extend(keyword_results)

    # 重複を削除して返す
    unique_results = {r['path']: r for r in results}.values()
    return list(unique_results)[:limit]

async def extract_keywords(text: str) -> list:
    """テキストからキーワードを抽出"""

    prompt = f"""
以下のテキストから、重要なキーワードを抽出してください。
テニス用語、技術名、感覚表現を優先してください。

テキスト:
{text}

キーワード（JSON配列形式）:
["キーワード1", "キーワード2", ...]
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    import json
    keywords = json.loads(response.text)

    return keywords
```

### 方法2: 大規模コンテキスト活用（Phase 3）

全メモを一度に送信し、文脈の一貫性を高める方法です。

```python
async def load_all_memos_as_context(months: int = 3):
    """全メモをコンテキストとしてロード"""

    from datetime import datetime, timedelta

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)

    memos = await obsidian.search_by_date_and_scene(
        start_date=start_date.strftime('%Y-%m-%d'),
        limit=100
    )

    # Markdown形式で結合
    context = f"# 過去の練習記録（{months}ヶ月分）\n\n"

    for memo in memos:
        context += f"""
## {memo['date']} - {memo['scene']}

{memo['raw_text']}

**改善した点:** {memo.get('improvement', 'なし')}
**課題:** {memo.get('issue', 'なし')}

---

"""

    return context
```

### 方法3: ベクトル検索 + RAG（Phase 4）

意味的な類似性で検索する、最も精度の高い方法です。

```python
async def get_embedding(text: str) -> list:
    """テキストをEmbedding化"""

    model = 'models/embedding-001'

    embedding = genai.embed_content(
        model=model,
        content=text,
        task_type="retrieval_document"
    )

    return embedding['embedding']

async def search_related_memos_semantic(question: str, limit: int = 5):
    """意味検索で関連メモを検索"""

    # 質問をEmbedding化
    question_embedding = await get_embedding(question)

    # ベクトル検索（Chroma等）
    results = await vector_db.query(
        vector=question_embedding,
        top_k=limit
    )

    return results
```

---

## Discordチャンネル実装

### #質問 チャンネル

```python
async def handle_question(message: discord.Message):
    """#質問 チャンネルでの質問に回答"""

    # 検索中メッセージ
    searching_msg = await message.channel.send("🔍 過去のメモを検索中...")

    # 音声またはテキストを取得
    if message.attachments:
        audio_url = message.attachments[0].url
        question = await transcribe_audio(audio_url)
    else:
        question = message.content

    # 関連メモを検索
    related_memos = await search_related_memos(question)

    if len(related_memos) == 0:
        await searching_msg.edit(content="関連するメモが見つかりませんでした。")
        return

    # AIで回答生成
    answer = await answer_with_knowledge(question, related_memos)

    await searching_msg.edit(content=answer)
```

### #分析 チャンネル

```python
async def handle_analysis(message: discord.Message):
    """#分析 チャンネルでの分析リクエストに対応"""

    analyzing_msg = await message.channel.send("📊 分析中...")

    # 期間を判定
    period = detect_period_from_text(message.content)

    # メモを取得して分析
    memos = await obsidian.search_by_date_and_scene(
        start_date=period['start_date'],
        limit=100
    )

    analysis = await analyze_memos(memos, period['label'])

    await analyzing_msg.edit(content=analysis)
```

---

## コスト試算

### キーワード検索 + RAG

```
想定:
- 過去のメモ5件を毎回送信（約1,000トークン）
- 回答生成（約300トークン）
- 月100回質問

合計: 約 $0.02/月
```

### 大規模コンテキスト

```
想定:
- 過去のメモ100件を毎回送信（約20,000トークン）
- 回答生成（約300トークン）
- 月100回質問

合計: 約 $0.16/月
```

**結論:** どちらの方法でも月額数十円程度で実現可能

---

## ベクトルDBの選択肢

| DB | 特徴 | コスト |
|----|------|--------|
| **Chroma** | ローカル、軽量（推奨） | 無料 |
| **Qdrant** | 高速、スケーラブル | 無料（自己ホスト） |
| **Pinecone** | マネージド、簡単 | 有料 |
| **Weaviate** | オープンソース | 無料（自己ホスト） |

---

## 実装ロードマップ

### Phase 2: 基本的な質問応答

- キーワード抽出機能
- 関連メモ検索機能
- #質問 チャンネル実装

### Phase 3: 分析・可視化

- #分析 チャンネル実装
- 成長分析機能
- パターン検出機能

### Phase 4: ベクトル検索

- Embedding生成機能
- ベクトルDB統合
- 意味検索機能

---

## 次のステップ

- [セキュリティ考慮事項](security.md)
