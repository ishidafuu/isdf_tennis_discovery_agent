# 📋 Phase 2 実装計画：継続性の担保

**目標**: 前回の練習から今回へ、今回から次回へ「線」でつなぐ

---

## 🎯 Phase 2の目的

Phase 1では「1回の練習を記録する」ことができました。
Phase 2では「練習の継続性」を実現します。

### コンセプト
- **Cycle Oriented**: 前回の課題を今回のテーマにし、今回の発見を次回へつなげる
- **Manager Role**: 練習開始時に前回の内容をリマインド
- **Reflection**: 練習終了時に振り返りを促す

---

## 📝 実装する機能

### 1. `/start` コマンド

**目的**: 練習開始時に前回の課題を思い出させる

**動作フロー**:
```
ユーザー: /start
    ↓
Bot: GitHubから最新のセッションを取得
    ↓
Bot: 前回のNext Actionを読み出す
    ↓
Bot: 「前回は〇〇を意識することが課題でした。今日はこれを試しますか？」とメッセージ
    ↓
Bot: スレッドを作成（このセッション専用）
```

**実装箇所**:
- `src/bot/commands.py` - 新規作成
- `src/storage/github_sync.py` - `get_latest_session_content()` メソッド追加

**データ構造**:
```python
class SessionReminder:
    last_session_date: datetime
    last_next_actions: list[NextAction]
    last_somatic_marker: Optional[str]
    last_condition: str
```

---

### 2. `/finish` コマンド

**目的**: 練習終了時に振り返りを促し、セッションをクローズ

**動作フロー**:
```
ユーザー: /finish
    ↓
Bot: このスレッド内の全メッセージを集約
    ↓
Bot: 「今日の気づきは？」などソクラテス式の質問
    ↓
ユーザー: 回答（音声/テキスト）
    ↓
Bot: 最終的なMarkdownを生成＆GitHub Push
    ↓
Bot: 「お疲れ様でした！次回は〇〇を意識しましょう」
```

**実装箇所**:
- `src/bot/commands.py` - `/finish` コマンド追加
- `src/ai/gemini_client.py` - `generate_reflection_questions()` メソッド追加
- `src/models/session.py` - セッション状態管理の追加

---

### 3. セッション管理機能

**目的**: 1つの練習を1つのスレッドで管理

**機能**:
- `/start` でスレッドを自動作成
- スレッド内の全メッセージを1つのセッションとして扱う
- `/finish` でセッションをクローズ

**実装箇所**:
- `src/models/session.py` - `SessionState` クラス追加
- `src/storage/session_manager.py` - 新規作成（メモリ内状態管理）

**データ構造**:
```python
class SessionState:
    thread_id: str
    user_id: str
    started_at: datetime
    messages: list[str]
    is_active: bool
```

---

### 4. 前回ログの読み込み

**目的**: GitHubから過去のセッションを取得

**機能**:
- 最新のMarkdownファイルを読み込み
- フロントマターをパース
- Next Actionを抽出

**実装箇所**:
- `src/storage/github_sync.py` - `get_latest_session_content()` 追加
- `src/storage/markdown_parser.py` - 新規作成（Markdownパース）

---

## 🗂️ 新規作成ファイル

```
src/
├── bot/
│   └── commands.py                 # /start, /finish コマンド
├── storage/
│   ├── markdown_parser.py          # Markdownパース
│   └── session_manager.py          # セッション状態管理
└── models/
    └── session_state.py            # SessionState, SessionReminder
```

---

## 📐 実装の優先順位

### Step 1: 基本的な `/start` コマンド（高優先度）
- [ ] コマンドの登録
- [ ] GitHubから最新セッション取得
- [ ] 前回のNext Actionを表示
- [ ] スレッド作成

### Step 2: `/finish` コマンド（高優先度）
- [ ] コマンドの登録
- [ ] 振り返り質問の生成
- [ ] セッションのクローズ

### Step 3: セッション管理（中優先度）
- [ ] スレッドベースのセッション管理
- [ ] 複数ユーザー対応

### Step 4: 高度な機能（低優先度）
- [ ] セッション履歴の表示
- [ ] 統計情報の表示

---

## 🎨 ユーザー体験の設計

### 理想的なフロー

**練習前（コートに到着）**:
```
ユーザー: /start
Bot: 📊 前回（11/26）の練習では...
     🎯 次回のテーマ：トスアップ時の呼吸を意識する
     💡 意識すること：上げる瞬間に息を吐く

     今日はこれを試しますか？
     このスレッドで練習中の気づきを送ってください！

[新しいスレッドが作成される]
```

**練習中**:
```
ユーザー: 🎤 [音声メッセージ]
         「呼吸を意識したら、トスが安定してきた...」

Bot: ✅ 記録しました
     💭 その時、身体のどこに一番意識が向いていましたか？

ユーザー: 🎤 [音声メッセージ]
         「肩の力が抜けた感覚があった」
```

**練習後（帰宅前）**:
```
ユーザー: /finish

Bot: 🎾 今日の練習お疲れ様でした！
     📝 今日の発見を振り返ってみましょう

     💭 今日、一番印象に残った「身体の感覚」は何でしたか？

ユーザー: 🎤 [音声メッセージ]
         「肩の力を抜くと、自然に回旋が生まれた」

Bot: ✅ 練習記録を保存しました
     📁 [GitHub リンク]

     🟦 次回のテーマ：
     • 肩の脱力を維持しながらパワーを出す

     次回も頑張りましょう！
```

---

## 🔧 技術的な実装詳細

### 1. Discord スレッド管理

```python
# /start コマンド
@bot.command()
async def start(ctx):
    # 前回のセッションを取得
    last_session = await github_sync.get_latest_session()

    # スレッドを作成
    thread = await ctx.message.create_thread(
        name=f"練習セッション {datetime.now().strftime('%Y/%m/%d')}",
        auto_archive_duration=1440  # 24時間
    )

    # リマインダーを送信
    await thread.send(embed=create_reminder_embed(last_session))

    # セッション状態を記録
    session_manager.start_session(thread.id, ctx.author.id)
```

### 2. Markdownパース

```python
class MarkdownParser:
    def parse_frontmatter(self, content: str) -> dict:
        """YAMLフロントマターをパース"""

    def extract_next_actions(self, content: str) -> list[NextAction]:
        """Next Actionセクションを抽出"""
```

### 3. セッション状態管理

```python
class SessionManager:
    def __init__(self):
        self.active_sessions: dict[str, SessionState] = {}

    def start_session(self, thread_id: str, user_id: str):
        """セッション開始"""

    def end_session(self, thread_id: str) -> SessionState:
        """セッション終了"""

    def is_active(self, thread_id: str) -> bool:
        """セッションがアクティブか確認"""
```

---

## 🧪 テスト計画

### 単体テスト
- [ ] MarkdownParser のテスト
- [ ] SessionManager のテスト
- [ ] コマンドのテスト

### 統合テスト
- [ ] /start → 音声送信 → /finish の一連のフロー
- [ ] 複数ユーザーの同時利用

---

## 📊 成功の定義

Phase 2が成功したと言えるのは：
- ✅ `/start` で前回の課題を表示できる
- ✅ スレッド内で複数の音声メッセージを送信できる
- ✅ `/finish` でセッションをクローズできる
- ✅ 前回→今回→次回の「線」がつながる

---

## ⚠️ 注意点

1. **スレッド管理の複雑さ**
   - 複数ユーザーが同時に使う場合の競合
   - セッション状態の永続化（メモリ vs DB）

2. **Markdownパースの堅牢性**
   - フォーマットが変わった場合の対応
   - 不正なMarkdownの処理

3. **UXの向上**
   - コマンドを忘れた時の対応
   - ヘルプメッセージの充実

---

## 🚀 実装開始の準備

Phase 2を始める前に確認：
- ✅ Phase 1が完全に動作している
- ✅ GitHubに練習記録が複数保存されている
- ✅ 環境変数が正しく設定されている

準備ができたら、Step 1 から実装を開始します！
