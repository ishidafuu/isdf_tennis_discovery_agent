# 🎾 Tennis Discovery Agent

**自律的な上達を支援する「第2の脳」**

## 🎯 プロジェクトの目的

単なる練習記録の保存ではなく、「仮説・実行・検証」のサイクルを回し、ユーザーの自律的な上達を支援する。特に「身体感覚（Somatic Marker）」の言語化と蓄積に重点を置き、スランプやイップス時の回復の拠り所となる「第2の脳」を構築する。

## 💡 コア・フィロソフィー

- **No Teaching, But Coaching**: 答えを教えるのではなく、問いかけによってユーザー自身の気づきを引き出す（ソクラテス式問答）
- **Voice First**: 練習現場でのUXを最優先し、手入力ではなく「会話（音声）」を中心にする
- **Cycle Oriented**: 前回の課題を今回のテーマにし、今回の発見を次回へつなげる「線」の管理を行う

## 🚀 クイックスタート

### 1. セットアップ

詳細な手順は **[SETUP.md](./SETUP.md)** を参照してください。

```bash
# リポジトリをクローン（既に完了している場合はスキップ）
git clone https://github.com/ishidafuu/isdf_tennis_discovery_agent.git
cd isdf_tennis_discovery_agent

# 環境変数の設定
cp .env.example .env
# .env ファイルを編集して、APIキーを設定

# 依存パッケージのインストール
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 実行（Phase 1実装後）

```bash
python main.py
```

## 📁 プロジェクト構成

```
isdf_tennis_discovery_agent/
├── src/
│   ├── bot/          # Discordボット
│   ├── ai/           # Gemini AI処理
│   ├── storage/      # Markdown生成・GitHub連携
│   └── models/       # データモデル
├── config/           # 設定ファイル
├── tests/            # テストコード
├── .env.example      # 環境変数テンプレート
├── requirements.txt  # 依存パッケージ
├── SETUP.md          # セットアップガイド
└── main.py           # エントリーポイント（Phase 1で作成）
```

## 📋 開発ロードマップ

### Phase 1: 記録の構造化 ✅ **準備中**
- 音声入力 → Gemini文字起こし → Obsidian形式保存
- まずは「喋るだけで綺麗なノートができる」体験を作る

### Phase 2: 継続性の担保
- 前回ログの読み込み
- 練習開始時のリマインド機能

### Phase 3: 対話の深化
- ソクラテス式問答の精度向上

### Phase 4: 資産の活用
- ベクトル検索による「感覚検索」機能

## 🛡️ セキュリティ

- `.env`ファイルは**絶対にGitにコミットしない**
- APIキーは`.env`ファイルにのみ保存
- プライベートリポジトリで管理

## 📄 ライセンス

MIT License

---

**⚠️ 注意**: 現在Phase 1の準備段階です。実装はこれから開始します。
