# 🔄 次のセッション用プロンプト

次のセッションでClaude Codeを起動したら、このファイルの内容をコピーして送信してください。

---

## 📝 プロンプト（以下をコピーして送信）

```
Tennis Discovery Agent の Phase 2 実装を開始したいです。

# 現在の状態

## Phase 1 完了状況
✅ Phase 1（記録の構造化）は完全に実装済み・動作確認済み

実装済み機能：
- Discord Botによる音声メッセージ受信
- Gemini 2.5 Flash による音声文字起こし・構造化データ抽出
- Obsidian形式のMarkdown生成（Callout対応）
- GitHubへの自動Push（リポジトリ: ishidafuu/isdf_tennis_vault）
- スマホ（Android）でのObsidian閲覧環境

使用技術：
- Python 3.12
- discord.py 2.3.0+
- Gemini 2.5 Flash (モデル名: "gemini-2.5-flash")
- PyGithub 2.1.1+
- Pydantic 2.0.0+

# Phase 2 でやりたいこと

Phase 2のテーマ：「継続性の担保」

実装する機能：
1. `/start` コマンド - 練習開始時に前回の課題をリマインド
2. `/finish` コマンド - 練習終了時に振り返りを促す
3. セッション管理 - スレッドベースで1つの練習を管理
4. 前回ログの読み込み - GitHubから最新セッションを取得

詳細な計画は `docs/PHASE2_PLAN.md` に記載されています。

# 質問

1. Phase 2 の実装を開始する前に、Phase 1 の実装内容を確認してもらえますか？
2. Phase 2 の実装計画（docs/PHASE2_PLAN.md）を読んで、実装の優先順位や進め方についてアドバイスをください
3. 準備ができたら、Step 1（基本的な `/start` コマンド）から実装を開始しましょう

# 参考ドキュメント

- `docs/PHASE1_COMPLETION.md` - Phase 1 完了報告
- `docs/PHASE2_PLAN.md` - Phase 2 詳細計画
- `README.md` - プロジェクト概要
- `src/bot/client.py` - Discord Bot本体
- `src/ai/gemini_client.py` - Gemini API処理
- `src/storage/github_sync.py` - GitHub同期
- `src/models/session.py` - データモデル
```

---

## 💡 補足情報

### 重要なファイルパス

**実装済みのコア機能**:
- `src/bot/client.py` - Discord Bot（音声メッセージ処理）
- `src/ai/gemini_client.py` - Gemini API クライアント
- `src/storage/markdown_builder.py` - Markdown生成
- `src/storage/github_sync.py` - GitHub同期
- `src/models/session.py` - データモデル（PracticeSession等）

**Phase 2 で新規作成予定**:
- `src/bot/commands.py` - /start, /finish コマンド
- `src/storage/markdown_parser.py` - Markdownパース
- `src/storage/session_manager.py` - セッション状態管理
- `src/models/session_state.py` - SessionState, SessionReminder

### 環境変数（.env）

```bash
DISCORD_BOT_TOKEN=（設定済み）
GEMINI_API_KEY=（設定済み）
GITHUB_TOKEN=（設定済み）
GITHUB_REPO=ishidafuu/isdf_tennis_vault
OBSIDIAN_PATH=sessions
DEBUG=true
```

### 既知の問題と解決済み事項

1. **Geminiモデル名**: `gemini-2.5-flash` を使用（過去に404エラーがあったため注意）
2. **Pydanticバリデーション**: `PracticeSession.condition` は `Optional[str]` で実装済み
3. **スマホ同期**: Obsidian Gitプラグインで5分間隔の自動同期設定済み

### 動作確認方法

```bash
# Botの起動
cd ~/Documents/repository/isdf_tennis_discovery_agent
source venv/bin/activate
python main.py

# セットアップ確認
python check_setup.py

# 利用可能なGeminiモデルの確認
python check_models.py
```

### GitHubリポジトリ

- **Bot本体**: `ishidafuu/isdf_tennis_discovery_agent`
- **Obsidian Vault**: `ishidafuu/isdf_tennis_vault`
- **ブランチ**: `claude/plan-app-development-01BitVbtVooMWHRSnQMBSUy2`

---

## 🎯 次のセッションのゴール

Phase 2 の実装を開始し、少なくとも以下を完成させる：

**最小目標**:
- [ ] `/start` コマンドの基本実装
- [ ] GitHubから最新セッションを取得する機能
- [ ] 前回のNext Actionを表示

**理想目標**:
- [ ] `/start` と `/finish` の完全実装
- [ ] スレッドベースのセッション管理
- [ ] 動作確認とテスト

---

## 📞 質問があれば

Phase 2の実装中に不明点があれば、以下を参照：
- Phase 1のコードを見る（特に `src/bot/client.py`）
- `docs/PHASE2_PLAN.md` の詳細設計を確認
- Discord.py のドキュメント: https://discordpy.readthedocs.io/

---

**準備完了！次のセッションで Phase 2 を実装しましょう！**
