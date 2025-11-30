# クイックスタートガイド

Claude Code Commands Templateを5分でセットアップ。

## ステップ1: ファイルをコピー（1分）

```bash
# このリポジトリをクローン
git clone <repository-url> claude-commands-template
cd claude-commands-template

# 新規プロジェクトにコピー
PROJECT_DIR="/path/to/your/project"

# コマンドファイルをコピー
cp -r .claude "$PROJECT_DIR/"

# ドキュメントテンプレートをコピー
mkdir -p "$PROJECT_DIR/docs"
cp docs/plan.md.template "$PROJECT_DIR/docs/plan.md"
cp docs/session-log.md.template "$PROJECT_DIR/docs/session-log.md"

# CLAUDE.mdテンプレートをコピー
cp CLAUDE.md.template "$PROJECT_DIR/CLAUDE.md"
```

## ステップ2: CLAUDE.mdを編集（2分）

```bash
cd "$PROJECT_DIR"
# お好みのエディタでCLAUDE.mdを開く
vim CLAUDE.md  # または code CLAUDE.md
```

最低限、以下を記入：

1. **プロジェクト名**: 1行目の `[プロジェクト名]` を置換
2. **概要**: プロジェクトの目的を1-2文で記述
3. **技術スタック**: 使用している主要な技術を列挙

## ステップ3: plan.mdを編集（2分）

```bash
vim docs/plan.md  # または code docs/plan.md
```

最初のタスクを3-5個追加：

```markdown
## Phase 1: 基盤構築

### タスク

#### 🔴 高優先度
- [ ] 環境セットアップ
- [ ] READMEの作成
- [ ] 基本的なプロジェクト構造の構築
```

## ステップ4: 動作確認（30秒）

Claude Codeで以下を実行：

```
/status
```

以下のような出力が表示されればOK：

```
📊 [プロジェクト名] - 進捗状況

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Phase 1: 基盤構築
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
進捗: ░░░░░░░░░░░░░░░░░░░░ 0/3 (0%)

未完了:
⬜ 環境セットアップ（優先度: 高）
⬜ READMEの作成（優先度: 高）
⬜ 基本的なプロジェクト構造の構築（優先度: 高）
```

## ステップ5: 作業開始（すぐに）

```
/start
```

Claude Codeが自動的に：
1. 最初の未完了タスクを特定
2. 関連ファイルを分析
3. 実装を開始

---

## よくある質問

### Q: 既存プロジェクトに導入できますか？
**A:** はい。既存の構造を壊さずに `.claude/` と `docs/` を追加できます。

### Q: フェーズはいくつまで増やせますか？
**A:** 制限なし。`docs/plan.md` で自由に追加できます。

### Q: コマンドをカスタマイズできますか？
**A:** はい。`.claude/commands/` に新しい `.md` ファイルを追加すればOKです。

### Q: 既存の `docs/` ディレクトリと競合しますか？
**A:** いいえ。`plan.md` と `session-log.md` のみ追加されます。

---

## 次のステップ

- 📖 [README.md](README.md) - 詳細な機能説明
- 🎯 [CLAUDE.md.template](CLAUDE.md.template) - カスタマイズ例
- 📝 [docs/plan.md.template](docs/plan.md.template) - タスク管理例

---

**5分でセットアップ完了！ `/start` で開発を始めましょう。**
