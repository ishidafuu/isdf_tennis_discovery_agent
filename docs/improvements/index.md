# Tennis Discovery Agent - ドキュメント索引

## このドキュメントについて

Tennis Discovery Agentの改善実装を開始するための包括的なドキュメント集です。

**対象読者:** 開発者（実装を担当する方）

---

## クイックナビゲーション

### 今すぐ始めたい方

| ドキュメント | 説明 | 所要時間 |
|-------------|------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | 最短で始める完全ガイド | 10分 |
| **[setup/03-raspberry-pi.md](setup/03-raspberry-pi.md)** | Raspberry Piセットアップ | 30分 |

### 全体像を把握したい方

| ドキュメント | 説明 |
|-------------|------|
| [overview/01-vision.md](overview/01-vision.md) | プロジェクトのビジョンと設計思想 |
| [overview/02-architecture.md](overview/02-architecture.md) | システムアーキテクチャ |
| [overview/03-success-criteria.md](overview/03-success-criteria.md) | 成功の定義と評価基準 |

---

## ドキュメント構成

### 1. 概要 (`overview/`)

プロジェクトの全体像と設計思想を説明します。

- [index.md](overview/index.md) - 概要セクションの索引
- [01-vision.md](overview/01-vision.md) - ビジョン・設計思想
- [02-architecture.md](overview/02-architecture.md) - アーキテクチャ概要
- [03-success-criteria.md](overview/03-success-criteria.md) - 成功の定義

### 2. 実装フェーズ (`phases/`)

段階的な実装ガイドです。Phase 1から順に進めてください。

- [index.md](phases/index.md) - フェーズセクションの索引

#### Phase 1: 基盤強化 (`phases/01-foundation/`)
- [index.md](phases/01-foundation/index.md) - Phase 1の概要とタスク
- [input.md](phases/01-foundation/input.md) - 入力機能（音声・テキスト・画像・動画）
- [processing.md](phases/01-foundation/processing.md) - 処理機能（構造化・前回ログ関連付け）
- [output.md](phases/01-foundation/output.md) - 出力機能（Markdown・週次レビュー）

#### Phase 2: 対話の深化 (`phases/02-dialogue/`)
- [index.md](phases/02-dialogue/index.md) - Phase 2の概要とタスク
- [features.md](phases/02-dialogue/features.md) - ソクラテス式問答・ボタンUI

#### Phase 3: データ活用 (`phases/03-data-utilization/`)
- [index.md](phases/03-data-utilization/index.md) - Phase 3の概要とタスク
- [features.md](phases/03-data-utilization/features.md) - 検索・統計・リマインド

#### Phase 4: 高度な分析 (`phases/04-advanced-analysis/`)
- [index.md](phases/04-advanced-analysis/index.md) - Phase 4の概要とタスク
- [features.md](phases/04-advanced-analysis/features.md) - ベクトル検索・パターン分析

### 3. 技術詳細 (`technical/`)

実装に必要な技術的な詳細を説明します。

- [index.md](technical/index.md) - 技術セクションの索引
- [data-structures.md](technical/data-structures.md) - データ構造の定義
- [discord-bot.md](technical/discord-bot.md) - Discord Bot実装
- [ai-processing.md](technical/ai-processing.md) - AI処理（文字起こし・構造化）
- [obsidian-storage.md](technical/obsidian-storage.md) - Obsidian保存・検索
- [knowledge-rag.md](technical/knowledge-rag.md) - ナレッジ統合（RAG）
- [security.md](technical/security.md) - セキュリティ考慮事項

### 4. セットアップ (`setup/`)

環境構築の詳細ガイドです。

- [index.md](setup/index.md) - セットアップセクションの索引
- [01-discord-bot.md](setup/01-discord-bot.md) - Discord Bot作成
- [02-gemini-api.md](setup/02-gemini-api.md) - Gemini API設定
- [03-obsidian.md](setup/03-obsidian.md) - Obsidianセットアップ
- [04-raspberry-pi.md](setup/04-raspberry-pi.md) - Raspberry Piセットアップ
- [05-environment.md](setup/05-environment.md) - 環境変数と設定ファイル

### 5. リファレンス (`reference/`)

コマンドや設定のリファレンスです。

- [index.md](reference/index.md) - リファレンスセクションの索引
- [commands.md](reference/commands.md) - コマンドリファレンス
- [environment-vars.md](reference/environment-vars.md) - 環境変数
- [troubleshooting.md](reference/troubleshooting.md) - トラブルシューティング

---

## 推奨する読み順

### 初回セットアップ時

```
1. QUICKSTART.md               # まず動かす
2. setup/03-raspberry-pi.md    # 環境構築の詳細
3. setup/05-obsidian.md        # Obsidianの設定
```

### 実装開始時

```
1. overview/01-vision.md       # ビジョンを理解
2. overview/02-architecture.md # 全体像を把握
3. phases/01-foundation/       # Phase 1から順に実装
```

### 特定機能の実装時

```
技術詳細 (technical/) から該当ドキュメントを参照
```

---

## ドキュメントの更新履歴

| 日付 | 変更内容 |
|------|---------|
| 2025-01-27 | 初版作成 |
| 2025-01-27 | ドキュメント構造を再編成・分割 |

---

## 関連リンク

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Google AI Studio (Gemini API)](https://makersuite.google.com/app/apikey)
- [Obsidian公式サイト](https://obsidian.md/)
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
