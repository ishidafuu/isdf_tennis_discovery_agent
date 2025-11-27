# Phase 4: 高度な分析の機能詳細

## ベクトル検索

### 概要

キーワードではなく、**意味的な類似性**で検索する機能。

**メリット:**
- 「あの時の感覚」を類似のメモから探せる
- 同義語や言い回しの違いを吸収
- より自然な検索体験

### Embedding生成

```python
import google.generativeai as genai

async def get_embedding(text: str) -> list:
    """テキストをEmbedding化"""

    result = genai.embed_content(
        model='models/embedding-001',
        content=text,
        task_type="retrieval_document"
    )

    return result['embedding']

async def save_memo_with_embedding(memo_data: dict):
    """メモを保存する際にEmbeddingも生成"""

    # テキストからEmbedding生成
    text = memo_data.get('raw_text', '')
    embedding = await get_embedding(text)

    # Chromaに保存
    collection.add(
        ids=[memo_data['id']],
        embeddings=[embedding],
        metadatas=[{
            "date": memo_data['date'],
            "scene": memo_data['scene'],
            "user_id": memo_data.get('user_id', 'default')
        }],
        documents=[text]
    )

    # 通常の保存も実行
    await obsidian_manager.save_memo(memo_data)
```

### Chromaのセットアップ

```python
import chromadb
from chromadb.config import Settings

def setup_vector_db(persist_directory: str = "./chroma_db"):
    """Chromaベクトルデータベースをセットアップ"""

    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_directory,
        anonymized_telemetry=False
    ))

    # コレクションを作成または取得
    collection = client.get_or_create_collection(
        name="tennis_memos",
        metadata={"hnsw:space": "cosine"}  # コサイン類似度を使用
    )

    return client, collection
```

### ベクトル検索の実装

```python
async def search_similar_memos_semantic(
    query: str,
    user_id: str = None,
    limit: int = 5
) -> list:
    """意味検索で関連メモを検索"""

    # 質問をEmbedding化
    query_embedding = await get_embedding(query)

    # フィルター条件
    where_filter = {}
    if user_id:
        where_filter["user_id"] = user_id

    # ベクトル検索
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        where=where_filter if where_filter else None
    )

    # 結果を整形
    memos = []
    for i, doc_id in enumerate(results['ids'][0]):
        memos.append({
            "id": doc_id,
            "text": results['documents'][0][i],
            "metadata": results['metadatas'][0][i],
            "distance": results['distances'][0][i] if 'distances' in results else None
        })

    return memos
```

### 既存メモのバッチ変換

```python
async def batch_embed_existing_memos():
    """既存のメモをバッチでEmbedding化"""

    # 全メモを取得
    all_memos = await obsidian_manager.get_all_memos()

    # バッチ処理（API制限を考慮）
    batch_size = 10
    for i in range(0, len(all_memos), batch_size):
        batch = all_memos[i:i+batch_size]

        for memo in batch:
            try:
                # Embedding生成
                embedding = await get_embedding(memo.get('raw_text', memo.get('body', '')))

                # Chromaに保存
                collection.add(
                    ids=[memo['id']],
                    embeddings=[embedding],
                    metadatas=[{
                        "date": memo['date'],
                        "scene": memo.get('scene', '不明')
                    }],
                    documents=[memo.get('raw_text', memo.get('body', ''))]
                )
            except Exception as e:
                print(f"Error embedding memo {memo['id']}: {e}")

        # API制限を考慮して待機
        await asyncio.sleep(1)

    print(f"Embedded {len(all_memos)} memos")
```

---

## パターン分析

### 好調/不調パターンの抽出

```python
async def extract_condition_patterns(memos: list) -> dict:
    """好調時と不調時のパターンを抽出"""

    # メモを好調/不調に分類
    good_memos = [m for m in memos if is_good_condition(m)]
    bad_memos = [m for m in memos if is_bad_condition(m)]

    prompt = f"""
以下の練習メモを分析し、好調時と不調時のパターンを抽出してください。

【好調時のメモ（{len(good_memos)}件）】
{format_memos_for_analysis(good_memos)}

【不調時のメモ（{len(bad_memos)}件）】
{format_memos_for_analysis(bad_memos)}

以下の形式でJSON出力してください:
{{
    "good_patterns": {{
        "common_themes": ["共通するテーマ"],
        "physical_sensations": ["身体感覚"],
        "mental_states": ["メンタル状態"],
        "practice_types": ["練習タイプ"]
    }},
    "bad_patterns": {{
        "common_themes": ["共通するテーマ"],
        "physical_sensations": ["身体感覚"],
        "mental_states": ["メンタル状態"],
        "practice_types": ["練習タイプ"]
    }},
    "key_differences": ["好調と不調の重要な違い"],
    "recommendations": ["改善のための提案"]
}}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return json.loads(response.text)

def is_good_condition(memo: dict) -> bool:
    """好調かどうかを判定"""
    indicators = ['うまくいった', '改善', '成功', '良かった', '上達', 'できた']
    text = memo.get('raw_text', memo.get('body', '')).lower()
    return any(ind in text for ind in indicators)

def is_bad_condition(memo: dict) -> bool:
    """不調かどうかを判定"""
    indicators = ['うまくいかない', '課題', '失敗', '悪い', 'できない', 'ミス']
    text = memo.get('raw_text', memo.get('body', '')).lower()
    return any(ind in text for ind in indicators)
```

### 時系列分析

```python
async def analyze_time_series(memos: list) -> dict:
    """時系列でのトレンドを分析"""

    # 月別に集計
    monthly_data = {}
    for memo in memos:
        month = memo['date'][:7]  # "2025-01"
        if month not in monthly_data:
            monthly_data[month] = {
                "count": 0,
                "improvements": [],
                "issues": []
            }

        monthly_data[month]["count"] += 1

        if memo.get('improvement'):
            monthly_data[month]["improvements"].append(memo['improvement'])
        if memo.get('issue'):
            monthly_data[month]["issues"].append(memo['issue'])

    # トレンドを分析
    prompt = f"""
以下の月別データからトレンドを分析してください。

{json.dumps(monthly_data, ensure_ascii=False, indent=2)}

以下の観点で分析:
1. 練習頻度の変化
2. 改善が見られる技術
3. 継続している課題
4. ターニングポイント
5. 次の成長予測

JSON形式で出力してください。
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return json.loads(response.text)
```

### ターニングポイントの特定

```python
async def find_turning_points(memos: list) -> list:
    """成長のターニングポイントを特定"""

    # 時系列順にソート
    sorted_memos = sorted(memos, key=lambda x: x['date'])

    prompt = f"""
以下の練習メモの時系列から、成長のターニングポイント（転機）を特定してください。

【メモ一覧（時系列順）】
"""

    for memo in sorted_memos:
        prompt += f"""
{memo['date']} ({memo.get('scene', '不明')}):
{memo.get('raw_text', memo.get('body', ''))[:200]}

"""

    prompt += """
ターニングポイントとは:
- 大きな気づきがあった時
- 技術的なブレイクスルー
- メンタル面での転換
- 練習方法の変更

以下の形式でJSON出力:
[
    {{
        "date": "日付",
        "description": "何が変わったか",
        "impact": "その後への影響",
        "importance": "high/medium/low"
    }}
]
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return json.loads(response.text)
```

---

## 予測・提案

### 成長予測

```python
async def predict_growth(memos: list, target_skill: str = None) -> dict:
    """成長を予測"""

    # 最近3ヶ月のメモを分析
    recent_memos = [m for m in memos if is_within_months(m['date'], 3)]

    prompt = f"""
以下の練習メモを分析し、今後の成長を予測してください。

【最近3ヶ月のメモ】
{format_memos_for_analysis(recent_memos)}

{f"【分析対象の技術】: {target_skill}" if target_skill else ""}

以下の観点で予測:
1. 順調に成長している技術
2. 伸び悩んでいる技術
3. 今後1ヶ月での予測
4. 重点的に練習すべきこと

JSON形式で出力:
{{
    "growing_skills": [
        {{"skill": "技術名", "progress": "進捗状況", "prediction": "予測"}}
    ],
    "struggling_skills": [
        {{"skill": "技術名", "barrier": "壁となっていること", "suggestion": "提案"}}
    ],
    "one_month_forecast": "1ヶ月後の予測",
    "recommended_focus": ["重点練習項目"]
}}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return json.loads(response.text)
```

### 練習メニュー提案

```python
async def suggest_practice_menu(
    memos: list,
    available_time: int = 60,
    scene: str = "壁打ち"
) -> str:
    """練習メニューを提案"""

    # 最近の課題を抽出
    recent_issues = []
    for memo in memos[-10:]:  # 直近10件
        if memo.get('next_action'):
            recent_issues.append(memo['next_action'])
        if memo.get('issue'):
            recent_issues.append(memo['issue'])

    prompt = f"""
以下の情報を元に、練習メニューを提案してください。

【練習時間】{available_time}分
【練習場所】{scene}

【最近の課題】
{chr(10).join(f'- {issue}' for issue in recent_issues)}

以下の形式で練習メニューを作成:

## 今日の練習メニュー（{available_time}分）

### ウォームアップ（5分）
- 内容

### メイン練習1（XX分）
- 内容
- ポイント

### メイン練習2（XX分）
- 内容
- ポイント

### クールダウン（5分）
- 内容

### 今日の意識ポイント
- 課題に対するフォーカスポイント
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text
```

### コンディション予測

```python
async def predict_condition(memos: list) -> dict:
    """コンディションを予測"""

    # 直近の練習パターンを分析
    recent_memos = memos[-14:]  # 直近2週間

    # 練習間隔を計算
    practice_intervals = calculate_practice_intervals(recent_memos)

    # 疲労度を推定
    fatigue_indicators = count_fatigue_indicators(recent_memos)

    prompt = f"""
以下の情報から、現在のコンディションを予測してください。

【練習間隔（日）】
{practice_intervals}

【疲労関連のキーワード出現数】
{fatigue_indicators}

【最近のメモの傾向】
{format_recent_trends(recent_memos)}

以下の形式でJSON出力:
{{
    "overall_condition": "good/normal/needs_rest",
    "fatigue_level": 1-5,
    "recommendation": "今日の練習についての提案",
    "warning_signs": ["注意すべきサイン"]
}}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return json.loads(response.text)
```

---

## コストとパフォーマンス

### Embedding生成コスト

```
Gemini Embedding API:
- 入力: $0.00025 / 1000トークン

想定:
- 1メモ平均 200トークン
- 月100メモ → 20,000トークン
- コスト: $0.005/月（約1円）
```

### ベクトル検索のパフォーマンス

```
Chroma（ローカル）:
- 1,000件: 数ms
- 10,000件: 数十ms
- 100,000件: 数百ms

個人利用なら十分高速
```

---

## 次のステップ

Phase 4完了後:
1. ユーザーフィードバックの収集
2. 精度の継続的な改善
3. 新機能のアイデア検討
