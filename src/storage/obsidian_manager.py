"""
Obsidian Vault file operations manager.
"""
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import yaml


class ObsidianManager:
    """Manage Obsidian Vault file operations for tennis practice memos."""

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize ObsidianManager.

        Args:
            vault_path: Path to Obsidian vault. If None, uses OBSIDIAN_VAULT_PATH env var.
        """
        self.vault_path = Path(vault_path or os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault"))
        self.sessions_path = self.vault_path / "sessions"

        # Ensure directories exist
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.sessions_path.mkdir(parents=True, exist_ok=True)

    def get_latest_memo(
        self,
        scene_type: Optional[str] = None,
        scene_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest memo, optionally filtered by scene.

        Args:
            scene_type: Scene type to filter by (wall_practice, school, match, etc.)
            scene_name: Scene display name to filter by (壁打ち, スクール, 試合, etc.)

        Returns:
            Dictionary containing memo data, or None if no memos found
        """
        # Get all markdown files from sessions directory (recursively)
        md_files = list(self.sessions_path.rglob("*.md"))

        if not md_files:
            return None

        # Sort by modification time (newest first)
        md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Filter by scene if specified
        if scene_name:
            md_files = [f for f in md_files if scene_name in f.name]

        if not md_files:
            return None

        # Parse and return the latest file
        return self._parse_markdown(md_files[0])

    def get_memos_in_range(
        self,
        start_date: datetime,
        end_date: datetime,
        scene_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get memos within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            scene_name: Optional scene name filter

        Returns:
            List of memo dictionaries, sorted by date
        """
        md_files = list(self.sessions_path.rglob("*.md"))
        memos = []

        for file in md_files:
            # Extract date from filename (YYYY-MM-DD format)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file.name)
            if not date_match:
                continue

            try:
                file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')

                # Check if within range
                if start_date.date() <= file_date.date() <= end_date.date():
                    # Filter by scene if specified
                    if scene_name and scene_name not in file.name:
                        continue

                    memo = self._parse_markdown(file)
                    if memo:
                        memos.append(memo)
            except ValueError:
                continue

        # Sort by date
        return sorted(memos, key=lambda x: x.get('date', ''), reverse=True)

    def search_by_keyword(
        self,
        keyword: str,
        scene_name: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memos by keyword in content.

        Args:
            keyword: Keyword to search for
            scene_name: Optional scene name filter
            max_results: Maximum number of results to return

        Returns:
            List of matching memo dictionaries
        """
        md_files = list(self.sessions_path.rglob("*.md"))
        matches = []

        for file in md_files:
            # Filter by scene if specified
            if scene_name and scene_name not in file.name:
                continue

            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Search for keyword (case-insensitive)
                if keyword.lower() in content.lower():
                    memo = self._parse_markdown(file)
                    if memo:
                        matches.append(memo)

                        if len(matches) >= max_results:
                            break
            except Exception:
                continue

        return matches

    def search_by_date(
        self,
        target_date: datetime,
        scene_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memos by specific date.

        Args:
            target_date: Target date to search
            scene_name: Optional scene name filter

        Returns:
            List of memos from the specified date
        """
        date_str = target_date.strftime('%Y-%m-%d')
        md_files = list(self.sessions_path.rglob("*.md"))
        matches = []

        for file in md_files:
            # Check if filename contains the date
            if date_str in file.name:
                # Filter by scene if specified
                if scene_name and scene_name not in file.name:
                    continue

                memo = self._parse_markdown(file)
                if memo:
                    matches.append(memo)

        return sorted(matches, key=lambda x: x.get('timestamp', ''))

    def get_memo_by_tags(
        self,
        tags: List[str],
        match_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search memos by tags.

        Args:
            tags: List of tags to search for
            match_all: If True, memo must have all tags. If False, any tag matches.

        Returns:
            List of matching memo dictionaries
        """
        md_files = list(self.sessions_path.rglob("*.md"))
        matches = []

        for file in md_files:
            memo = self._parse_markdown(file)
            if not memo:
                continue

            memo_tags = memo.get('tags', [])
            if not memo_tags:
                continue

            # Convert to lowercase for comparison
            memo_tags_lower = [tag.lower() for tag in memo_tags]
            search_tags_lower = [tag.lower() for tag in tags]

            if match_all:
                # All tags must match
                if all(tag in memo_tags_lower for tag in search_tags_lower):
                    matches.append(memo)
            else:
                # Any tag matches
                if any(tag in memo_tags_lower for tag in search_tags_lower):
                    matches.append(memo)

        return sorted(matches, key=lambda x: x.get('date', ''), reverse=True)

    def find_memo_by_fuzzy_criteria(
        self,
        date_text: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        scene_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find memos using fuzzy criteria (for review channel).

        Args:
            date_text: Date text (e.g., "1/15", "昨日", "3日前")
            keywords: List of keywords to search
            scene_name: Scene name to filter

        Returns:
            List of matching memos, sorted by relevance
        """
        candidates = []

        # Extract date if provided
        target_date = None
        if date_text:
            target_date = self._extract_date_from_text(date_text)

        # Search by date
        if target_date:
            candidates = self.search_by_date(target_date, scene_name)
        else:
            # If no date, get recent memos (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            candidates = self.get_memos_in_range(start_date, end_date, scene_name)

        # Filter by keywords if provided
        if keywords and candidates:
            filtered = []
            for memo in candidates:
                content = f"{memo.get('body', '')} {' '.join(memo.get('tags', []))}".lower()
                if any(kw.lower() in content for kw in keywords):
                    filtered.append(memo)
            candidates = filtered

        return candidates

    def _extract_date_from_text(self, text: str) -> Optional[datetime]:
        """
        Extract date from text.

        Args:
            text: Text containing date information

        Returns:
            Datetime object or None
        """
        # Full date: YYYY/MM/DD or YYYY-MM-DD
        pattern1 = r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
        match = re.search(pattern1, text)
        if match:
            year, month, day = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass

        # Short date: MM/DD (current year assumed)
        pattern2 = r'(\d{1,2})[/-](\d{1,2})'
        match = re.search(pattern2, text)
        if match:
            month, day = match.groups()
            try:
                return datetime(datetime.now().year, int(month), int(day))
            except ValueError:
                pass

        # Relative dates
        if '昨日' in text or 'yesterday' in text.lower():
            return datetime.now() - timedelta(days=1)
        if '一昨日' in text:
            return datetime.now() - timedelta(days=2)

        # N days ago: "3日前", "5日前"
        pattern3 = r'(\d+)日前'
        match = re.search(pattern3, text)
        if match:
            days_ago = int(match.group(1))
            return datetime.now() - timedelta(days=days_ago)

        return None

    def _parse_markdown(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse markdown file and extract frontmatter and body.

        Args:
            file_path: Path to markdown file

        Returns:
            Dictionary containing memo data, or None if parse fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()

                    # Add file metadata
                    return {
                        **frontmatter,
                        'body': body,
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime)
                    }

            return None

        except Exception as e:
            print(f"Error parsing markdown file {file_path}: {e}")
            return None

    def append_to_memo(
        self,
        file_path: str,
        append_text: str,
        section_title: str = "振り返り・追記"
    ) -> bool:
        """
        Append content to an existing memo.

        Args:
            file_path: Path to the memo file
            append_text: Text to append
            section_title: Title of the append section

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return False

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create append section with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            append_section = f"""

> [!tip] {section_title}（{timestamp}）
> {append_text}
"""

            # Append to existing content
            updated_content = content + append_section

            with open(path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            return True

        except Exception as e:
            print(f"Error appending to memo: {e}")
            return False
