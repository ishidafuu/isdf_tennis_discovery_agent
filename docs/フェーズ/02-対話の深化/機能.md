# Phase 2: 対話深化の機能詳細

## AIの自動判断

### 判断基準

AIが以下を自動判断：

1. **そのまま保存でOK**: 日常的なメモ、特に深掘り不要
2. **深堀質問すべき**: 新しい気づき、曖昧な表現
3. **過去と比較すべき**: 過去に似たテーマがある

### 実装コード

```python
async def ai_auto_decision(text: str, scene_type: str, previous_memo: dict) -> dict:
    """AIが自動的に次のアクションを判断"""

    prompt = f"""
以下の音声メモを分析し、次のアクションを判断してください。

音声メモ:
{text}

シーン: {scene_type}

前回のメモ: {previous_memo.get('raw_text') if previous_memo else 'なし'}

判断基準:
1. **そのまま保存**: 日常的な記録、特に深掘り不要
2. **深堀質問**: 新しい気づき、曖昧な表現、深掘りする価値あり
3. **過去と比較**: 過去に似たテーマがあり、比較すると有益

判定結果をJSON形式で出力してください:
{{
  "action": "save_only / deep_dive / compare",
  "reason": "判断理由",
  "confidence": 0.0-1.0
}}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    decision = json.loads(response.text)

    # 自信度が低い場合はデフォルト（保存のみ）
    if decision['confidence'] < 0.7:
        decision['action'] = 'save_only'

    return decision
```

### 自動実行フロー

```python
async def process_with_ai_decision(text: str, scene_type: str):
    """AIの判断に基づいて自動処理"""

    # 前回メモを読み込み
    previous_memo = await load_previous_memo(scene_type)

    # AIが判断
    decision = await ai_auto_decision(text, scene_type, previous_memo)

    if decision['action'] == 'save_only':
        # そのまま保存
        await save_memo(text, scene_type)
        await send_message("保存しました！")

    elif decision['action'] == 'deep_dive':
        # 深堀質問
        question = await generate_follow_up_question(text, scene_type)
        await send_message(f"{question}\n\n回答を音声で送信してください（スキップ可能）")

    elif decision['action'] == 'compare':
        # 過去と比較
        comparison = await compare_with_past(text)
        await send_message(f"過去のメモと比較：\n\n{comparison}")
        await save_memo_with_comparison(text, comparison, scene_type)
```

---

## 深堀質問の生成

### ソクラテス式問答

**目的:**
- ユーザーに気づきを促す
- 曖昧な表現を具体化させる
- 思考を深める

### 質問のパターン

| パターン | 質問例 |
|---------|--------|
| **理由を聞く** | 「なぜそう思ったんですか？」 |
| **具体化を促す** | 「『うまくいった』とは、具体的にどういう感覚ですか？」 |
| **他の可能性** | 「他に試せることはありますか？」 |
| **次のアクション** | 「次回も同じように意識しますか？」 |
| **過去との違い** | 「前回と何が違いましたか？」 |

### 実装コード

```python
async def generate_follow_up_question(text: str, scene_type: str) -> str:
    """追加質問を生成"""

    prompt = f"""
以下の音声メモに対して、ソクラテス式の質問を1つ生成してください。

音声メモ:
{text}

シーン: {scene_type}

質問の目的:
- ユーザーの気づきを深める
- 曖昧な表現を具体化させる
- 次のアクションを明確にする

質問の例:
- 「なぜそう思ったんですか？」
- 「具体的にどういう感覚でしたか？」
- 「他に試せることはありますか？」

生成した質問のみを出力してください（前置きや説明不要）。
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text.strip()
```

### 複数回の質問

```python
async def deep_dive_conversation(initial_text: str, scene_type: str, max_turns: int = 3):
    """複数回の質問で深掘り"""

    conversation_history = [initial_text]
    turn = 0

    while turn < max_turns:
        # 質問を生成
        question = await generate_follow_up_question(
            text="\n".join(conversation_history),
            scene_type=scene_type
        )

        # 質問を送信
        await send_message(f"{question}")

        # ユーザーの回答を待つ（タイムアウト: 60秒）
        answer = await wait_for_voice_message(timeout=60)

        if not answer:
            # タイムアウト or スキップ
            break

        # 回答を履歴に追加
        conversation_history.append(f"Q: {question}")
        conversation_history.append(f"A: {answer}")

        # 十分深掘りできたか判定
        if await is_deep_enough(conversation_history):
            break

        turn += 1

    # すべての会話を含めて保存
    full_text = "\n\n".join(conversation_history)
    await save_memo(full_text, scene_type)
```

---

## オプションボタンUI

### Discordボタンの実装

```python
import discord
from discord.ui import Button, View

class ActionButtonsView(View):
    """保存後のアクションボタン"""

    def __init__(self, memo_data: dict, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.memo_data = memo_data
        self.result = None

    @discord.ui.button(label="深堀り質問", style=discord.ButtonStyle.primary, emoji="🤔")
    async def deep_dive_button(self, interaction: discord.Interaction, button: Button):
        self.result = "deep_dive"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="過去と比較", style=discord.ButtonStyle.secondary, emoji="📊")
    async def compare_button(self, interaction: discord.Interaction, button: Button):
        self.result = "compare"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="そのまま終了", style=discord.ButtonStyle.success, emoji="✅")
    async def finish_button(self, interaction: discord.Interaction, button: Button):
        self.result = "finish"
        await interaction.response.defer()
        self.stop()

    async def on_timeout(self):
        """タイムアウト時の処理"""
        self.result = "timeout"
        for item in self.children:
            item.disabled = True
```

### 使用例

```python
async def send_with_action_buttons(channel, memo_data: dict):
    """アクションボタン付きでメッセージを送信"""

    view = ActionButtonsView(memo_data)

    message = await channel.send(
        f"メモを保存しました！\n\n追加のアクションを選択してください：",
        view=view
    )

    # ボタン押下を待つ
    await view.wait()

    # ボタンを無効化
    for item in view.children:
        item.disabled = True
    await message.edit(view=view)

    # 結果に応じた処理
    if view.result == "deep_dive":
        question = await generate_follow_up_question(memo_data['raw_text'], memo_data['scene'])
        await channel.send(f"💭 {question}")

    elif view.result == "compare":
        comparison = await compare_with_past(memo_data['raw_text'])
        await channel.send(f"📊 過去との比較：\n\n{comparison}")

    elif view.result == "finish" or view.result == "timeout":
        pass  # 何もしない
```

---

## 過去と比較

### 類似メモの検索

```python
async def search_similar_memos(text: str, scene_type: str = None, limit: int = 5) -> list:
    """類似するメモを検索"""

    # キーワード抽出
    keywords = await extract_keywords(text)

    # メモを検索
    similar_memos = await obsidian_manager.search_by_keywords(
        keywords=keywords,
        scene=scene_type,
        limit=limit,
        exclude_recent_days=3  # 直近3日は除外
    )

    return similar_memos
```

### 比較分析

```python
async def compare_with_past(text: str) -> str:
    """過去のメモと比較分析"""

    # 類似メモを検索
    similar_memos = await search_similar_memos(text, limit=3)

    if len(similar_memos) == 0:
        return "過去に類似するメモが見つかりませんでした。"

    # Geminiで比較分析
    prompt = f"""
今回のメモと過去のメモを比較分析してください。

【今回のメモ】
{text}

【過去のメモ】
"""

    for i, memo in enumerate(similar_memos, 1):
        prompt += f"""
{i}. {memo['date']} ({memo['scene']})
{memo.get('raw_text', memo.get('body', ''))}

"""

    prompt += """
以下の観点で分析してください:
1. 共通点: 何が一貫しているか
2. 変化: 何が改善/変化したか
3. パターン: 繰り返し出てくるテーマ
4. 提案: 次に意識すべきこと

分析結果:
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text
```

---

## 矛盾の指摘

### 目的

- 考えの変化に気づかせる
- 一貫性を確認させる
- 意図的な変化か、無意識か確認

### 実装コード

```python
async def detect_contradiction(current_text: str, previous_memos: list) -> str | None:
    """矛盾・変化を検出"""

    if len(previous_memos) == 0:
        return None

    prompt = f"""
今回のメモと過去のメモを比較し、矛盾や考えの変化があれば指摘してください。

【今回のメモ】
{current_text}

【過去のメモ】
"""

    for memo in previous_memos[-5:]:  # 直近5件
        prompt += f"""
- {memo['date']}: {memo.get('raw_text', memo.get('body', ''))}
"""

    prompt += """
判定結果をJSON形式で出力してください:
{{
  "has_contradiction": true/false,
  "previous_statement": "過去の発言",
  "current_statement": "今回の発言",
  "comment": "指摘のコメント"
}}
"""

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    result = json.loads(response.text)

    if result['has_contradiction']:
        message = f"""
**考えの変化に気づきました:**

**過去:**
{result['previous_statement']}

**今回:**
{result['current_statement']}

{result['comment']}

考えが変わったのですか？それとも状況が違いますか？
"""
        return message

    return None
```

---

## #質問チャンネルの実装

### 設計思想

- コマンドではなく、チャンネルで分ける
- 音声ファーストに一貫性を持たせる
- 他のチャンネル（#壁打ち、#スクール等）と同じUX

### 使用例

```
#質問 チャンネルで音声送信
「最近サーブの調子が悪いんだけど、どうすればいい？」

または

#質問 チャンネルでテキスト送信
「バックハンドのコツって何だっけ？」
```

### 実装コード

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

    if not question:
        await searching_msg.edit(content="質問を認識できませんでした。")
        return

    # 関連メモを検索
    related_memos = await search_related_memos(question, message.author.id)

    if len(related_memos) == 0:
        await searching_msg.edit(content="関連するメモが見つかりませんでした。\nもっと練習を記録してみてください。")
        return

    # AIで回答生成
    answer = await answer_with_knowledge(question, related_memos)

    # 参照したメモのリスト
    memo_list = "\n".join([
        f"- {m['date']} ({m['scene']})" for m in related_memos
    ])

    # 回答を送信
    response = f"""
{answer}

**参照したメモ:**
{memo_list}
"""

    await searching_msg.edit(content=response)
```

### チャンネルルーティング

```python
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    channel_name = message.channel.name

    # リアルタイム記録チャンネル
    if channel_name in ["壁打ち", "スクール", "試合", "フリー練習"]:
        await handle_practice_memo(message, channel_name)

    # 振り返りチャンネル
    elif channel_name == "振り返り":
        await handle_retrospective(message)

    # 質問チャンネル（Phase 2）
    elif channel_name == "質問":
        await handle_question(message)

    await bot.process_commands(message)
```

---

## 次のドキュメント

- [../03-data-utilization/index.md](../03-data-utilization/index.md) - Phase 3: データ活用
