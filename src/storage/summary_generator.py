"""
Summary Generator for Tennis Discovery Agent

Generates summary pages from practice memos using Gemini AI.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import yaml
import re
from collections import Counter

from src.models.scene_data import SearchFilters


class SummaryGenerator:
    """まとめページ生成エンジン"""

    def __init__(self, obsidian_manager, gemini_client, github_sync):
        """
        Initialize SummaryGenerator.

        Args:
            obsidian_manager: ObsidianManager instance
            gemini_client: GeminiClient instance
            github_sync: GitHubSync instance
        """
        self.obsidian_manager = obsidian_manager
        self.gemini_client = gemini_client
        self.github_sync = github_sync
        self.vault_path = Path(obsidian_manager.vault_path)

    # ========================================
    # Public Methods
    # ========================================

    async def generate_all_summaries(self) -> bool:
        """
        Generate all 6 summary pages.

        Returns:
            True if successful, False otherwise
        """
        try:
            print("📊 まとめページ生成を開始します...")

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

            print("✅ まとめページ生成完了！")
            return True

        except Exception as e:
            print(f"❌ まとめページ生成エラー: {e}")
            return False

    async def generate_summary_overview(self) -> None:
        """Generate まとめ_総合.md"""
        from src.ai.summary_prompts import SummaryPrompts

        print("  → まとめ_総合.md 生成中...")

        # データ収集
        data = self.collect_memos_for_summary(period="recent")

        # AI生成プロンプト
        prompt = SummaryPrompts.generate_overview_prompt(data)

        # Gemini APIで生成
        markdown_content = await self._generate_with_gemini(prompt)

        # ファイル保存
        output_path = self.vault_path / "まとめ_総合.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print("  ✅ まとめ_総合.md 完成")

    async def generate_summary_period(self, period: str) -> None:
        """
        Generate period-based summary.

        Args:
            period: "recent" or "month"
        """
        from src.ai.summary_prompts import SummaryPrompts

        filename = "まとめ_最近.md" if period == "recent" else "まとめ_1ヶ月.md"
        print(f"  → {filename} 生成中...")

        # データ収集
        data = self.collect_memos_for_summary(period=period)

        # AI生成プロンプト
        prompt = SummaryPrompts.generate_period_prompt(data, period)

        # Gemini APIで生成
        markdown_content = await self._generate_with_gemini(prompt)

        # ファイル保存
        output_path = self.vault_path / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"  ✅ {filename} 完成")

    async def generate_summary_technique(self, technique: str) -> None:
        """
        Generate technique-based summary.

        Args:
            technique: "フォアハンド", "バックハンド", "サーブ"
        """
        from src.ai.summary_prompts import SummaryPrompts

        filename = f"まとめ_{technique}.md"
        print(f"  → {filename} 生成中...")

        # データ収集
        data = self.collect_memos_for_summary(period="all", technique=technique)

        # AI生成プロンプト
        prompt = SummaryPrompts.generate_technique_prompt(data, technique)

        # Gemini APIで生成
        markdown_content = await self._generate_with_gemini(prompt)

        # ファイル保存
        output_path = self.vault_path / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"  ✅ {filename} 完成")

    # ========================================
    # Data Collection
    # ========================================

    def collect_memos_for_summary(
        self,
        period: str = "all",
        technique: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect memo data for summary generation.

        Args:
            period: "recent" (2 weeks), "month" (1 month), "all"
            technique: Technique name filter (None = all techniques)

        Returns:
            {
                'memos': [...],          # Raw memo data
                'insights': [...],       # Insight list
                'reflections': [...],    # Reflection list (unresolved only)
                'tags': {...},           # Tag counts
                'date_range': {...},     # Period info
                'trends': {...}          # Trend analysis
            }
        """
        # 1. Calculate period
        if period == "recent":
            start_date = datetime.now() - timedelta(days=14)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = None  # All period

        # 2. Get memos
        if technique:
            # Filter by technique tag
            memos = self.obsidian_manager.search(
                filters=SearchFilters(tags=[technique]),
                limit=None
            )
        else:
            # All memos
            memos = self.obsidian_manager._get_all_memos(force_refresh=True)

        # Filter by date
        if start_date:
            memos = [m for m in memos if self._parse_memo_date(m) >= start_date]

        # 3. Extract data
        insights = []
        reflections = []
        tag_counts = {}

        for memo in memos:
            memo_data = self._extract_memo_data_from_dict(memo)

            insights.extend(memo_data['insights'])

            # Only include unresolved reflections
            unresolved = [r for r in memo_data['reflections'] if r['status'] == 'unresolved']
            reflections.extend(unresolved)

            for tag in memo_data['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 4. Analyze trends
        trends = self._analyze_trends(memos, period)

        return {
            'memos': memos,
            'insights': insights,
            'reflections': reflections,
            'tags': tag_counts,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d') if start_date else '全期間',
                'end': datetime.now().strftime('%Y-%m-%d')
            },
            'trends': trends
        }

    def _extract_memo_data_from_dict(self, memo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from memo dictionary.

        Args:
            memo: Memo dictionary from ObsidianManager

        Returns:
            Extracted memo data
        """
        # Parse Markdown sections
        content = memo.get('content', '')
        markdown_data = self._parse_markdown_sections(content)

        return {
            'date': memo.get('date'),
            'scene': memo.get('scene'),
            'tags': memo.get('tags', []),
            'insights': markdown_data.get('insights', []),
            'reflections': markdown_data.get('reflections', []),
            'deepening': markdown_data.get('deepening', {})
        }

    def _parse_memo_date(self, memo: Dict[str, Any]) -> datetime:
        """
        Parse date from memo.

        Args:
            memo: Memo dictionary

        Returns:
            Datetime object (or far past date if parsing fails)
        """
        date_str = memo.get('date')
        if not date_str:
            return datetime(1900, 1, 1)

        try:
            return datetime.fromisoformat(date_str)
        except:
            return datetime(1900, 1, 1)

    # ========================================
    # Markdown Parsing
    # ========================================

    def _parse_markdown_sections(self, content: str) -> Dict[str, Any]:
        """
        Parse Markdown sections.

        Args:
            content: Markdown content

        Returns:
            Parsed sections data
        """
        # Extract "## 気づき" section
        insights_section = self._extract_section(content, '## 気づき')

        # Extract "## 反省点" section
        reflections_section = self._extract_section(content, '## 反省点')

        # Extract "### 深堀り情報" section
        deepening_section = self._extract_section(content, '### 深堀り情報')

        return {
            'insights': self._parse_list_items(insights_section),
            'reflections': self._parse_reflections(reflections_section),
            'deepening': self._parse_deepening(deepening_section)
        }

    def _extract_section(self, content: str, section_name: str) -> str:
        """
        Extract specific section from Markdown.

        Args:
            content: Markdown content
            section_name: Section header (e.g., "## 気づき")

        Returns:
            Section content (empty string if not found)
        """
        if section_name not in content:
            return ""

        start = content.index(section_name)
        # Get until next section (##)
        next_section = content.find('\n##', start + len(section_name))

        if next_section == -1:
            return content[start:]
        else:
            return content[start:next_section]

    def _parse_list_items(self, section: str) -> List[str]:
        """
        Parse list items from section.

        Args:
            section: Markdown section

        Returns:
            List of items
        """
        lines = section.split('\n')
        items = []

        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())

        return items

    def _parse_reflections(self, section: str) -> List[Dict[str, str]]:
        """
        Parse reflections from section.

        Args:
            section: Markdown section

        Returns:
            List of reflection dictionaries
        """
        items = self._parse_list_items(section)
        reflections = []

        for item in items:
            # "[ ]" = unresolved, "[x]" = resolved
            if item.startswith('[ ]'):
                status = 'unresolved'
                content = item[4:].strip()
            elif item.startswith('[x]'):
                status = 'resolved'
                content = item[4:].strip()
            else:
                status = 'unresolved'
                content = item

            reflections.append({
                'content': content,
                'status': status
            })

        return reflections

    def _parse_deepening(self, section: str) -> Dict[str, str]:
        """
        Parse deepening information.

        Args:
            section: Markdown section

        Returns:
            Deepening data dictionary
        """
        deepening = {}

        # Extract "**対比**:", "**変化**:", etc.
        patterns = ['対比', '変化', '根拠', '具体化']

        for pattern in patterns:
            marker = f"**{pattern}**:"
            if marker in section:
                start = section.index(marker) + len(marker)
                # Until next pattern or end
                end = len(section)
                for other_pattern in patterns:
                    other_marker = f"**{other_pattern}**:"
                    if other_marker in section[start:]:
                        end = start + section[start:].index(other_marker)
                        break

                value = section[start:end].strip()
                deepening[pattern] = value

        return deepening

    # ========================================
    # Trend Analysis
    # ========================================

    def _analyze_trends(self, memos: List[Dict[str, Any]], period: str) -> Dict[str, Any]:
        """
        Analyze trends from memos.

        Args:
            memos: List of memo dictionaries
            period: Period type

        Returns:
            Trend analysis data
        """
        if not memos:
            return {
                'practice_frequency': "データなし",
                'most_common_tags': [],
                'keywords': {},
                'patterns': []
            }

        # Practice frequency
        practice_count = len(memos)
        days = 14 if period == "recent" else 30 if period == "month" else 365
        frequency = f"{practice_count}回 / {days}日"

        # Most common tags
        all_tags = []
        for memo in memos:
            all_tags.extend(memo.get('tags', []))

        tag_counter = Counter(all_tags)
        most_common_tags = tag_counter.most_common(5)

        # Keyword extraction
        all_text = []
        for memo in memos:
            content = memo.get('content', '')
            all_text.append(content)

        combined_text = ' '.join(all_text)
        keywords = self._extract_keywords_with_count(combined_text)

        return {
            'practice_frequency': frequency,
            'most_common_tags': most_common_tags,
            'keywords': keywords,
            'patterns': [f"「{k}」が{v}回" for k, v in keywords.items() if v > 2][:5]
        }

    def _extract_keywords_with_count(self, text: str) -> Dict[str, int]:
        """
        Extract keywords with count from text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary of keyword counts
        """
        # Split by particles
        particles = ['は', 'が', 'を', 'に', 'へ', 'と', 'から', 'まで', 'より', 'で', 'の']

        for particle in particles:
            text = text.replace(particle, ' ')

        # Remove symbols
        symbols = ['、', '。', '！', '？', '（', '）', '「', '」', '【', '】', '『', '』']
        for symbol in symbols:
            text = text.replace(symbol, ' ')

        # Split and count
        words = text.split()
        words = [w.strip() for w in words if w.strip() and len(w.strip()) >= 2]

        word_counter = Counter(words)
        # Return top 10
        return dict(word_counter.most_common(10))

    # ========================================
    # AI Generation
    # ========================================

    async def _generate_with_gemini(self, prompt: str) -> str:
        """
        Generate content using Gemini API.

        Args:
            prompt: Generation prompt

        Returns:
            Generated Markdown content
        """
        try:
            # Call Gemini API using the model's generate_content method
            response = self.gemini_client.model.generate_content(prompt)

            # Extract text from response
            content = response.text.strip()

            # Remove code blocks if present
            if content.startswith('```markdown'):
                content = content[11:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]

            return content.strip()

        except Exception as e:
            print(f"Gemini API error: {e}")
            import traceback
            traceback.print_exc()
            return f"# エラー\n\nまとめページの生成中にエラーが発生しました: {e}"
