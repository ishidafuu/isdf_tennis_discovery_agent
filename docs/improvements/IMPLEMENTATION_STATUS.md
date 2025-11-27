# Tennis Discovery Agent - 実装状況

最終更新: 2025-11-27

## 📊 Phase 1 実装進捗

**全体進捗: 16/20 タスク完了 (80%)**

---

## ✅ 完了済み機能

### 1. 基礎機能
- [x] チャンネル分け機能（#壁打ち、#スクール、#試合、#フリー練習、#振り返り）
- [x] シーン別プロンプト・構造化データ抽出
- [x] シーン別Markdownテンプレート
- [x] ファイル名重複バグ修正（タイムスタンプ追加: YYYY-MM-DD-HHMMSS-シーン名.md）

### 2. マルチモーダル入力
- [x] **音声メモ機能** (既存)
  - Gemini 2.5 Flash による文字起こし
  - シーン別構造化データ抽出
  - GitHub自動プッシュ

- [x] **テキストメモ機能**
  - URL自動検出（regex: `r'https?://[^\s<>"\']+'`）
  - 最小文字数: 10文字
  - コマンド除外（`!`で始まるメッセージ）

- [x] **画像メモ機能**
  - ファイルサイズ制限: 20MB
  - 対応形式: JPG, JPEG, PNG, GIF
  - 保存先: `attachments/{date}/YYYY-MM-DD_シーン名_HHMMSS.ext`
  - ユーザーコメント記録（AI解析なし）
  - Markdown埋め込み: `![[filepath]]`

- [x] **動画メモ機能**
  - ファイルサイズ制限: 20MB
  - 対応形式: MP4, MOV, AVI, WEBM
  - 画像と同じ保存・管理構造

### 3. ファイル管理
- [x] **ObsidianManager実装** (`src/storage/obsidian_manager.py`)
  - `get_latest_memo(scene_name)`: 最新メモ取得
  - `get_memos_in_range(start_date, end_date, scene_name)`: 期間内メモ取得
  - `search_by_keyword(keyword, scene_name)`: キーワード検索
  - `search_by_date(target_date, scene_name)`: 日付検索
  - `get_memo_by_tags(tags, match_all)`: タグ検索
  - `find_memo_by_fuzzy_criteria(date_text, keywords, scene_name)`: あいまい検索
  - `append_to_memo(file_path, append_text)`: メモ追記
  - 日付抽出機能:
    - 完全日付: YYYY/MM/DD, YYYY-MM-DD
    - 短縮日付: MM/DD（今年）
    - 相対日付: 昨日, 一昨日, N日前

- [x] **Git LFS セットアップ** (`.gitattributes`)
  - 画像ファイル: jpg, jpeg, png, gif
  - 動画ファイル: mp4, mov, avi, webm
  - 音声ファイル: ogg, mp3, wav, m4a, opus

### 4. サイクル追跡機能
- [x] **前回ログ読み込み機能**
  - 同一シーンの最新メモを自動取得
  - Discord応答に「🔄 サイクル」セクション表示
  - 表示内容:
    - 📅 前回の日付
    - 🎯 前回の身体感覚（50文字まで）
    - 📝 前回の課題（100文字まで）
  - 音声・テキストメモ両方に対応

### 5. 振り返り機能
- [x] **#振り返りチャンネル実装**
  - 専用チャンネル検出: `is_reflection_channel()`
  - あいまい検索による過去メモ特定
  - 日付・キーワード抽出
  - 自動追記機能（タイムスタンプ付きCallout形式）
  - 複数候補がある場合は他の候補も表示
  - GitHub自動同期

**使用例:**
```
ユーザー（#振り返りチャンネル）:
「1/15のサーブメモに追記。実はその前日にコーチがトスについてアドバイスしてた」

Bot:
✅ 2025-01-15 の 壁打ち メモに追記しました
📄 追記したメモ: 2025-01-15-143052-壁打ち.md
```

### 6. 環境設定
- [x] **環境変数追加** (`.env.example`)
  - `OBSIDIAN_VAULT_PATH`: ローカルVaultパス（画像・動画保存用）
  - `ADMIN_USER_ID`: 管理者のDiscord User ID（DM処理用）

---

## 🔄 実装済みコード構造

### ディレクトリ構成
```
src/
├── ai/
│   ├── gemini_client.py          # Gemini API処理（音声・テキスト）
│   ├── prompts.py                # シーン別プロンプト
│   └── structured_extraction.py  # 構造化データ抽出
├── bot/
│   ├── client.py                 # Discord Bot メインロジック
│   └── channel_handler.py        # チャンネル・シーン検出
├── storage/
│   ├── github_sync.py            # GitHub連携
│   ├── markdown_builder.py       # Markdown生成
│   ├── markdown_templates.py     # シーン別テンプレート
│   └── obsidian_manager.py       # ファイル管理・検索 ⭐NEW
└── models/
    └── session.py                # PracticeSession モデル

docs/improvements/                 # 実装計画ドキュメント
└── IMPLEMENTATION_STATUS.md      # 本ファイル ⭐NEW

.gitattributes                    # Git LFS設定 ⭐NEW
```

### 主要な実装内容

#### `src/bot/client.py`
```python
class TennisDiscoveryBot:
    def __init__(self):
        self.obsidian_manager = ObsidianManager()  # ⭐NEW

    async def on_message(self, message):
        # 振り返りチャンネルの特別処理 ⭐NEW
        if is_reflection_channel(message.channel.name):
            await self._process_reflection_message(message)

        # 音声・画像・動画・テキストの処理
        ...

    # ⭐NEW メソッド
    async def _process_reflection_message(self, message)
    async def _process_image_message(self, message, attachment)
    async def _process_video_message(self, message, attachment)
    def _get_previous_log_summary(self, scene_name)
```

#### `src/storage/obsidian_manager.py` ⭐NEW
```python
class ObsidianManager:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.sessions_path = self.vault_path / "sessions"

    # ファイル検索
    def get_latest_memo(self, scene_name)
    def get_memos_in_range(self, start_date, end_date, scene_name)
    def search_by_keyword(self, keyword, scene_name, max_results)
    def search_by_date(self, target_date, scene_name)
    def get_memo_by_tags(self, tags, match_all)

    # あいまい検索
    def find_memo_by_fuzzy_criteria(self, date_text, keywords, scene_name)

    # 日付抽出
    def _extract_date_from_text(self, text)

    # ファイル操作
    def _parse_markdown(self, file_path)
    def append_to_memo(self, file_path, append_text, section_title)
```

---

## 🚧 未完了タスク（残り4つ）

### 1. 週次レビュー自動生成機能
**優先度: 中**

**要件:**
- APSchedulerを使用して定期実行
- 毎週日曜日夜に過去1週間のメモを集約
- Geminiで週次サマリーを生成
- 専用の週次レビューMarkdownを作成
- GitHub自動プッシュ

**実装場所:**
- `src/scheduler/weekly_review.py` (新規作成)
- `src/bot/client.py` に統合

**参考資料:**
- `docs/improvements/phases/01-foundation/output.md`

**依存関係:**
- `ObsidianManager.get_memos_in_range()` ✅ 実装済み

---

### 2. 練習開始時リマインド機能
**優先度: 低**

**要件:**
- 曜日・時間ベースのリマインダー
- Discord DMまたはチャンネルに通知
- 前回の課題を含めたリマインド

**実装場所:**
- `src/scheduler/reminders.py` (新規作成)

**参考資料:**
- `docs/improvements/phases/01-foundation/index.md`

**依存関係:**
- `ObsidianManager.get_latest_memo()` ✅ 実装済み

---

### 3. Discord DM処理（Bot停止時バックアップ）
**優先度: 高**

**要件:**
- Bot起動時に未処理DMをチェック
- 音声・画像・動画メッセージを処理
- ✅リアクションで処理済みマーク
- シーン情報をメッセージ本文から抽出

**実装場所:**
- `src/bot/client.py` の `on_ready()` メソッド拡張
- `src/bot/dm_handler.py` (新規作成推奨)

**参考資料:**
- `docs/improvements/phases/01-foundation/input.md` (lines 362-421)

**実装例（ドキュメントより）:**
```python
@bot.event
async def on_ready():
    await process_pending_dms()

async def process_pending_dms():
    admin_user_id = int(os.getenv('ADMIN_USER_ID'))
    admin_user = await bot.fetch_user(admin_user_id)
    dm_channel = await admin_user.create_dm()

    async for message in dm_channel.history(limit=50):
        # ✅リアクションがあればスキップ
        if any(r.emoji == '✅' for r in message.reactions):
            continue

        # 音声メッセージを処理
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith('audio/'):
                    scene = extract_scene_from_text(message.content)
                    await process_voice_with_scene(message, attachment, scene)
                    await message.add_reaction('✅')
```

---

### 4. Phase 1全機能の統合テスト
**優先度: 高**

**テスト項目:**
- [ ] 音声メモ（各シーン）
- [ ] テキストメモ（URL含む/なし）
- [ ] 画像メモ（コメント含む/なし）
- [ ] 動画メモ
- [ ] 前回ログ表示（音声・テキスト）
- [ ] 振り返りチャンネル（日付抽出、キーワード検索）
- [ ] ファイル名の一意性（同日複数投稿）
- [ ] Git LFS動作確認
- [ ] GitHub同期

**実装場所:**
- `tests/integration/test_phase1.py` (新規作成)
- 手動テスト手順書: `docs/improvements/testing/phase1-manual-tests.md`

---

## 📝 次回セッションで実施すべきこと

### 推奨順序:

1. **Discord DM処理の実装** （優先度: 高）
   - Bot停止時の重要な情報を逃さないための機能
   - 実装が比較的シンプル
   - ユーザー体験向上に直結

2. **Phase 1統合テスト** （優先度: 高）
   - 既存機能の動作確認
   - バグの早期発見
   - リリース前の品質保証

3. **週次レビュー自動生成** （優先度: 中）
   - より高度な機能
   - APSchedulerの導入が必要
   - Geminiによるサマリー生成実装

4. **練習開始時リマインド** （優先度: 低）
   - Nice-to-have機能
   - Phase 2での実装でも可

---

## 🔧 技術的な注意点

### 既知の制約・設計決定
1. **ファイル名形式**: `YYYY-MM-DD-HHMMSS-シーン名.md`
   - タイムスタンプで一意性を保証
   - 同日複数投稿に対応

2. **画像・動画の保存先**: `attachments/{date}/YYYY-MM-DD_シーン名_HHMMSS.ext`
   - 日付ごとにフォルダ分け
   - Git LFSで管理

3. **Git LFS必須ファイル**:
   - 画像: jpg, jpeg, png, gif
   - 動画: mp4, mov, avi, webm
   - 音声: ogg, mp3, wav, m4a, opus

4. **前回ログ読み込み**:
   - `ObsidianManager.get_latest_memo(scene_name)` を使用
   - 同一シーンの最新メモを取得
   - bodyから `## 次回` セクションを正規表現で抽出

5. **振り返りチャンネル**:
   - あいまい検索で最も関連性の高いメモに追記
   - 複数候補がある場合は他の候補も表示（最大2件）

---

## 📚 参考ドキュメント

- **Phase 1 全体**: `docs/improvements/phases/01-foundation/index.md`
- **入力機能**: `docs/improvements/phases/01-foundation/input.md`
- **処理機能**: `docs/improvements/phases/01-foundation/processing.md`
- **出力機能**: `docs/improvements/phases/01-foundation/output.md`
- **クイックスタート**: `docs/improvements/QUICKSTART.md`

---

## 🎯 Phase 1 完了基準

Phase 1を「完了」とみなす条件:

- ✅ マルチモーダル入力（音声・テキスト・画像・動画）
- ✅ シーン別処理（壁打ち・スクール・試合・フリー練習）
- ✅ サイクル追跡（前回→今回→次回）
- ✅ 振り返り機能
- ⬜ DM処理（Bot停止時バックアップ）
- ⬜ 統合テスト完了
- ⬜ 週次レビュー（Optional）
- ⬜ リマインダー（Optional）

**現状: 必須機能の80%完了、Optional機能は未着手**

---

## 🚀 次フェーズへの準備

Phase 1完了後、Phase 2「対話の深化」に進む予定:
- ユーザーとの対話的なやり取り
- 質問による深掘り
- コーチング的なフィードバック

詳細: `docs/improvements/phases/02-dialogue/index.md`

---

最終更新: 2025-11-27
現在のブランチ: `claude/review-improvements-docs-017JEdvVNwBgwjGomM8jH3bb`
最新コミット: `2cf288d - feat: Implement review/reflection channel for retrospective notes`
