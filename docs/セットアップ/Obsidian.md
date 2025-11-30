# Obsidian セットアップ

## 概要

Tennis Discovery Agentと連携するObsidianの設定方法です。

---

## 1. 初期セットアップ

### 1.1 Obsidianのインストール

1. [Obsidian公式サイト](https://obsidian.md/)からダウンロード
2. インストール後、新しいVaultを作成
3. Vault名: `Tennis Notes`（任意）
4. 保存場所: `/path/to/obsidian-vault`

### 1.2 基本設定

**設定 → ファイルとリンク:**
```
✅ 新しいノートの保存先: daily/
✅ 添付ファイルの保存先: attachments/
✅ Wikiリンク形式を使用
✅ 相対パスを使用
```

---

## 2. 必須プラグイン

### 2.1 Dataview（データ集計・クエリ）

**インストール:**
```
設定 → コミュニティプラグイン → 閲覧 → "Dataview" で検索 → インストール → 有効化
```

**使用例（今週の練習一覧）:**

````markdown
```dataview
TABLE scene as "シーン", tags as "タグ"
FROM "daily"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```
````

### 2.2 Calendar（カレンダービュー）

**インストール:**
```
設定 → コミュニティプラグイン → "Calendar" → インストール → 有効化
```

**設定:**
```
週の開始: 月曜日
ノートの保存先: daily/
ファイル名形式: YYYY-MM-DD
```

---

## 3. 推奨プラグイン（Phase 2以降）

### 3.1 Templater（テンプレート自動化）

**設定:**
```
テンプレートフォルダ: templates/
自動ジャンプ: 有効
```

### 3.2 QuickAdd（素早い入力）

マクロを作成して、シーン別にワンクリックでメモを作成。

### 3.3 Periodic Notes（週次レビュー）

週次ノート設定:
```
フォーマット: YYYY-[W]WW
フォルダ: weekly-reviews/
テンプレート: templates/weekly-review.md
```

---

## 4. ディレクトリ構造

```
obsidian-vault/
├── daily/
│   ├── 2025-01-27-壁打ち.md
│   ├── 2025-01-27-スクール.md
│   └── 2025-01-28-試合.md
├── weekly-reviews/
│   └── 2025-W04.md
├── attachments/
│   └── 2025-01-27/
│       ├── 2025-01-27_壁打ち_143000.jpg
│       └── 2025-01-27_壁打ち_150000.mp4
├── templates/
│   ├── wall-practice.md
│   ├── school.md
│   └── match.md
└── index.md
```

---

## 5. Botとの連携設定

### 5.1 環境変数

```env
OBSIDIAN_VAULT_PATH=/path/to/obsidian-vault
```

### 5.2 GitHub連携（オプション）

```bash
cd /path/to/obsidian-vault

# Gitリポジトリを初期化
git init

# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/tennis-notes.git

# Git LFSを設定（画像・動画用）
git lfs install
git lfs track "attachments/**/*.jpg"
git lfs track "attachments/**/*.png"
git lfs track "attachments/**/*.mp4"
git lfs track "attachments/**/*.mov"

# 初回コミット
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

## 6. ダッシュボードの作成（オプション）

`index.md` を作成：

````markdown
# Tennis Discovery Dashboard

## 最近の練習

```dataview
TABLE scene as "シーン", tags as "タグ"
FROM "daily"
SORT date DESC
LIMIT 5
```

## 継続中の課題

```dataview
LIST issue
FROM "daily"
WHERE issue != null AND issue != ""
SORT date DESC
LIMIT 5
```
````

---

## 次のステップ

- [Raspberry Pi環境構築](04-raspberry-pi.md)（常時稼働する場合）
- [環境変数と設定ファイル](05-environment.md)
