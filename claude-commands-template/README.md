# Claude Code Commands Template

Claude Codeプロジェクトで使用する、タスク管理用のカスタムコマンドテンプレートです。
新規プロジェクトに簡単に導入でき、効率的なプロジェクト管理を実現します。

## 機能

### `/start` - 作業開始コマンド
- `docs/plan.md` から次の未完了タスクを自動検出
- `docs/session-log.md` で前回の作業状況を確認
- 関連ファイルを分析してから実装開始
- タスク完了時の自動記録をサポート

### `/status` - 進捗確認コマンド
- フェーズごとの完了率を可視化
- 最新のセッションログを表示
- 次に取り組むべきタスクを提案

## セットアップ

### 1. ファイルをプロジェクトにコピー

```bash
# このテンプレートディレクトリを新規プロジェクトにコピー
cp -r claude-commands-template/.claude /path/to/your/project/
cp claude-commands-template/docs/*.template /path/to/your/project/docs/
cp claude-commands-template/CLAUDE.md.template /path/to/your/project/CLAUDE.md
```

### 2. テンプレートをカスタマイズ

以下のファイルをプロジェクトに合わせて編集：

#### `CLAUDE.md`
```bash
# テンプレートからコピーして編集
cd /path/to/your/project
mv CLAUDE.md.template CLAUDE.md
# エディタで開いてプロジェクト固有の内容を記入
```

プロジェクト固有の情報を追加：
- 技術スタック
- ディレクトリ構造
- コーディング規約
- アーキテクチャ原則

#### `docs/plan.md`
```bash
mv docs/plan.md.template docs/plan.md
```

プロジェクトのタスクを記入：
- フェーズ構成（Phase 1, Phase 2...）
- 各フェーズのタスクリスト
- 優先度設定

#### `docs/session-log.md`
```bash
mv docs/session-log.md.template docs/session-log.md
```

最初のエントリを記録：
- プロジェクト開始日
- 初期セットアップ内容

### 3. 動作確認

```bash
# Claude Codeで以下のコマンドを実行
/status  # 進捗状況を確認
/start   # 最初のタスクを開始
```

## ディレクトリ構造

```
your-project/
├── .claude/
│   └── commands/
│       ├── start.md          # 作業開始コマンド
│       └── status.md         # 進捗確認コマンド
├── docs/
│   ├── plan.md               # タスク管理ファイル
│   └── session-log.md        # セッションログ
└── CLAUDE.md                 # プロジェクト指示ファイル
```

## 使い方

### 日常的なワークフロー

1. **作業開始時**
   ```
   /status  # 現在の進捗を確認
   /start   # 次のタスクを開始
   ```

2. **作業中**
   - Claude Codeが自動的にタスクを実行
   - 完了時に `docs/plan.md` と `docs/session-log.md` を自動更新

3. **コンテキストクリア後**
   ```
   /clear   # コンテキストをクリア
   /start   # 前回の続きから再開
   ```

### タスク完了時の自動処理

Claude Codeは以下を自動的に実行します：

1. `docs/plan.md` の該当タスクを `[x]` に更新
2. `docs/session-log.md` に完了記録を追記
3. 重要な変更があれば `CLAUDE.md` を更新
4. 次のタスクを提案

## カスタマイズ

### コマンドの追加

`.claude/commands/` に新しい `.md` ファイルを作成：

```markdown
---
description: コマンドの説明
---

# /your-command - コマンド名

コマンドの詳細な説明と実行内容
```

### フェーズ構成の変更

`docs/plan.md` でフェーズ数や構成を自由に変更可能：

```markdown
## Phase 1: 基盤構築
- [ ] タスク1
- [ ] タスク2

## Phase 2: 機能実装
- [ ] タスク3
- [ ] タスク4
```

## ベストプラクティス

### 1. タスクの粒度
- 1タスク = 1-3時間で完了できる単位
- 大きすぎるタスクはサブタスクに分割

### 2. セッションログの記録
- 毎回の作業後に記録（自動化されています）
- 技術的な決定事項や制約を「備考」に記録
- 次回のために重要なコンテキストを残す

### 3. CLAUDE.mdの更新
- 重要なアーキテクチャ変更は「最近の変更」に追記
- 新しい技術的制約や既知の問題を文書化
- セキュリティ関連の注意事項を明記

## トラブルシューティング

### コマンドが認識されない
- `.claude/commands/` ディレクトリが正しい場所にあるか確認
- ファイル名が `.md` 拡張子で終わっているか確認
- Claude Codeを再起動

### タスクが自動検出されない
- `docs/plan.md` の形式が正しいか確認（`- [ ]` または `- [x]`）
- ファイルパスが正しいか確認

## ライセンス

MIT License

## 貢献

改善提案やバグ報告は歓迎します。
