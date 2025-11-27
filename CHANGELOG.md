# Changelog

All notable changes to this project will be documented in this file.

## [Phase 1] - 2025-11-27

### 🎉 Phase 1 完了：記録の構造化

#### Added
- **Discord Bot による音声メッセージ受信機能**
  - スマホから音声メッセージを送信
  - 自動ダウンロードと処理
  - リアルタイムステータス表示

- **Gemini 2.5 Flash による AI 処理**
  - 音声の文字起こし
  - 構造化データ抽出（成功/失敗/次回アクション）
  - 身体感覚（Somatic Marker）の特定
  - ソクラテス式フォローアップ質問生成

- **Obsidian 形式 Markdown 生成**
  - YAML フロントマター
  - Callout 形式（Success, Warning, Next Action）
  - 年月別ディレクトリ構造

- **GitHub 自動同期**
  - Markdown の自動 Push
  - ファイル作成・更新の自動判定
  - リポジトリ: ishidafuu/isdf_tennis_vault

- **ドキュメント**
  - セットアップガイド（SETUP.md）
  - Discord Bot セットアップガイド（docs/DISCORD_SETUP.md）
  - 環境チェックスクリプト（check_setup.py）
  - モデル確認スクリプト（check_models.py）
  - Phase 1 完了報告（docs/PHASE1_COMPLETION.md）
  - Phase 2 実装計画（docs/PHASE2_PLAN.md）

#### Fixed
- **Gemini モデル名の更新**
  - gemini-1.5-flash → gemini-2.5-flash
  - 404 エラーの解決

- **Pydantic バリデーションエラーの修正**
  - PracticeSession.condition を Optional[str] に変更
  - null 値のデフォルト処理を追加
  - プロンプト改善で null 値を防止

#### Technical Details
- Python 3.12
- discord.py 2.3.0+
- google-generativeai 0.3.0+
- PyGithub 2.1.1+
- Pydantic 2.0.0+

#### Commits
- c4cc2ca: feat: Initialize project structure and setup documentation
- 5d7e1c2: feat: Implement Phase 1 - Voice to Obsidian pipeline
- d7ed702: docs: Add Discord Bot setup guide and environment checker
- 63f31f5: fix: Update Gemini model name to gemini-1.5-flash-latest
- 8c44ba5: fix: Update to Gemini 2.0 Flash experimental model
- 30f9fb4: fix: Correct model name to gemini-2.5-flash
- 846be78: fix: Handle null values in Gemini API responses

---

## [Upcoming] - Phase 2

### 🔜 Phase 2: 継続性の担保

#### Planned Features
- `/start` コマンド - 前回の課題をリマインド
- `/finish` コマンド - セッション終了と振り返り
- スレッドベースのセッション管理
- 前回ログの読み込み機能

詳細は `docs/PHASE2_PLAN.md` を参照。

---

## Version History

- **Phase 1 (2025-11-27)**: 記録の構造化 ✅ 完了
- **Phase 2 (Planned)**: 継続性の担保
- **Phase 3 (Future)**: 対話の深化
- **Phase 4 (Future)**: 資産の活用（ベクトル検索）
