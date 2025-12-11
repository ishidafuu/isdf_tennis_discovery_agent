# 実装仕様: Discord返信による追記機能

**作成日**: 2025-12-08
**関連ドキュメント**: `docs/改修/ヒアリング結果_まとめページ機能.md`

---

## 📌 概要

気づきメモ投稿後、**Discordの返信機能を使って追記できる**仕組みを実装する。

### 採用方式
**ハイブリッド方式**: 返信方式（メイン） + ボタン方式（補助）

---

## 🎯 動作フロー

### 全体の流れ

```
1. ユーザーが音声/テキストでメモを入力
   ↓
2. Botがメモを保存（Markdown生成、GitHub push）
   ↓
3. Botがメモ内容をDiscordに投稿
   - メモの要約
   - 「返信で追記できます」の案内
   - 質問例（対比、変化、根拠、具体化）
   - [深堀り質問を見る] ボタン
   ↓
4. ユーザーが返信 or ボタンを押す
   ↓
   【返信の場合】
   ├─ Botが返信を検知
   ├─ AIで内容を整形（質問パターンを判定）
   └─ 元のメモファイルに追記

   【ボタンの場合】
   ├─ 詳しい質問例を表示
   └─ 「返信してください」と案内
   ↓
5. 追記完了（✅リアクション + 確認メッセージ）
```

---

## 📱 Discord表示イメージ

### メモ投稿直後の表示

```
┌─────────────────────────────────────────┐
│ 🎾 壁打ち練習メモを記録しました         │
│                                         │
│ 📅 2025-12-08 14:30                     │
│                                         │
│ ## 気づき                               │
│ - フラットで当てると安定した           │
│                                         │
│ 📊 前回との比較:                       │
│ - 前回はスピンを意識していた           │
│                                         │
│ 🔄 次回のポイント:                     │
│ - フラット打ちを継続                   │
│                                         │
│ [Obsidianで開く]                       │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                         │
│ 💡 このメッセージに返信して追記できます │
│                                         │
│ 質問例:                                 │
│ • フラット以外だとどうなる？（対比）   │
│ • 以前はどうだった？（変化）           │
│ • なぜそう気づいた？（根拠）           │
│ • どこをどう変えた？（具体化）         │
│                                         │
│ [深堀り質問を見る]                     │
└─────────────────────────────────────────┘
```

### ユーザーが返信

```
┌─────────────────────────────────────────┐
│ 🎾 壁打ち練習メモ...                   │
│ ...                                     │
└─────────────────────────────────────────┘
     ↓ 返信
┌─────────────────────────────────────────┐
│ あなた:                                 │
│ スピンだと打点がずれて変な回転がかかる。│
│ スライスは安定するけどスピードが出ない │
└─────────────────────────────────────────┘
     ↓ Botが反応
┌─────────────────────────────────────────┐
│ Bot: 追記しました！ ✅                  │
│                                         │
│ 対比情報を記録しました:                 │
│ - スピン: 打点がずれて変な回転         │
│ - スライス: 安定するがスピード不足     │
└─────────────────────────────────────────┘
```

### ボタンを押した場合

```
（[深堀り質問を見る] ボタンを押す）

┌─────────────────────────────────────────┐
│ 💡 深堀り質問ガイド                     │
│                                         │
│ このメッセージに返信する形で、         │
│ 以下の質問に答えてみてください。       │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                         │
│ 1️⃣ 対比: 他の方法と比べてどう？       │
│ 「フラット」以外に、「スピン」や       │
│ 「スライス」で打つとどうなりますか？   │
│                                         │
│ 例: 「スピンだと打点がずれる」         │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                         │
│ 2️⃣ 変化: 以前はどうだった？           │
│ 今回気づく前は、どんな打ち方を         │
│ していましたか？                       │
│                                         │
│ 例: 「以前はスピンで打っていた」       │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                         │
│ 3️⃣ 根拠: なぜそう気づいた？           │
│ この気づきを得たきっかけは何ですか？   │
│                                         │
│ 例: 「コーチに指摘された」             │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                         │
│ 4️⃣ 具体化: どこをどう変えた？         │
│ 具体的にどの部分を変えましたか？       │
│                                         │
│ 例: 「グリップを薄く持った」           │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│                                         │
│ 💬 元のメッセージに返信して回答して   │
│    ください。複数の質問に答えても     │
│    大丈夫です！                         │
└─────────────────────────────────────────┘
```

---

## 🔧 技術実装

### 1. メモ投稿時にメッセージIDを記録

#### `src/bot/handlers/message_handler.py`（更新）

```python
async def process_voice_message(bot, message):
    """音声メッセージ処理（既存関数の更新）"""

    # ... 既存の処理（文字起こし、構造化抽出、メモ保存）...

    # Markdown生成
    memo_path = markdown_builder.build_memo(...)

    # GitHub push
    bot.github_sync.push_to_github()

    # Discordに投稿
    embed = build_memo_embed(session_data, previous_log)

    # 深堀りガイドを追加
    deepening_guide = build_deepening_guide(session_data)

    # ボタンを追加
    view = DeepeningButtonView()

    sent_message = await message.channel.send(
        embed=embed,
        content=deepening_guide,
        view=view
    )

    # メッセージIDをメモに記録
    update_memo_metadata(memo_path, {
        'discord_message_id': sent_message.id,
        'discord_channel_id': message.channel.id
    })
```

#### 深堀りガイド生成

```python
def build_deepening_guide(session_data: dict) -> str:
    """深堀りガイドテキストを生成"""

    # 気づきの内容から質問例を動的生成
    insight = session_data.get('insights', [''])[0]

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **このメッセージに返信して追記できます**

質問例:
• {insight} 以外だとどうなる？（対比）
• 以前はどうだった？（変化）
• なぜそう気づいた？（根拠）
• どこをどう変えた？（具体化）
"""
```

#### ボタンView

```python
# src/bot/action_buttons.py（更新）

class DeepeningButtonView(discord.ui.View):
    """深堀り質問ボタン"""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="深堀り質問を見る", style=discord.ButtonStyle.primary)
    async def show_deepening_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        """詳しい質問ガイドを表示"""

        guide = """
💡 **深堀り質問ガイド**

このメッセージに返信する形で、以下の質問に答えてみてください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ **対比**: 他の方法と比べてどう？
「フラット」以外に、「スピン」や「スライス」で打つとどうなりますか？

例: 「スピンだと打点がずれる」

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ **変化**: 以前はどうだった？
今回気づく前は、どんな打ち方をしていましたか？

例: 「以前はスピンで打っていた」

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ **根拠**: なぜそう気づいた？
この気づきを得たきっかけは何ですか？

例: 「コーチに指摘された」

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ **具体化**: どこをどう変えた？
具体的にどの部分を変えましたか？

例: 「グリップを薄く持った」

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 元のメッセージに返信して回答してください。
   複数の質問に答えても大丈夫です！
"""

        await interaction.response.send_message(guide, ephemeral=True)
```

---

### 2. 返信を検知して追記

#### `src/bot/client.py`（更新）

```python
@bot.event
async def on_message(message):
    """メッセージ受信イベント"""

    # Botの投稿は無視
    if message.author == bot.user:
        return

    # 返信かどうかをチェック
    if message.reference:
        await handle_reply_to_memo(bot, message)
        return

    # ... 既存の処理（メモ入力など）...
```

#### 返信処理

```python
# src/bot/handlers/reply_handler.py（新規作成）

async def handle_reply_to_memo(bot, message):
    """メモへの返信を検知して追記"""

    # 返信先のメッセージIDを取得
    original_message_id = message.reference.message_id

    # そのメッセージIDに対応するメモファイルを検索
    memo_path = bot.obsidian_manager.find_memo_by_discord_id(original_message_id)

    if not memo_path:
        # 対応するメモが見つからない
        return

    # 返信内容を解析・整形
    deepening_info = await analyze_and_format_reply(bot, message.content)

    if not deepening_info:
        # 深堀り情報でない（例: 「了解」「ありがとう」）
        await message.add_reaction("👍")
        return

    # メモに追記
    bot.obsidian_manager.append_to_memo(memo_path, deepening_info)

    # GitHub push
    bot.github_sync.push_to_github()

    # 確認メッセージ
    await message.add_reaction("✅")
    await message.reply(f"追記しました！\n\n{deepening_info['summary']}")
```

---

### 3. AI解析・整形

#### `src/ai/deepening_analysis.py`（新規作成）

```python
import google.generativeai as genai

async def analyze_and_format_reply(bot, reply_content: str) -> dict:
    """
    返信内容を解析し、深堀り情報として整形

    Returns:
        {
            'is_deepening': bool,  # 深堀り情報かどうか
            'pattern': str,  # 質問パターン（contrast/change/reason/detail）
            'formatted': str,  # 整形されたMarkdown
            'summary': str  # ユーザーへの確認メッセージ
        }
    """

    prompt = f"""
以下のテキストを分析してください。

テキスト:
{reply_content}

タスク:
1. これは「深堀り情報」ですか？
   - 深堀り情報: テニスの技術的な気づきに関する詳細情報
   - 深堀り情報でない: 「了解」「ありがとう」などの挨拶

2. 深堀り情報の場合、以下のどのパターンに該当しますか？
   - contrast: 他の方法との対比
   - change: 以前との変化
   - reason: 気づいた理由・根拠
   - detail: 具体的な変更点

3. Markdown形式で整形してください。

出力形式（JSON）:
{{
  "is_deepening": true/false,
  "pattern": "contrast" | "change" | "reason" | "detail" | null,
  "formatted": "整形されたMarkdown",
  "summary": "ユーザーへの確認メッセージ"
}}
"""

    response = await bot.gemini_client.generate_content(prompt)
    result = json.loads(response.text)

    return result if result['is_deepening'] else None


def format_deepening_markdown(pattern: str, content: str) -> str:
    """
    パターンに応じてMarkdownを整形

    Args:
        pattern: 質問パターン（contrast/change/reason/detail）
        content: 返信内容

    Returns:
        整形されたMarkdown
    """

    pattern_labels = {
        'contrast': '対比',
        'change': '変化',
        'reason': '根拠',
        'detail': '具体化'
    }

    label = pattern_labels.get(pattern, '補足')

    return f"""

### 深堀り情報

**{label}**:
{content}
"""
```

#### プロンプト例

```
入力:
「スピンだと打点がずれて変な回転がかかる。スライスは安定するけどスピードが出ない」

出力:
{
  "is_deepening": true,
  "pattern": "contrast",
  "formatted": "

### 深堀り情報

**対比**: フラット以外だとどうなる？
- スピン: 打点がずれて変な回転がかかる
- スライス: 安定するがスピード不足
",
  "summary": "対比情報を記録しました:\n- スピン: 打点がずれて変な回転\n- スライス: 安定するがスピード不足"
}
```

---

### 4. メモファイルのメタデータ管理

#### YAML frontmatter（拡張）

```yaml
---
date: 2025-12-08
scene: 壁打ち
tags: [フォアハンド, 強打]
discord_message_id: 1234567890123456789
discord_channel_id: 9876543210987654321
---
```

#### メモ検索機能

```python
# src/storage/obsidian_manager.py（更新）

def find_memo_by_discord_id(self, message_id: int) -> Optional[str]:
    """
    Discord MessageIDからメモファイルを検索

    Args:
        message_id: DiscordメッセージID

    Returns:
        メモファイルのパス（見つからない場合はNone）
    """

    # 全メモファイルを検索
    for memo_path in self.vault_path.glob("*.md"):
        metadata = self._parse_frontmatter(memo_path)

        if metadata.get('discord_message_id') == message_id:
            return str(memo_path)

    return None
```

---

## 📊 データフロー図

```
┌─────────────────┐
│ ユーザー        │
│ 音声/テキスト  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Discord Bot     │
│ メモ保存        │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Markdown生成    │
│ GitHub push     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Discord投稿     │
│ + 深堀りガイド  │
│ + MessageID記録 │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ ユーザーが返信  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ on_message      │
│ 返信検知        │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ MessageIDから   │
│ メモファイル検索│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Gemini API      │
│ 内容解析・整形  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ メモに追記      │
│ GitHub push     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ ✅確認メッセージ│
└─────────────────┘
```

---

## 🧪 テストシナリオ

### 1. 正常系: 返信で追記

```
【入力】
音声メモ: 「フラットで当てると安定した」

【期待される動作】
1. メモが保存される
2. Discordに投稿（深堀りガイド付き）
3. MessageIDがメモに記録される

【入力】
返信: 「スピンだと打点がずれる」

【期待される動作】
1. 返信を検知
2. AIで解析（pattern: contrast）
3. 整形されてメモに追記
4. ✅リアクション + 確認メッセージ
```

### 2. 正常系: ボタンで質問表示

```
【入力】
ボタン押下: 「深堀り質問を見る」

【期待される動作】
1. 詳しい質問ガイドを表示（ephemeral）
2. 元のメッセージに返信するよう案内
```

### 3. 正常系: 複数回の返信

```
【入力】
1回目の返信: 「スピンだと打点がずれる」
2回目の返信: 「以前はスピンで打っていた」

【期待される動作】
1. 1回目の返信が追記される（pattern: contrast）
2. 2回目の返信も追記される（pattern: change）
3. 同じメモに両方の情報が記録される
```

### 4. 異常系: 深堀り情報でない返信

```
【入力】
返信: 「了解」

【期待される動作】
1. AIが「深堀り情報でない」と判定
2. 追記されない
3. 👍リアクションのみ
```

### 5. 異常系: 対応するメモが見つからない

```
【入力】
過去の無関係なメッセージに返信

【期待される動作】
1. MessageIDから検索 → 見つからない
2. 何もしない（通常のメッセージとして処理）
```

---

## 🚀 実装順序

### Phase 1: 基本機能
1. ✅ メモ投稿時にMessageIDを記録
2. ✅ 返信検知機能（`on_message`）
3. ✅ MessageIDからメモ検索
4. ✅ 返信内容をそのまま追記（整形なし）

### Phase 2: AI整形
1. ✅ Gemini APIで返信内容を解析
2. ✅ 質問パターンを判定（contrast/change/reason/detail）
3. ✅ Markdown形式で整形
4. ✅ 深堀り情報でない返信を除外

### Phase 3: UI強化
1. ✅ 深堀りガイドをメモ投稿に追加
2. ✅ 「深堀り質問を見る」ボタン
3. ✅ 確認メッセージ（追記内容のサマリー）

### Phase 4: テスト
1. ✅ 正常系テスト
2. ✅ 異常系テスト
3. ✅ 実環境での動作確認

---

## 📝 備考

### 既存機能との互換性
- Phase 2の `action_buttons.py` を拡張
- `obsidian_manager.py` に検索機能を追加
- 既存のメモ保存フローは変更なし

### パフォーマンス
- Gemini API呼び出し: 1回/返信
- コスト: 約0.001円/返信（text-embedding-004の場合）

### セキュリティ
- MessageIDは公開情報（問題なし）
- 返信内容は既存のメモと同様に扱う（.envで管理）

---

**最終更新**: 2025-12-08
**次回レビュー**: Phase 1実装後
