# リファクタリング分析レポート

**日付**: 2025-11-29
**対象**: Tennis Discovery Agent コードベース

## エグゼクティブサマリー

コードベースを分析した結果、以下の主要な問題領域を特定しました：

1. **コードの重複** - DRY原則違反が多数
2. **長いメソッド** - 100行を超える関数が複数
3. **責任の分散** - 単一責任原則(SRP)違反
4. **型安全性の欠如** - `Dict[str, Any]`の多用
5. **テストしにくい設計** - 依存性注入(DI)の不足
6. **マジックナンバー/文字列** - 定数の重複定義

---

## 🔴 高優先度（Critical）

### 1. メッセージハンドラーの重複コード

**問題箇所**: `src/bot/handlers/message_handler.py`

**問題内容**:
- `process_voice_message` (120行)
- `process_text_message` (120行)
- `process_image_message` (120行)
- `process_video_message` (120行)
- `process_reflection_message` (135行)

これら5つの関数が以下の処理を繰り返している：
```python
# 1. シーン検出
scene_type, scene_name = detect_scene_from_channel(channel_name)
scene_emoji = get_scene_emoji(scene_type)

# 2. Thinking messageの送信
thinking_msg = await message.reply(f"{scene_emoji} 処理中...")

# 3. 処理の実行（ここだけ異なる）
# ...

# 4. GitHub push
file_url = bot.github_sync.push_session(...)

# 5. Embed作成と送信
embed = discord.Embed(...)
# 同じフィールド追加ロジック
await thinking_msg.edit(content=None, embed=embed)

# 6. エラーハンドリング（完全に同一）
except Exception as e:
    error_msg = f"❌ エラーが発生しました: {str(e)}"
    print(f"Error processing ...: {e}")
    if bot.debug:
        import traceback
        traceback.print_exc()
    await message.reply(error_msg)
```

**リファクタリング提案**:

```python
# 基本クラスまたは共通関数を作成
class MessageProcessor:
    """メッセージ処理の基底クラス"""

    async def process(
        self,
        bot: TennisDiscoveryBot,
        message: discord.Message,
        attachment: Optional[discord.Attachment] = None
    ):
        try:
            # 共通処理
            scene_info = self._detect_scene(message.channel.name)
            thinking_msg = await self._send_thinking_message(message, scene_info)

            # サブクラスで実装
            session, file_url = await self._process_content(
                bot, message, attachment, scene_info, thinking_msg
            )

            # 共通処理
            await self._send_result_embed(
                thinking_msg, session, file_url, scene_info
            )

        except Exception as e:
            await self._handle_error(message, e, bot.debug)

    async def _process_content(self, ...):
        """サブクラスで実装する抽象メソッド"""
        raise NotImplementedError

class VoiceMessageProcessor(MessageProcessor):
    async def _process_content(self, ...):
        # 音声処理のみ実装
        ...

class ImageMessageProcessor(MessageProcessor):
    async def _process_content(self, ...):
        # 画像処理のみ実装
        ...
```

**影響度**: 高
**推定工数**: 4-6時間
**削減コード量**: 約300-400行

---

### 2. メディアヘルパーの重複

**問題箇所**: `src/bot/helpers/markdown_helpers.py`

**問題内容**:
```python
# build_image_markdown と build_video_markdown がほぼ同一
# push_image_memo_to_github と push_video_memo_to_github がほぼ同一
```

**リファクタリング提案**:

```python
def build_media_markdown(
    memo_data: dict,
    scene_name: str,
    media_type: Literal["image", "video"]
) -> str:
    """統合メディアMarkdown生成"""
    emoji = "📸" if media_type == "image" else "🎥"
    frontmatter_data = {
        "date": memo_data['date'],
        "scene": scene_name,
        "input_type": media_type,
        "tags": memo_data.get('tags', ['tennis', media_type]),
    }
    # ...共通ロジック

def push_media_memo_to_github(
    github_sync,
    session,
    markdown_content: str,
    scene_name: str,
    media_type: Literal["image", "video"]
) -> str:
    """統合メディアGitHub push"""
    builder = MarkdownBuilder()
    suffix = "画像" if media_type == "image" else "動画"
    filename = builder.get_filename_for_session(session, f"{scene_name}-{suffix}")
    # ...共通ロジック
```

**影響度**: 中
**推定工数**: 1-2時間
**削減コード量**: 約80行

---

### 3. Discord Embed作成ロジックの集約

**問題箇所**: `src/bot/handlers/message_handler.py` (各関数内)

**問題内容**:
各メッセージハンドラーで同じようなEmbed作成ロジックが重複

**リファクタリング提案**:

```python
# src/bot/helpers/embed_builder.py (新規作成)

class SessionEmbedBuilder:
    """練習セッションのDiscord Embed生成"""

    @staticmethod
    def build(
        session: PracticeSession,
        scene_info: SceneInfo,
        file_url: str,
        previous_log: Optional[str] = None,
        extra_fields: Optional[list[dict]] = None
    ) -> discord.Embed:
        """統一されたEmbed生成"""
        embed = discord.Embed(
            title=f"{scene_info.emoji} {scene_info.name}の記録を保存しました",
            description=session.summary or "記録しました",
            color=scene_info.color
        )

        if previous_log:
            embed.add_field(name="🔄 サイクル", value=previous_log, inline=False)

        if session.somatic_marker:
            embed.add_field(name="🎯 身体感覚", value=session.somatic_marker, inline=False)

        # ...共通フィールド

        if extra_fields:
            for field in extra_fields:
                embed.add_field(**field)

        embed.add_field(name="📁 GitHub", value=f"[ファイルを見る]({file_url})", inline=False)
        embed.set_footer(text=f"📅 {session.date.strftime('%Y年%m月%d日')}")

        return embed
```

**影響度**: 高
**推定工数**: 2-3時間
**削減コード量**: 約150-200行

---

## 🟡 中優先度（High）

### 4. 型安全性の向上

**問題箇所**: 複数ファイル

**問題内容**:
- `Dict[str, Any]`が多用されている
- scene_dataなどの構造化データに型がない

**リファクタリング提案**:

```python
# src/models/scene_data.py (新規作成)

from pydantic import BaseModel
from typing import Literal

class SceneInfo(BaseModel):
    """シーン情報"""
    type: str
    name: str
    emoji: str
    color: discord.Color

class WallPracticeData(BaseModel):
    """壁打ちシーン専用データ"""
    drill: str = ""
    duration: int = 0
    focus: str = ""
    body_sensation: str = ""
    improvement: str = ""
    issue: str = ""
    tags: list[str] = []
    summary: str = ""
    next_action: str = ""

class SchoolPracticeData(BaseModel):
    """スクールシーン専用データ"""
    coach_feedback: str = ""
    new_technique: str = ""
    practice_content: str = ""
    realization: str = ""
    homework: str = ""
    tags: list[str] = []
    summary: str = ""
    next_action: str = ""

class MatchData(BaseModel):
    """試合シーン専用データ"""
    opponent: str = ""
    opponent_level: str = ""
    score: str = ""
    result: Literal["勝ち", "負け", "不明"] = "不明"
    good_plays: str = ""
    bad_plays: str = ""
    mental: str = ""
    strategy: str = ""
    tags: list[str] = []
    summary: str = ""
    next_action: str = ""

# Union型で統合
SceneData = WallPracticeData | SchoolPracticeData | MatchData | dict
```

**影響度**: 中
**推定工数**: 3-4時間
**効果**: ランタイムエラー削減、コード補完向上

---

### 5. ObsidianManagerの検索メソッド整理

**問題箇所**: `src/storage/obsidian_manager.py`

**問題内容**:
- `search_by_keyword`
- `search_by_date`
- `get_memo_by_tags`
- `find_memo_by_fuzzy_criteria`

これらのメソッドで共通ロジック（ファイル走査、フィルタリング）が重複

**リファクタリング提案**:

```python
class ObsidianManager:
    def _get_all_memos(self) -> list[Dict[str, Any]]:
        """全メモを取得（キャッシュ可能）"""
        md_files = list(self.sessions_path.rglob("*.md"))
        return [self._parse_markdown(f) for f in md_files if f]

    def search(
        self,
        filters: Optional[SearchFilters] = None,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """統一された検索インターフェース"""
        memos = self._get_all_memos()

        if filters:
            if filters.keywords:
                memos = self._filter_by_keywords(memos, filters.keywords)
            if filters.date_range:
                memos = self._filter_by_date_range(memos, filters.date_range)
            if filters.tags:
                memos = self._filter_by_tags(memos, filters.tags, filters.match_all_tags)
            if filters.scene_name:
                memos = self._filter_by_scene(memos, filters.scene_name)

        return memos[:limit]
```

**影響度**: 中
**推定工数**: 2-3時間
**削減コード量**: 約100行

---

### 6. 設定管理の一元化

**問題箇所**: 複数ファイル

**問題内容**:
環境変数読み込みが各所に散在：
- `os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault")`
- `os.getenv("DEBUG", "false").lower() == "true"`
- デフォルト値が統一されていない

**リファクタリング提案**:

```python
# src/config.py (新規作成)

from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """アプリケーション設定"""

    # Discord
    discord_bot_token: str

    # Gemini
    gemini_api_key: str

    # GitHub
    github_repo: str
    github_token: str
    obsidian_path: str = "sessions"

    # Obsidian
    obsidian_vault_path: Path = Path("./obsidian_vault")

    # アプリケーション
    debug: bool = False
    max_file_size_mb: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False

# グローバル設定インスタンス
settings = Settings()
```

使用例：
```python
# 従来
vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault")

# 改善後
from src.config import settings
vault_path = settings.obsidian_vault_path
```

**影響度**: 中
**推定工数**: 2時間
**効果**: 設定管理の一元化、型安全性向上

---

## 🟢 低優先度（Medium）

### 7. 定数の定義

**問題箇所**: 複数ファイル

**問題内容**:
マジックナンバー/文字列が散在：
- `20 * 1024 * 1024` (ファイルサイズ制限)
- `"振り返り・追記"` (セクションタイトル)
- `.ogg`, `.mp3` などの拡張子リスト

**リファクタリング提案**:

```python
# src/constants.py (新規作成)

from pathlib import Path

# ファイル制限
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

# メディア拡張子
AUDIO_EXTENSIONS = [".ogg", ".mp3", ".wav", ".m4a", ".opus", ".webm"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".webm"]

# Markdown セクション
SECTION_TITLE_REFLECTION = "振り返り・追記"
SECTION_TITLE_TRANSCRIPT = "文字起こし全文"

# 調子のレベル
CONDITION_GOOD = "good"
CONDITION_NORMAL = "normal"
CONDITION_BAD = "bad"

# シーンタイプ
SCENE_WALL_PRACTICE = "wall_practice"
SCENE_SCHOOL = "school"
SCENE_MATCH = "match"
SCENE_FREE_PRACTICE = "free_practice"
SCENE_REFLECTION = "reflection"
SCENE_QUESTION = "question"
SCENE_ANALYSIS = "analysis"
```

**影響度**: 低
**推定工数**: 1時間
**効果**: 保守性向上、変更容易性

---

### 8. 依存性注入の導入

**問題箇所**: `src/bot/client.py`

**問題内容**:
```python
class TennisDiscoveryBot(commands.Bot):
    def __init__(self):
        # ハードコーディングされた依存関係
        self.gemini_client = GeminiClient()
        self.github_sync = GitHubSync()
        self.markdown_builder = MarkdownBuilder()
        self.obsidian_manager = ObsidianManager()
```

テストが困難

**リファクタリング提案**:

```python
class TennisDiscoveryBot(commands.Bot):
    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        github_sync: Optional[GitHubSync] = None,
        markdown_builder: Optional[MarkdownBuilder] = None,
        obsidian_manager: Optional[ObsidianManager] = None,
    ):
        # デフォルトまたは注入された依存関係
        self.gemini_client = gemini_client or GeminiClient()
        self.github_sync = github_sync or GitHubSync()
        self.markdown_builder = markdown_builder or MarkdownBuilder()
        self.obsidian_manager = obsidian_manager or ObsidianManager()
```

テスト時：
```python
# モックを注入できる
mock_gemini = MagicMock(spec=GeminiClient)
bot = TennisDiscoveryBot(gemini_client=mock_gemini)
```

**影響度**: 低（機能変更なし、テスト容易性のみ）
**推定工数**: 1-2時間

---

### 9. プロンプトのテンプレート化

**問題箇所**: `src/ai/prompts.py`

**問題内容**:
各シーンのプロンプト関数が似た構造

**リファクタリング提案**:

```python
from string import Template

PROMPT_TEMPLATE = Template("""以下の音声メモから、${scene_name}の情報を抽出してください。

音声メモ:
${text}

抽出する情報（JSON形式）:
${schema}

**重要な注意事項:**
- すべてのフィールドは必須です。値がない場合は空文字列""または適切なデフォルト値を使用
- tags は配列形式で、空の場合は []
- ユーザーが明示的に言及していない項目は空文字列""にする
- 推測や一般論は避け、ユーザーの実際の体験のみを抽出する
- JSON以外のテキストは出力しない
""")

SCENE_SCHEMAS = {
    "wall_practice": {
        "name": "壁打ち練習",
        "schema": {...}
    },
    "school": {
        "name": "スクール練習",
        "schema": {...}
    },
    # ...
}

def get_prompt_for_scene(scene_type: str, text: str) -> str:
    scene_info = SCENE_SCHEMAS.get(scene_type, SCENE_SCHEMAS["free_practice"])
    return PROMPT_TEMPLATE.substitute(
        scene_name=scene_info["name"],
        text=text,
        schema=json.dumps(scene_info["schema"], ensure_ascii=False, indent=2)
    )
```

**影響度**: 低
**推定工数**: 1-2時間
**削減コード量**: 約50行

---

## 📊 リファクタリング優先順位まとめ

| 優先度 | 項目 | 削減コード量 | 工数 | ROI |
|--------|------|--------------|------|-----|
| 🔴 | メッセージハンドラー重複削減 | 300-400行 | 4-6h | 高 |
| 🔴 | Discord Embed集約 | 150-200行 | 2-3h | 高 |
| 🔴 | メディアヘルパー統合 | 80行 | 1-2h | 高 |
| 🟡 | 型安全性向上 | - | 3-4h | 中 |
| 🟡 | ObsidianManager検索統合 | 100行 | 2-3h | 中 |
| 🟡 | 設定管理一元化 | - | 2h | 中 |
| 🟢 | 定数定義 | - | 1h | 低 |
| 🟢 | 依存性注入 | - | 1-2h | 低 |
| 🟢 | プロンプトテンプレート化 | 50行 | 1-2h | 低 |

**合計削減コード量**: 約680-830行
**合計推定工数**: 17-28時間

---

## 推奨実装順序

### Phase 1: 基盤整備 (4-6時間)
1. 設定管理一元化 (`src/config.py`)
2. 定数定義 (`src/constants.py`)
3. 型モデル定義 (`src/models/scene_data.py`)

### Phase 2: コア機能リファクタリング (7-11時間)
4. Discord Embed集約 (`src/bot/helpers/embed_builder.py`)
5. メディアヘルパー統合
6. メッセージハンドラー重複削減 (最大の効果)

### Phase 3: 最適化 (6-11時間)
7. ObsidianManager検索統合
8. プロンプトテンプレート化
9. 依存性注入

---

## テスト戦略

リファクタリング前に以下のテストを追加推奨：

1. **統合テスト** - 既存の `tests/integration/test_phase1.py` を拡張
2. **ユニットテスト** - 各メッセージハンドラーの動作確認
3. **リグレッションテスト** - リファクタリング前後で同じ結果が得られるか

---

## リスク評価

| リスク | 確率 | 影響度 | 対策 |
|--------|------|--------|------|
| 既存機能の破壊 | 中 | 高 | 段階的リファクタリング、テスト追加 |
| パフォーマンス劣化 | 低 | 低 | ベンチマーク実施 |
| 新たなバグ混入 | 中 | 中 | レビュー、テスト |

---

## 結論

コードベースは全体的に機能的ですが、**重複コードが多く保守性に課題**があります。

最優先で取り組むべきは：
1. **メッセージハンドラーの重複削減** - 最大の効果
2. **Embed作成ロジックの集約** - 可読性向上
3. **型安全性の向上** - バグ削減

段階的なリファクタリングにより、コード量を **約680-830行削減**し、保守性と拡張性を大幅に向上できます。
