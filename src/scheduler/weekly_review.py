"""
Weekly review generator for Tennis Discovery Agent.

Automatically generates weekly practice summary and analysis.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter

import yaml
import google.generativeai as genai
from dotenv import load_dotenv

from src.storage.obsidian_manager import ObsidianManager
from src.storage.github_sync import GitHubSync

# Load environment variables
load_dotenv()


class WeeklyReviewGenerator:
    """Generate weekly practice review and summary."""

    def __init__(self):
        """Initialize weekly review generator."""
        self.obsidian_manager = ObsidianManager()
        self.github_sync = GitHubSync()

        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

    def generate_weekly_review(self, week_offset: int = 0) -> str:
        """
        Generate weekly review for the specified week.

        Args:
            week_offset: Number of weeks ago (0 = current week, 1 = last week, etc.)

        Returns:
            Path to generated review file
        """
        # Calculate date range for the week
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday() + (week_offset * 7))
        end_of_week = start_of_week + timedelta(days=6)

        print(f"📊 Generating weekly review for {start_of_week.date()} to {end_of_week.date()}")

        # Get memos for the week
        memos = self.obsidian_manager.get_memos_in_range(
            start_date=start_of_week,
            end_date=end_of_week
        )

        if not memos:
            print("⚠️ No memos found for this week")
            return None

        # Calculate statistics
        stats = self._calculate_statistics(memos)

        # Extract key insights
        insights = self._extract_insights(memos)

        # Generate AI summary
        ai_summary = self._generate_ai_summary(memos, stats) if self.model else ""

        # Build markdown content
        markdown = self._build_review_markdown(
            start_date=start_of_week,
            end_date=end_of_week,
            stats=stats,
            insights=insights,
            ai_summary=ai_summary,
            memos=memos
        )

        # Save to weekly-reviews directory
        file_path = self._save_review(markdown, start_of_week)

        # Push to GitHub
        self._push_to_github(file_path, start_of_week)

        print(f"✅ Weekly review generated: {file_path}")
        return file_path

    def _calculate_statistics(self, memos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate practice statistics from memos.

        Args:
            memos: List of memo dictionaries

        Returns:
            Statistics dictionary
        """
        stats = {
            "total_sessions": len(memos),
            "practice_days": len(set(m.get('date') for m in memos if m.get('date'))),
            "scenes": Counter(),
            "tags": Counter(),
            "total_duration": 0,
        }

        for memo in memos:
            # Count scenes
            scene = memo.get('scene', 'その他')
            stats['scenes'][scene] += 1

            # Count tags
            tags = memo.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    stats['tags'][tag] += 1

            # Sum duration (if available)
            duration = memo.get('duration', 0)
            if isinstance(duration, (int, float)):
                stats['total_duration'] += duration

        return stats

    def _extract_insights(self, memos: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract key insights from memos.

        Args:
            memos: List of memo dictionaries

        Returns:
            Insights dictionary
        """
        insights = {
            "frequent_keywords": [],
            "common_issues": [],
            "improvements": [],
        }

        # Collect keywords from body text
        keyword_counter = Counter()
        issue_keywords = ["課題", "問題", "難しい", "うまくいかない"]
        improvement_keywords = ["改善", "良くなった", "できた", "成功"]

        for memo in memos:
            body = memo.get('body', '')

            # Extract frequent words (simple approach)
            words = body.split()
            for word in words:
                if len(word) > 2 and word not in ["です", "ます", "した", "でした"]:
                    keyword_counter[word] += 1

            # Detect issues
            if any(kw in body for kw in issue_keywords):
                # Extract sentence containing issue keyword
                for line in body.split('\n'):
                    if any(kw in line for kw in issue_keywords):
                        insights['common_issues'].append(line.strip()[:100])
                        break

            # Detect improvements
            if any(kw in body for kw in improvement_keywords):
                for line in body.split('\n'):
                    if any(kw in line for kw in improvement_keywords):
                        insights['improvements'].append(line.strip()[:100])
                        break

        # Get top 10 frequent keywords
        insights['frequent_keywords'] = [
            word for word, count in keyword_counter.most_common(10)
        ]

        return insights

    def _generate_ai_summary(
        self,
        memos: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> str:
        """
        Generate AI-powered weekly summary.

        Args:
            memos: List of memo dictionaries
            stats: Statistics dictionary

        Returns:
            AI-generated summary text
        """
        if not self.model:
            return ""

        # Prepare memo summaries for AI
        memo_texts = []
        for memo in memos[:20]:  # Limit to 20 most recent
            date = memo.get('date', 'unknown')
            scene = memo.get('scene', 'その他')
            body = memo.get('body', '')[:500]  # Limit body length
            memo_texts.append(f"**{date} ({scene})**\n{body}\n")

        combined_text = "\n---\n".join(memo_texts)

        prompt = f"""以下は1週間のテニス練習記録です。この週の練習を分析して、簡潔な週次サマリーを生成してください。

練習統計:
- 総セッション数: {stats['total_sessions']}
- 練習日数: {stats['practice_days']}日
- シーン別回数: {dict(stats['scenes'])}

練習記録:
{combined_text}

以下の観点でサマリーを生成してください:
1. **今週の概要**: 練習の全体的な傾向
2. **成長のポイント**: 改善した点、良かった点
3. **継続課題**: 来週も意識すべきこと
4. **提案**: 次週に試すべき練習内容

200-300文字程度で簡潔にまとめてください。
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ AI summary generation failed: {e}")
            return ""

    def _build_review_markdown(
        self,
        start_date: datetime,
        end_date: datetime,
        stats: Dict[str, Any],
        insights: Dict[str, List[str]],
        ai_summary: str,
        memos: List[Dict[str, Any]]
    ) -> str:
        """
        Build weekly review markdown content.

        Args:
            start_date: Week start date
            end_date: Week end date
            stats: Statistics dictionary
            insights: Insights dictionary
            ai_summary: AI-generated summary
            memos: List of memo dictionaries

        Returns:
            Markdown content
        """
        # Calculate week number
        week_num = start_date.isocalendar()[1]
        year = start_date.year

        # Frontmatter
        frontmatter_data = {
            "date": start_date.strftime("%Y-%m-%d"),
            "week": week_num,
            "year": year,
            "type": "weekly-review",
            "tags": ["tennis", "weekly-review", f"{year}"],
        }
        frontmatter = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

        markdown = f"""---
{frontmatter}---

# 週次レビュー - {year}年 第{week_num}週

**期間**: {start_date.strftime('%Y年%m月%d日')} - {end_date.strftime('%Y年%m月%d日')}

---

## 📊 練習統計

| 項目 | 数値 |
|------|------|
| **総セッション数** | {stats['total_sessions']} 回 |
| **練習日数** | {stats['practice_days']} 日 |
| **総練習時間** | {stats['total_duration']} 分 |

### シーン別の内訳

"""

        # Scene breakdown
        for scene, count in stats['scenes'].most_common():
            markdown += f"- **{scene}**: {count}回\n"

        markdown += "\n### 技術タグ別\n\n"

        # Tag breakdown
        for tag, count in stats['tags'].most_common(10):
            markdown += f"- `{tag}`: {count}回\n"

        # AI Summary
        if ai_summary:
            markdown += f"""

---

## 🤖 AI週次サマリー

{ai_summary}

"""

        # Insights
        if insights['frequent_keywords']:
            markdown += f"""
---

## 🔑 頻出キーワード

{', '.join(insights['frequent_keywords'])}

"""

        if insights['common_issues']:
            markdown += f"""
## ⚠️ 共通課題

"""
            for issue in insights['common_issues'][:5]:
                markdown += f"- {issue}\n"

        if insights['improvements']:
            markdown += f"""

## ✅ 改善ポイント

"""
            for improvement in insights['improvements'][:5]:
                markdown += f"- {improvement}\n"

        # Memo list
        markdown += f"""

---

## 📝 今週の記録一覧

"""
        for memo in memos:
            date = memo.get('date', 'unknown')
            scene = memo.get('scene', 'その他')
            file_name = memo.get('file_name', '')
            markdown += f"- [{date} - {scene}]({file_name})\n"

        return markdown

    def _save_review(self, markdown: str, start_date: datetime) -> Path:
        """
        Save weekly review to file.

        Args:
            markdown: Markdown content
            start_date: Week start date

        Returns:
            Path to saved file
        """
        # Get vault path
        vault_path = self.obsidian_manager.vault_path
        reviews_dir = vault_path / "weekly-reviews"
        reviews_dir.mkdir(exist_ok=True)

        # Create year subdirectory
        year = start_date.year
        year_dir = reviews_dir / str(year)
        year_dir.mkdir(exist_ok=True)

        # Generate filename
        week_num = start_date.isocalendar()[1]
        filename = f"{year}-W{week_num:02d}.md"
        file_path = year_dir / filename

        # Write file
        file_path.write_text(markdown, encoding='utf-8')

        return file_path

    def _push_to_github(self, file_path: Path, start_date: datetime):
        """
        Push weekly review to GitHub.

        Args:
            file_path: Path to review file
            start_date: Week start date
        """
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')

            # Generate GitHub path
            year = start_date.year
            week_num = start_date.isocalendar()[1]
            github_path = f"weekly-reviews/{year}/{year}-W{week_num:02d}.md"

            # Commit message
            commit_message = f"Add weekly review: {year} Week {week_num}"

            # Push to GitHub
            self.github_sync._push_file(
                file_path=github_path,
                content=content,
                commit_message=commit_message
            )

            print(f"✅ Pushed to GitHub: {github_path}")

        except Exception as e:
            print(f"⚠️ Failed to push to GitHub: {e}")


def generate_current_week_review():
    """Generate review for current week (convenience function)."""
    generator = WeeklyReviewGenerator()
    return generator.generate_weekly_review(week_offset=0)


def generate_last_week_review():
    """Generate review for last week (convenience function)."""
    generator = WeeklyReviewGenerator()
    return generator.generate_weekly_review(week_offset=1)


if __name__ == "__main__":
    # Generate current week review
    generate_current_week_review()
