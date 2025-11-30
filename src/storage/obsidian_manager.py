"""
Obsidian Vault file operations manager (REFACTORED).

Unified search interface to reduce code duplication.
"""
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import yaml

from src.models.scene_data import SearchFilters


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

        # Cache for memos (invalidated on write operations)
        self._memo_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 60  # Cache TTL: 60 seconds

    def get_latest_memo(
        self,
        scene_type: Optional[str] = None,
        scene_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest memo, optionally filtered by scene.

        REFACTORED: Now uses unified search interface.

        Args:
            scene_type: Scene type to filter by (wall_practice, school, match, etc.)
            scene_name: Scene display name to filter by (壁打ち, スクール, 試合, etc.)

        Returns:
            Dictionary containing memo data, or None if no memos found
        """
        filters = SearchFilters(scene_name=scene_name) if scene_name else None
        results = self.search(filters=filters, limit=1)
        return results[0] if results else None

    def get_memos_in_range(
        self,
        start_date: datetime,
        end_date: datetime,
        scene_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get memos within a date range.

        REFACTORED: Now uses unified search interface.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            scene_name: Optional scene name filter

        Returns:
            List of memo dictionaries, sorted by date
        """
        date_range = (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        filters = SearchFilters(date_range=date_range, scene_name=scene_name)
        return self.search(filters=filters, limit=1000)

    def search_by_keyword(
        self,
        keyword: str,
        scene_name: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memos by keyword in content.

        REFACTORED: Now uses unified search interface.

        Args:
            keyword: Keyword to search for
            scene_name: Optional scene name filter
            max_results: Maximum number of results to return

        Returns:
            List of matching memo dictionaries
        """
        filters = SearchFilters(keywords=[keyword], scene_name=scene_name)
        return self.search(filters=filters, limit=max_results)

    def search_by_date(
        self,
        target_date: datetime,
        scene_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memos by specific date.

        REFACTORED: Now uses unified search interface.

        Args:
            target_date: Target date to search
            scene_name: Optional scene name filter

        Returns:
            List of memos from the specified date
        """
        date_str = target_date.strftime('%Y-%m-%d')
        filters = SearchFilters(date_range=(date_str, date_str), scene_name=scene_name)
        return self.search(filters=filters, limit=100)

    def get_memo_by_tags(
        self,
        tags: List[str],
        match_all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search memos by tags.

        REFACTORED: Now uses unified search interface.

        Args:
            tags: List of tags to search for
            match_all: If True, memo must have all tags. If False, any tag matches.

        Returns:
            List of matching memo dictionaries
        """
        filters = SearchFilters(tags=tags, match_all_tags=match_all)
        return self.search(filters=filters, limit=100)

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

    # ========================================================================
    # New unified search interface (Phase 3 refactoring)
    # ========================================================================

    def search(
        self,
        filters: Optional[SearchFilters] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Unified search interface for memos.

        This method consolidates the functionality of:
        - search_by_keyword()
        - search_by_date()
        - get_memo_by_tags()
        - get_memos_in_range()

        Args:
            filters: Search filters (keywords, tags, scene, date_range)
            limit: Maximum number of results to return

        Returns:
            List of matching memos, sorted by date (newest first)
        """
        # Get all memos (with caching)
        memos = self._get_all_memos()

        # Apply filters if provided
        if filters:
            if filters.keywords:
                memos = self._filter_by_keywords(memos, filters.keywords)

            if filters.date_range:
                memos = self._filter_by_date_range(memos, filters.date_range)

            if filters.tags:
                memos = self._filter_by_tags(memos, filters.tags, filters.match_all_tags)

            if filters.scene_name:
                memos = self._filter_by_scene(memos, filters.scene_name)

        # Sort by date (newest first)
        memos.sort(key=lambda x: x.get('date', ''), reverse=True)

        return memos[:limit]

    def _get_all_memos(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get all memos from vault (with caching).

        Args:
            force_refresh: Force cache refresh

        Returns:
            List of all memo dictionaries
        """
        # Check cache validity
        if not force_refresh and self._memo_cache is not None and self._cache_timestamp is not None:
            cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
            if cache_age < self._cache_ttl_seconds:
                return self._memo_cache

        # Refresh cache
        md_files = list(self.sessions_path.rglob("*.md"))
        memos = []

        for file in md_files:
            memo = self._parse_markdown(file)
            if memo:
                memos.append(memo)

        # Update cache
        self._memo_cache = memos
        self._cache_timestamp = datetime.now()

        return memos

    def _filter_by_keywords(
        self,
        memos: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter memos by keywords in content."""
        filtered = []
        for memo in memos:
            content = f"{memo.get('body', '')} {' '.join(memo.get('tags', []))}".lower()
            if any(kw.lower() in content for kw in keywords):
                filtered.append(memo)
        return filtered

    def _filter_by_date_range(
        self,
        memos: List[Dict[str, Any]],
        date_range: tuple[str, str]
    ) -> List[Dict[str, Any]]:
        """Filter memos by date range."""
        start_str, end_str = date_range
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

        filtered = []
        for memo in memos:
            memo_date_str = memo.get('date', '')
            if not memo_date_str:
                continue

            try:
                memo_date = datetime.strptime(memo_date_str, '%Y-%m-%d').date()
                if start_date <= memo_date <= end_date:
                    filtered.append(memo)
            except ValueError:
                continue

        return filtered

    def _filter_by_tags(
        self,
        memos: List[Dict[str, Any]],
        tags: List[str],
        match_all: bool = False
    ) -> List[Dict[str, Any]]:
        """Filter memos by tags."""
        filtered = []
        search_tags_lower = [tag.lower() for tag in tags]

        for memo in memos:
            memo_tags = memo.get('tags', [])
            if not memo_tags:
                continue

            memo_tags_lower = [tag.lower() for tag in memo_tags]

            if match_all:
                # All tags must match
                if all(tag in memo_tags_lower for tag in search_tags_lower):
                    filtered.append(memo)
            else:
                # Any tag matches
                if any(tag in memo_tags_lower for tag in search_tags_lower):
                    filtered.append(memo)

        return filtered

    def _filter_by_scene(
        self,
        memos: List[Dict[str, Any]],
        scene_name: str
    ) -> List[Dict[str, Any]]:
        """Filter memos by scene name."""
        return [m for m in memos if scene_name in m.get('file_name', '')]

    def _invalidate_cache(self):
        """Invalidate memo cache (call this after write operations)."""
        self._memo_cache = None
        self._cache_timestamp = None

    # ========================================================================
    # End of unified search interface
    # ========================================================================

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

            # Invalidate cache after write operation
            self._invalidate_cache()

            return True

        except Exception as e:
            print(f"Error appending to memo: {e}")
            return False
