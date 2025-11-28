---
description: 次の未完了タスクを取得して実装を開始
---

# /start - 作業開始コマンド

このコマンドは、次に取り組むべきタスクを自動的に特定し、実装を開始します。

## 実行手順

1. **`docs/plan.md` を読み込む**
   - Phase 1-4の全タスクリストを確認
   - 最初の未完了タスク（`- [ ]`）を特定

2. **`docs/session-log.md` で前回の状態を確認**
   - 最新のセッションログを確認
   - 「次回の作業」「備考」から継続ポイントを把握
   - 中断タスクがあれば優先的に取り組む

3. **関連ファイルを分析**
   - 次のタスクに関連するファイルを読み込み
   - 既存の実装を理解してから着手

4. **実装を開始**
   - 1つのタスクに集中する
   - コーディング規約に従う（CLAUDE.mdを参照）
   - 型ヒント、エラーハンドリング、ログ出力を忘れずに

## 重要な注意事項

- **1タスクに集中**: 複数タスクを同時に進めない
- **完了時は自動記録**: CLAUDE.mdの「自律行動ルール」に従い、完了時に以下を自動実行:
  - `docs/plan.md` の該当タスクを `[x]` に更新
  - `docs/session-log.md` に追記（日時、タスク名、変更ファイル、次回の作業）
  - 重要な設計判断があれば CLAUDE.md の「最近の変更」に追記
  - 完了報告と「/clear → /start で次へ」を提案

## タスク優先順位（Phase 1）

次に取り組むべきタスクの優先順位（`docs/plan.md` より）:

### 🔴 高優先度（Phase 1完了に必須）
1. **Discord DM処理の実装** `docs/improvements/phases/01-foundation/input.md:362-421`
2. **Phase 1統合テスト** `tests/integration/test_phase1.py`

### 🟡 中優先度（Phase 1オプション）
3. **週次レビュー自動生成** `src/scheduler/weekly_review.py`

### 🟢 低優先度（Phase 2以降でも可）
4. **練習開始時リマインド機能** `src/scheduler/reminders.py`

## 使用例

```
あなた: /start

Claude:
[docs/plan.md と docs/session-log.md を読み込み]
[次のタスクを特定: Discord DM処理の実装]
[関連ファイルを分析: src/bot/client.py、docs/improvements/phases/01-foundation/input.md]
[実装を開始...]
```

---

**このコマンドを使うことで、/clearの後でもシームレスに作業を再開できます。**
