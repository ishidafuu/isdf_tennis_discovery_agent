"""
Markdown file builder for Obsidian format.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import yaml

from src.models.session import PracticeSession
from src.storage.markdown_templates import build_markdown_for_scene


class MarkdownBuilder:
    """Build Obsidian-formatted markdown files from practice sessions."""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize markdown builder.

        Args:
            output_dir: Directory to save markdown files. Defaults to './output'
        """
        self.output_dir = output_dir or Path("./output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_for_scene(
        self,
        scene_type: str,
        scene_name: str,
        scene_data: Dict[str, Any],
        raw_transcript: str = ""
    ) -> str:
        """
        Build markdown content from scene-specific data.

        Args:
            scene_type: Scene type (wall_practice, school, etc.)
            scene_name: Scene display name (壁打ち, スクール, etc.)
            scene_data: Scene-specific structured data
            raw_transcript: Raw transcript text

        Returns:
            Markdown content as string
        """
        # Add date if not present
        if 'date' not in scene_data:
            scene_data['date'] = datetime.now().strftime('%Y-%m-%d')

        return build_markdown_for_scene(scene_type, scene_name, scene_data, raw_transcript)

    def build(self, session: PracticeSession) -> str:
        """
        Build markdown content from practice session.

        Args:
            session: PracticeSession object

        Returns:
            Markdown content as string
        """
        # Build frontmatter (YAML)
        frontmatter = self._build_frontmatter(session)

        # Build body sections
        summary_section = self._build_summary_section(session)
        success_section = self._build_success_section(session)
        failure_section = self._build_failure_section(session)
        next_action_section = self._build_next_action_section(session)
        transcript_section = self._build_transcript_section(session)

        # Combine all sections
        markdown = f"""---
{frontmatter}---

{summary_section}

{success_section}

{failure_section}

{next_action_section}

{transcript_section}
"""

        return markdown

    def save(self, session: PracticeSession, filename: Optional[str] = None) -> Path:
        """
        Save session as markdown file.

        Args:
            session: PracticeSession object
            filename: Custom filename. If None, uses date-based name.

        Returns:
            Path to saved file
        """
        if filename is None:
            date_str = session.date.strftime("%Y-%m-%d")
            filename = f"{date_str}-practice.md"

        file_path = self.output_dir / filename
        markdown = self.build(session)

        file_path.write_text(markdown, encoding="utf-8")
        print(f"✅ Markdown saved: {file_path}")

        return file_path

    def _build_frontmatter(self, session: PracticeSession) -> str:
        """Build YAML frontmatter."""
        # Extract failure pattern summary for frontmatter
        failure_summary = None
        if session.failure_patterns:
            failure_summary = session.failure_patterns[0].symptom

        # Extract next theme for frontmatter
        next_theme = None
        if session.next_actions:
            next_theme = session.next_actions[0].theme

        frontmatter_data = {
            "date": session.date.strftime("%Y-%m-%d"),
            "tags": session.tags if session.tags else ["tennis"],
            "condition": session.condition,
            "somatic_marker": session.somatic_marker or "",
            "failure_pattern": failure_summary or "",
            "next_theme": next_theme or "",
            "status": session.status
        }

        return yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)

    def _build_summary_section(self, session: PracticeSession) -> str:
        """Build summary section."""
        if not session.summary:
            return ""

        return f"""## 📊 練習サマリー

{session.summary}
"""

    def _build_success_section(self, session: PracticeSession) -> str:
        """Build success patterns section with Obsidian callout."""
        if not session.success_patterns:
            return ""

        callout_content = []
        for pattern in session.success_patterns:
            content = f"**{pattern.description}**"
            if pattern.context:
                content += f"\n- 状況: {pattern.context}"
            callout_content.append(content)

        patterns_text = "\n\n".join(callout_content)

        return f"""## 🟩 Success: 再現したい良い感覚

> [!success] 成功パターン
> {patterns_text}
"""

    def _build_failure_section(self, session: PracticeSession) -> str:
        """Build failure patterns section with Obsidian callout."""
        if not session.failure_patterns:
            return ""

        callout_content = []
        for pattern in session.failure_patterns:
            content = f"**症状**: {pattern.symptom}"
            if pattern.cause:
                content += f"\n- **原因**: {pattern.cause}"
            callout_content.append(content)

        patterns_text = "\n\n".join(callout_content)

        return f"""## 🟥 Warning: 起きやすいミスと原因

> [!warning] 失敗パターン
> {patterns_text}
"""

    def _build_next_action_section(self, session: PracticeSession) -> str:
        """Build next actions section with Obsidian callout."""
        if not session.next_actions:
            return ""

        callout_content = []
        for action in session.next_actions:
            content = f"**{action.theme}**"
            if action.focus_point:
                content += f"\n- 意識すること: {action.focus_point}"
            callout_content.append(content)

        actions_text = "\n\n".join(callout_content)

        return f"""## 🟦 Next Action: 次回試すこと

> [!info] 次回のテーマ
> {actions_text}
"""

    def _build_transcript_section(self, session: PracticeSession) -> str:
        """Build transcript section."""
        if not session.raw_transcript:
            return ""

        return f"""---

## 📝 文字起こし全文

{session.raw_transcript}
"""

    def get_filename_for_session(self, session: PracticeSession, scene_name: str = "") -> str:
        """
        Generate filename for a session with timestamp for uniqueness.

        Args:
            session: PracticeSession object
            scene_name: Scene name for the filename (optional)

        Returns:
            Filename string (e.g., "2025-11-26-143052-壁打ち.md" or "2025-11-26-143052-practice.md")
        """
        date_str = session.date.strftime("%Y-%m-%d")
        time_str = session.date.strftime("%H%M%S")
        if scene_name:
            return f"{date_str}-{time_str}-{scene_name}.md"
        return f"{date_str}-{time_str}-practice.md"

    def get_relative_path_for_session(self, session: PracticeSession, base_path: str = "sessions") -> str:
        """
        Generate relative path for a session (for GitHub organization).

        Args:
            session: PracticeSession object
            base_path: Base directory name

        Returns:
            Relative path string (e.g., "sessions/2025/11/2025-11-26-practice.md")
        """
        year = session.date.strftime("%Y")
        month = session.date.strftime("%m")
        filename = self.get_filename_for_session(session)

        return f"{base_path}/{year}/{month}/{filename}"
