# 実装仕様: まとめページ生成（AI完全生成方式）

**作成日**: 2025-12-08
**採用方式**: 案A - 完全AI生成
**関連ドキュメント**: `docs/改修/ヒアリング結果_まとめページ機能.md`

---

## 📌 概要

すべてのまとめページ（6種類）を**Gemini APIによる完全AI生成**で実装する。

### 採用理由
- ✅ 自然な日本語、具体的なアドバイス
- ✅ トレンド分析が高度（「継続しましょう」「改善すべき」を明示）
- ✅ コンテキストを考慮した優先順位付け
- ✅ コスト: 約0.04円/月（ほぼ無料）

---

## 🎯 生成するファイル（6種類）

### 1. まとめ_総合.md
- **目的**: 練習前チェック用（最重要）
- **更新頻度**: 練習日の翌日
- **内容**: 未解決の反省点、最近の気づき、トレンド分析

### 2. まとめ_最近.md
- **目的**: 直近2週間の詳細
- **更新頻度**: 練習日の翌日
- **内容**: 時系列での気づき・反省、技術別の集計

### 3. まとめ_1ヶ月.md
- **目的**: 過去1ヶ月の詳細
- **更新頻度**: 練習日の翌日
- **内容**: 月間トレンド、技術別の進化

### 4. まとめ_フォアハンド.md
- **目的**: フォアハンドの全記録
- **更新頻度**: 練習日の翌日
- **内容**: ショット種別ごとの気づき・反省、統計

### 5. まとめ_バックハンド.md
- **目的**: バックハンドの全記録
- **更新頻度**: 練習日の翌日
- **内容**: ショット種別ごとの気づき・反省、統計

### 6. まとめ_サーブ.md
- **目的**: サーブの全記録
- **更新頻度**: 練習日の翌日
- **内容**: ショット種別ごとの気づき・反省、統計

---

## 🔧 技術実装

### アーキテクチャ

```
┌─────────────────────────────────────┐
│ スケジューラー                      │
│ （毎日深夜3時、前日にメモがあれば）│
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ SummaryGenerator                    │
│ まとめページ生成エンジン            │
└──────────────┬──────────────────────┘
               ↓
       ┌───────┴───────┐
       ↓               ↓
┌─────────────┐   ┌─────────────┐
│ データ収集  │   │ AI生成      │
│ (Python)    │   │ (Gemini API)│
└──────┬──────┘   └──────┬──────┘
       │                 │
       └────────┬────────┘
                ↓
┌─────────────────────────────────────┐
│ Markdownファイル生成                │
│ （6種類のまとめページ）             │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ GitHub push                         │
│ Obsidian Vaultに反映                │
└─────────────────────────────────────┘
```

---

## 📂 実装ファイル

### 1. データ収集モジュール

#### `src/storage/summary_generator.py`（新規作成）

```python
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json
import yaml

class SummaryGenerator:
    """まとめページ生成エンジン"""

    def __init__(self, obsidian_manager, gemini_client, github_sync):
        self.obsidian_manager = obsidian_manager
        self.gemini_client = gemini_client
        self.github_sync = github_sync
        self.vault_path = Path(obsidian_manager.vault_path)

    # ========================================
    # データ収集
    # ========================================

    def collect_memos_for_summary(self, period: str = "all", technique: Optional[str] = None) -> dict:
        """
        まとめ用のメモデータを収集

        Args:
            period: "recent"（2週間）/ "month"（1ヶ月）/ "all"（全期間）
            technique: 技術名でフィルタ（None=全技術）

        Returns:
            {
                'memos': [...],  # メモの生データ
                'insights': [...],  # 気づきリスト
                'reflections': [...],  # 反省点リスト（未解決のみ）
                'tags': {...},  # タグ別の集計
                'date_range': {...}  # 期間情報
            }
        """

        # 1. 期間を計算
        if period == "recent":
            start_date = datetime.now() - timedelta(days=14)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = None  # 全期間

        # 2. メモを取得
        if technique:
            # 技術別フィルタ
            memos = self.obsidian_manager.search_by_tags([technique])
        else:
            # 全メモ
            memos = self.obsidian_manager.get_all_memos()

        # 期間でフィルタ
        if start_date:
            memos = [m for m in memos if self._parse_date(m) >= start_date]

        # 3. データを抽出
        insights = []
        reflections = []
        tag_counts = {}

        for memo_path in memos:
            memo_data = self._extract_memo_data(memo_path)

            insights.extend(memo_data['insights'])
            reflections.extend([r for r in memo_data['reflections'] if r['status'] == 'unresolved'])

            for tag in memo_data['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            'memos': memos,
            'insights': insights,
            'reflections': reflections,
            'tags': tag_counts,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d') if start_date else '全期間',
                'end': datetime.now().strftime('%Y-%m-%d')
            }
        }

    def _extract_memo_data(self, memo_path: str) -> dict:
        """メモファイルからデータを抽出"""

        with open(memo_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # YAML frontmatter
        metadata = self._parse_frontmatter(content)

        # Markdown本文
        markdown_content = self._parse_markdown_sections(content)

        return {
            'date': metadata.get('date'),
            'scene': metadata.get('scene'),
            'tags': metadata.get('tags', []),
            'insights': markdown_content.get('insights', []),
            'reflections': markdown_content.get('reflections', []),
            'deepening': markdown_content.get('deepening', {})
        }

    def _parse_frontmatter(self, content: str) -> dict:
        """YAML frontmatterをパース"""

        if not content.startswith('---'):
            return {}

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}

        return yaml.safe_load(parts[1])

    def _parse_markdown_sections(self, content: str) -> dict:
        """Markdownセクションをパース"""

        # "## 気づき" セクションを抽出
        insights = self._extract_section(content, '## 気づき')

        # "## 反省点" セクションを抽出
        reflections = self._extract_section(content, '## 反省点')

        # "### 深堀り情報" セクションを抽出
        deepening = self._extract_section(content, '### 深堀り情報')

        return {
            'insights': self._parse_list_items(insights),
            'reflections': self._parse_reflections(reflections),
            'deepening': self._parse_deepening(deepening)
        }

    def _extract_section(self, content: str, section_name: str) -> str:
        """特定のセクションを抽出"""

        if section_name not in content:
            return ""

        start = content.index(section_name)
        # 次のセクション（##）までを取得
        next_section = content.find('\n##', start + len(section_name))

        if next_section == -1:
            return content[start:]
        else:
            return content[start:next_section]

    def _parse_list_items(self, section: str) -> List[str]:
        """リストアイテムをパース"""

        lines = section.split('\n')
        items = []

        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:])

        return items

    def _parse_reflections(self, section: str) -> List[dict]:
        """反省点をパース"""

        items = self._parse_list_items(section)
        reflections = []

        for item in items:
            # "[ ]" = unresolved, "[x]" = resolved
            if item.startswith('[ ]'):
                status = 'unresolved'
                content = item[4:]
            elif item.startswith('[x]'):
                status = 'resolved'
                content = item[4:]
            else:
                status = 'unresolved'
                content = item

            reflections.append({
                'content': content,
                'status': status
            })

        return reflections

    def _parse_deepening(self, section: str) -> dict:
        """深堀り情報をパース"""

        deepening = {}

        # "**対比**:", "**変化**:" などを抽出
        patterns = ['対比', '変化', '根拠', '具体化']

        for pattern in patterns:
            marker = f"**{pattern}**:"
            if marker in section:
                start = section.index(marker) + len(marker)
                # 次のパターンまたは行末まで
                end = len(section)
                for other_pattern in patterns:
                    other_marker = f"**{other_pattern}**:"
                    if other_marker in section[start:]:
                        end = min(end, start + section[start:].index(other_marker))

                deepening[pattern] = section[start:end].strip()

        return deepening

    def _parse_date(self, memo_path: str) -> datetime:
        """メモファイルから日付を取得"""

        with open(memo_path, 'r', encoding='utf-8') as f:
            metadata = self._parse_frontmatter(f.read())

        date_str = metadata.get('date')
        if date_str:
            return datetime.strptime(date_str, '%Y-%m-%d')
        else:
            # ファイル名から抽出（YYYY-MM-DD-HHMMSS形式）
            filename = Path(memo_path).stem
            date_part = filename.split('-')[:3]
            return datetime.strptime('-'.join(date_part), '%Y-%m-%d')

    # ========================================
    # トレンド分析
    # ========================================

    def _analyze_trends(self, insights: List[str], reflections: List[dict]) -> dict:
        """
        トレンドを分析

        Returns:
            {
                'keywords': {...},  # 頻出キーワード
                'patterns': [...]  # パターン（例: 「早めの準備」が3回）
            }
        """

        # 簡易的なキーワード抽出（助詞で分割）
        all_text = ' '.join(insights + [r['content'] for r in reflections])
        words = self._extract_keywords(all_text)

        # 頻出キーワード
        keyword_counts = {}
        for word in words:
            if len(word) >= 2:  # 2文字以上
                keyword_counts[word] = keyword_counts.get(word, 0) + 1

        # 頻度順にソート
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            'keywords': dict(sorted_keywords[:10]),  # 上位10件
            'patterns': [f"「{k}」が{v}回" for k, v in sorted_keywords[:5]]
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """簡易的なキーワード抽出"""

        # 助詞で分割
        particles = ['は', 'が', 'を', 'に', 'へ', 'と', 'から', 'まで', 'より', 'で', 'の']

        for particle in particles:
            text = text.replace(particle, ' ')

        # 記号を除去
        symbols = ['、', '。', '！', '？', '（', '）', '「', '」']
        for symbol in symbols:
            text = text.replace(symbol, ' ')

        # 分割
        words = text.split()
        return [w.strip() for w in words if w.strip()]
```

---

### 2. AI生成モジュール

#### `src/ai/summary_prompts.py`（新規作成）

```python
from datetime import datetime

class SummaryPrompts:
    """まとめ生成用のプロンプト"""

    @staticmethod
    def generate_overview_prompt(data: dict) -> str:
        """まとめ_総合.md 生成用プロンプト"""

        today = datetime.now().strftime('%Y-%m-%d')

        return f"""
あなたはテニスコーチのアシスタントです。
以下のテニス練習データから、練習前チェック用のまとめを生成してください。

# データ

## 未解決の反省点
{SummaryPrompts._format_reflections(data['reflections'])}

## 最近の気づき（直近10件）
{SummaryPrompts._format_insights(data['insights'][:10])}

## タグ別集計
{SummaryPrompts._format_tags(data['tags'])}

## トレンド情報
{SummaryPrompts._format_trends(data.get('trends', {}))}

# タスク

練習前に見て、今日の練習で意識すべきポイントが明確になるまとめを作成してください。

# 出力形式

以下のMarkdown形式で出力してください：

```markdown
# テニス練習まとめ（総合）

最終更新: {today}

---

## 🚨 練習前チェック

### 今日意識すること（未解決の反省点）

未解決の反省点を優先度順に3-5件表示してください。
- 繰り返し発生している反省点を上位に
- それぞれに具体的な対策を添えてください

フォーマット:
- [ ] [技術名]: [反省内容] → [具体的な対策]
  [補足説明（あれば）]

### 最近うまくいっていること

直近2週間で成功した気づきを3-5件表示してください。
- モチベーションが上がるような表現で

フォーマット:
- ✅ [技術名]・[ショット種別]: [気づき]
  [励ましの言葉（「この調子で！」など）]

---

## 📊 最近のトレンド（過去2週間）

### 頻出キーワード

トレンド情報から、以下を分析してください:
- 頻出キーワード上位3つ
- それぞれに対して「継続すべき」または「改善すべき」のアドバイス

フォーマット:
- 「[キーワード]」が[回数]回 → [解釈とアドバイス]

例:
- 「早めの準備」が3回 → 意識できている証拠です！継続しましょう。
- 「力みすぎ」の反省が2回 → 今週はリラックスを重点的に。
  具体的には、グリップを緩く持つことから始めてみてください。

### 技術別の気づき頻度

タグ別集計から、上位5つを表示してください。

フォーマット:
- [技術名]: [件数]

---

## 📚 詳細まとめへのリンク

### 期間別
- [[まとめ_最近]] - 直近2週間の詳細
- [[まとめ_1ヶ月]] - 過去1ヶ月の詳細

### 技術別
- [[まとめ_フォアハンド]] - フォアハンド全記録
- [[まとめ_バックハンド]] - バックハンド全記録
- [[まとめ_サーブ]] - サーブ全記録
```

# 注意事項

1. **自然な日本語**: 機械的にならず、コーチが話すような温かみのある表現
2. **具体的なアドバイス**: 「意識しましょう」だけでなく、「どうすれば良いか」を明示
3. **モチベーション**: 成功体験を強調し、前向きな気持ちになれるように
4. **優先順位**: 重要度・緊急度の高いものを上位に
5. **読みやすさ**: 箇条書き、絵文字を活用

それでは、まとめを生成してください。
"""

    @staticmethod
    def generate_technique_prompt(technique: str, data: dict) -> str:
        """技術別まとめ生成用プロンプト"""

        today = datetime.now().strftime('%Y-%m-%d')

        return f"""
あなたはテニスコーチのアシスタントです。
以下の{technique}に関するデータから、技術別まとめを生成してください。

# データ

## 気づき（全期間）
{SummaryPrompts._format_insights(data['insights'])}

## 反省点（未解決）
{SummaryPrompts._format_reflections(data['reflections'])}

## ショット種別の集計
{SummaryPrompts._format_shot_types(data.get('shot_types', {}))}

# タスク

{technique}の全記録を、ショット種別ごとに整理してまとめてください。

# 出力形式

```markdown
# {technique}まとめ

最終更新: {today}

---

## 🎾 強打（ドライブ）

### 気づき

強打に関する気づきを時系列で表示してください。
- 深堀り情報（対比、根拠など）も含めて

フォーマット:
- **[気づきの要約]**（[日付]）
  - 💡 対比: [対比情報]
  - 💡 根拠: [根拠情報]

### 反省点

未解決の反省点を表示してください。
- 繰り返し発生している場合は日付を複数表示

フォーマット:
- [ ] [反省内容]（[日付]、[日付]）
  - 原因: [推測される原因]
  - 対策: [試すべき対策]

---

## 🎾 丁寧（コントロール重視）

（同様の構造）

---

## 🎾 スライス

（同様の構造）

---

## 📊 統計

- 強打の気づき: [件数]
- 丁寧打ちの気づき: [件数]
- スライスの気づき: [件数]
- 未解決の反省点: [件数]

---

## 💡 {technique}の全体的な傾向

データから読み取れる{technique}の傾向を2-3文で要約してください。
```

# 注意事項

1. **時系列**: 気づきは日付順に並べる
2. **深堀り情報**: 対比、根拠などがあれば必ず含める
3. **反省点の追跡**: 同じ内容の反省が複数回出ている場合は明示
4. **統計**: 数値で振り返りができるように

それでは、まとめを生成してください。
"""

    @staticmethod
    def generate_period_prompt(period: str, data: dict) -> str:
        """期間別まとめ生成用プロンプト"""

        today = datetime.now().strftime('%Y-%m-%d')
        period_label = "直近2週間" if period == "recent" else "過去1ヶ月"

        return f"""
あなたはテニスコーチのアシスタントです。
以下の{period_label}のテニス練習データから、期間別まとめを生成してください。

# データ

## この期間の気づき
{SummaryPrompts._format_insights(data['insights'])}

## この期間の反省点
{SummaryPrompts._format_reflections(data['reflections'])}

## 期間情報
- 開始日: {data['date_range']['start']}
- 終了日: {data['date_range']['end']}

# タスク

{period_label}の練習内容を時系列で振り返り、成長を実感できるまとめを作成してください。

# 出力形式

```markdown
# {period_label}のまとめ

期間: {data['date_range']['start']} 〜 {data['date_range']['end']}
最終更新: {today}

---

## 📅 時系列での振り返り

この期間の気づき・反省を日付順に表示してください。

フォーマット:
### [日付]

#### 気づき
- [気づき内容]

#### 反省点
- [反省内容]

---

## 📈 この期間の成長

この期間で成長したポイントを2-3個挙げてください。
- 具体的なエピソードを交えて

---

## 🔄 次の期間に向けて

未解決の反省点を踏まえて、次の期間で意識すべきポイントを提案してください。
```

# 注意事項

1. **成長の可視化**: ポジティブな変化を強調
2. **時系列**: 日付順に整理
3. **次へのつながり**: 未来に向けたアドバイス

それでは、まとめを生成してください。
"""

    # ========================================
    # ヘルパー関数
    # ========================================

    @staticmethod
    def _format_reflections(reflections: list) -> str:
        """反省点をJSON形式で整形"""
        return json.dumps(reflections, ensure_ascii=False, indent=2)

    @staticmethod
    def _format_insights(insights: list) -> str:
        """気づきをJSON形式で整形"""
        return json.dumps(insights, ensure_ascii=False, indent=2)

    @staticmethod
    def _format_tags(tags: dict) -> str:
        """タグをJSON形式で整形"""
        return json.dumps(tags, ensure_ascii=False, indent=2)

    @staticmethod
    def _format_trends(trends: dict) -> str:
        """トレンドをJSON形式で整形"""
        return json.dumps(trends, ensure_ascii=False, indent=2)

    @staticmethod
    def _format_shot_types(shot_types: dict) -> str:
        """ショット種別をJSON形式で整形"""
        return json.dumps(shot_types, ensure_ascii=False, indent=2)
```

---

### 3. 生成実行モジュール

#### `src/storage/summary_generator.py`（続き）

```python
    # ========================================
    # まとめ生成（AI）
    # ========================================

    async def generate_all_summaries(self):
        """全まとめページを生成"""

        print("まとめページ生成開始...")

        # 1. まとめ_総合.md
        await self.generate_summary_overview()

        # 2. まとめ_最近.md
        await self.generate_summary_period("recent")

        # 3. まとめ_1ヶ月.md
        await self.generate_summary_period("month")

        # 4. まとめ_フォアハンド.md
        await self.generate_summary_technique("フォアハンド")

        # 5. まとめ_バックハンド.md
        await self.generate_summary_technique("バックハンド")

        # 6. まとめ_サーブ.md
        await self.generate_summary_technique("サーブ")

        # GitHub push
        self.github_sync.push_to_github()

        print("まとめページ生成完了！")

    async def generate_summary_overview(self):
        """まとめ_総合.md を生成"""

        print("  - まとめ_総合.md 生成中...")

        # データ収集
        data = self.collect_memos_for_summary(period="all")

        # トレンド分析
        data['trends'] = self._analyze_trends(data['insights'], data['reflections'])

        # プロンプト生成
        from src.ai.summary_prompts import SummaryPrompts
        prompt = SummaryPrompts.generate_overview_prompt(data)

        # Gemini API
        response = await self.gemini_client.generate_content(prompt)

        # Markdownとして保存
        output_path = self.vault_path / "まとめ_総合.md"
        self._save_markdown(output_path, response.text)

        print("    完了！")

    async def generate_summary_period(self, period: str):
        """期間別まとめを生成"""

        period_label = "最近" if period == "recent" else "1ヶ月"
        print(f"  - まとめ_{period_label}.md 生成中...")

        # データ収集
        data = self.collect_memos_for_summary(period=period)

        # プロンプト生成
        from src.ai.summary_prompts import SummaryPrompts
        prompt = SummaryPrompts.generate_period_prompt(period, data)

        # Gemini API
        response = await self.gemini_client.generate_content(prompt)

        # Markdownとして保存
        output_path = self.vault_path / f"まとめ_{period_label}.md"
        self._save_markdown(output_path, response.text)

        print("    完了！")

    async def generate_summary_technique(self, technique: str):
        """技術別まとめを生成"""

        print(f"  - まとめ_{technique}.md 生成中...")

        # データ収集
        data = self.collect_memos_for_summary(period="all", technique=technique)

        # ショット種別ごとに分類
        data['shot_types'] = self._categorize_by_shot_type(data['insights'], data['reflections'])

        # プロンプト生成
        from src.ai.summary_prompts import SummaryPrompts
        prompt = SummaryPrompts.generate_technique_prompt(technique, data)

        # Gemini API
        response = await self.gemini_client.generate_content(prompt)

        # Markdownとして保存
        output_path = self.vault_path / f"まとめ_{technique}.md"
        self._save_markdown(output_path, response.text)

        print("    完了！")

    def _categorize_by_shot_type(self, insights: list, reflections: list) -> dict:
        """ショット種別ごとに分類"""

        shot_types = {
            '強打': {'insights': [], 'reflections': []},
            '丁寧': {'insights': [], 'reflections': []},
            'スライス': {'insights': [], 'reflections': []},
            'スピン': {'insights': [], 'reflections': []}
        }

        # 簡易的な分類（キーワードベース）
        for insight in insights:
            for shot_type in shot_types.keys():
                if shot_type in insight:
                    shot_types[shot_type]['insights'].append(insight)
                    break

        for reflection in reflections:
            for shot_type in shot_types.keys():
                if shot_type in reflection['content']:
                    shot_types[shot_type]['reflections'].append(reflection)
                    break

        return shot_types

    def _save_markdown(self, path: Path, content: str):
        """Markdownファイルとして保存"""

        # コードブロックを除去（Geminiが```markdownで囲む場合がある）
        content = content.replace('```markdown', '').replace('```', '')

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
```

---

### 4. スケジューラー統合

#### `src/scheduler/scheduler_manager.py`（更新）

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class SchedulerManager:
    """スケジューラー管理"""

    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """スケジューラー開始"""

        # ... 既存のジョブ ...

        # 【新規】まとめページ更新チェック（毎日深夜3時）
        self.scheduler.add_job(
            self.check_and_generate_summaries,
            trigger='cron',
            hour=3,
            minute=0,
            id='summary_generation'
        )

        self.scheduler.start()

    async def check_and_generate_summaries(self):
        """まとめページ更新チェック"""

        # 前日にメモが追加されたかチェック
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        # 前日のメモを検索
        memos = self.bot.obsidian_manager.search_by_date(yesterday_str)

        if len(memos) > 0:
            print(f"前日（{yesterday_str}）にメモが{len(memos)}件追加されました。まとめページを更新します。")

            # まとめページ生成
            summary_generator = SummaryGenerator(
                self.bot.obsidian_manager,
                self.bot.gemini_client,
                self.bot.github_sync
            )

            await summary_generator.generate_all_summaries()
        else:
            print(f"前日（{yesterday_str}）にメモの追加なし。まとめページ更新をスキップ。")
```

---

## 📊 コスト試算

### Gemini API 使用量

| まとめページ | 入力トークン | 出力トークン | コスト/回 |
|------------|------------|------------|----------|
| 総合 | 約5,000 | 約1,500 | 約0.01円 |
| 最近 | 約3,000 | 約1,000 | 約0.006円 |
| 1ヶ月 | 約4,000 | 約1,200 | 約0.008円 |
| フォアハンド | 約2,000 | 約800 | 約0.004円 |
| バックハンド | 約2,000 | 約800 | 約0.004円 |
| サーブ | 約2,000 | 約800 | 約0.004円 |
| **合計** | **約18,000** | **約6,100** | **約0.036円/回** |

### 月間コスト

- 更新頻度: 週2回（金曜・土曜に練習）
- 月間: 約8回
- **月間コスト: 約0.29円**

**結論: ほぼ無料（1円以下）**

---

## 🧪 テストシナリオ

### 1. 正常系: まとめページ生成

```
【前提】
- 前日（12/7）にメモが2件追加されている

【実行】
深夜3時にスケジューラーが起動

【期待される動作】
1. 前日のメモを検出
2. 6種類のまとめページを生成
3. Obsidian Vaultに保存
4. GitHub push
5. ログ出力: "まとめページ生成完了！"
```

### 2. 正常系: 生成内容の確認

```
【入力データ】
- 反省点: 「フォアハンドの振り遅れ」（12/1、12/6に発生）
- 気づき: 「早めの準備を意識すると良い」（12/7）

【期待される出力（まとめ_総合.md）】
## 🚨 練習前チェック

### 今日意識すること
- [ ] フォアハンド: 振り遅れ → 早めの準備を徹底
  前回（12/6）と前々回（12/1）に発生しています。
  テイクバックのタイミングを意識してみてください。

### 最近うまくいっていること
- ✅ フォアハンド: 早めの準備を意識
  この調子で継続しましょう！
```

### 3. 異常系: 前日にメモなし

```
【前提】
- 前日（12/7）にメモが0件

【実行】
深夜3時にスケジューラーが起動

【期待される動作】
1. 前日のメモを検索 → 0件
2. まとめページ生成をスキップ
3. ログ出力: "前日にメモの追加なし。まとめページ更新をスキップ。"
```

---

## 🚀 実装順序

### Phase 1: データ収集（2-3時間）
1. ✅ `summary_generator.py` - データ収集機能
2. ✅ メモのパース（YAML、Markdown）
3. ✅ トレンド分析

### Phase 2: プロンプト設計（2-3時間）
1. ✅ `summary_prompts.py` - プロンプトテンプレート
2. ✅ 総合まとめ用プロンプト
3. ✅ 技術別まとめ用プロンプト
4. ✅ 期間別まとめ用プロンプト

### Phase 3: AI生成（1-2時間）
1. ✅ Gemini API統合
2. ✅ 6種類のまとめ生成関数
3. ✅ Markdown保存

### Phase 4: スケジューラー統合（1時間）
1. ✅ `scheduler_manager.py` 更新
2. ✅ 前日のメモチェック
3. ✅ 自動生成ジョブ

### Phase 5: テスト（2-3時間）
1. ✅ ユニットテスト
2. ✅ 実環境での動作確認
3. ✅ 生成内容のレビュー

**合計: 8-12時間**

---

## 📝 次のステップ

1. **実装開始**: Phase 1からスタート
2. **フィードバック**: 生成されたまとめページをレビュー
3. **調整**: プロンプトの改善、フォーマット調整
4. **Discord連携**: 練習前リマインド、コツ投稿の実装

---

**最終更新**: 2025-12-08
**次回レビュー**: Phase 1実装後
