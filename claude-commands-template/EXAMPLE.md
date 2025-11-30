# 使用例

実際のプロジェクトでこのテンプレートを使用する例を示します。

## シナリオ: Webアプリケーション開発

### 1. 初期セットアップ

```bash
# テンプレートをプロジェクトにコピー
cp -r claude-commands-template/.claude my-web-app/
cp claude-commands-template/docs/*.template my-web-app/docs/
cp claude-commands-template/CLAUDE.md.template my-web-app/CLAUDE.md

cd my-web-app
```

### 2. CLAUDE.mdのカスタマイズ例

```markdown
# My Web App

## 概要
React + Node.js + PostgreSQLで構築するタスク管理アプリケーション

## 技術スタック
- **フロントエンド**: React 18, TypeScript, Tailwind CSS
- **バックエンド**: Node.js, Express, Prisma ORM
- **データベース**: PostgreSQL 15
- **言語**: TypeScript
- **主要ライブラリ**: React Query, Zod, JWT
- **インフラ**: Vercel (フロント), Railway (バックエンド)
```

### 3. docs/plan.mdのカスタマイズ例

```markdown
# My Web App - タスク管理

## Phase 1: 基盤構築

### 概要
開発環境のセットアップとプロジェクト基盤の構築

### タスク

#### 🔴 高優先度
- [ ] Node.js + TypeScript環境セットアップ
- [ ] React + Viteプロジェクト作成
- [ ] PostgreSQLデータベースセットアップ
- [ ] Prismaスキーマ設計

#### 🟡 中優先度
- [ ] ESLint + Prettierの設定
- [ ] CI/CDパイプライン構築

## Phase 2: 認証機能

### 概要
ユーザー登録・ログイン機能の実装

### タスク

#### 🔴 高優先度
- [ ] ユーザーモデル作成
- [ ] JWT認証実装
- [ ] ログインAPIエンドポイント
- [ ] ユーザー登録APIエンドポイント

#### 🟡 中優先度
- [ ] パスワードリセット機能
- [ ] メール認証機能

## Phase 3: タスク管理機能

### タスク

#### 🔴 高優先度
- [ ] タスクモデル作成
- [ ] タスク一覧API
- [ ] タスク作成・更新・削除API
- [ ] タスク一覧UI実装
- [ ] タスク作成フォーム実装
```

### 4. 実際の作業フロー

#### セッション1: 環境セットアップ

```
開発者: /start

Claude Code:
[docs/plan.md を読み込み]
[最初の未完了タスク「Node.js + TypeScript環境セットアップ」を検出]
[実装開始...]

package.jsonを作成し、TypeScriptとNode.jsの設定を完了しました。

✅ 完了: Node.js + TypeScript環境セットアップ
📝 docs/plan.md を更新しました
📝 docs/session-log.md に記録しました

次のタスク: React + Viteプロジェクト作成
/clear → /start で次へ進めます。
```

#### セッション2: Reactプロジェクト作成

```
開発者: /status

Claude Code:
📊 My Web App - 進捗状況

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Phase 1: 基盤構築
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
進捗: ████░░░░░░░░░░░░░░░░ 1/6 (17%)

完了:
✅ Node.js + TypeScript環境セットアップ

未完了:
⬜ React + Viteプロジェクト作成（優先度: 高）
⬜ PostgreSQLデータベースセットアップ（優先度: 高）
⬜ Prismaスキーマ設計（優先度: 高）
⬜ ESLint + Prettierの設定（優先度: 中）
⬜ CI/CDパイプライン構築（優先度: 中）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 次のアクション
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 高優先度: React + Viteプロジェクト作成

/start で実装を開始できます。

開発者: /start

Claude Code:
[実装開始...]
```

### 5. session-log.mdの記録例

```markdown
# セッションログ

## 2025-11-30 10:00
**完了**: Node.js + TypeScript環境セットアップ
**変更ファイル**:
  - package.json
  - tsconfig.json
  - .gitignore

**次回の作業**: React + Viteプロジェクト作成
**備考**: TypeScript strictモードを有効化。Node.js 20 LTS推奨。

---

## 2025-11-30 11:30
**完了**: React + Viteプロジェクト作成
**変更ファイル**:
  - frontend/package.json
  - frontend/vite.config.ts
  - frontend/src/App.tsx
  - frontend/index.html

**次回の作業**: PostgreSQLデータベースセットアップ
**備考**: Vite 5.0を使用。Tailwind CSSも同時にセットアップ。

---

## 2025-11-30 14:00
**完了**: PostgreSQLデータベースセットアップ
**変更ファイル**:
  - docker-compose.yml
  - .env.example
  - backend/prisma/schema.prisma

**次回の作業**: Prismaスキーマ設計
**備考**: Docker ComposeでPostgreSQL 15をローカル環境に構築。
```

---

## 利点

このテンプレートを使用することで：

1. **コンテキストの継続性**: `/clear` 後も前回の作業から再開可能
2. **進捗の可視化**: いつでも `/status` で全体像を把握
3. **自動記録**: 完了タスクと変更内容が自動的にログに記録
4. **効率的な作業**: Claude Codeが次のタスクを自動提案

---

## カスタマイズのヒント

- **フェーズは柔軟に**: Phase数は自由に増減可能
- **優先度の活用**: 🔴🟡🟢で視覚的に管理
- **備考の活用**: 技術的な決定や制約を記録すると、後で役立つ
- **コマンドの追加**: プロジェクト固有のコマンドを `.claude/commands/` に追加可能
