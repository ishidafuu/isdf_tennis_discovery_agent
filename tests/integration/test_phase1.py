"""
Phase 1 Integration Tests for Tennis Discovery Agent.

Tests all major features implemented in Phase 1:
- Multi-modal input (voice, text, image, video)
- Scene detection
- Previous log loading
- Reflection channel
- Git LFS
- GitHub sync
"""
import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.bot.channel_handler import (
    detect_scene_from_channel,
    is_reflection_channel,
    get_scene_emoji
)
from src.storage.obsidian_manager import ObsidianManager
from src.models.session import PracticeSession, SuccessPattern, NextAction


class TestChannelDetection:
    """Test channel detection functionality."""

    def test_detect_wall_practice(self):
        """Test wall practice channel detection."""
        scene_type, scene_name = detect_scene_from_channel("壁打ち")
        assert scene_type == "wall_practice"
        assert scene_name == "壁打ち"

        scene_type, scene_name = detect_scene_from_channel("wall")
        assert scene_type == "wall_practice"
        assert scene_name == "壁打ち"

    def test_detect_school(self):
        """Test school channel detection."""
        scene_type, scene_name = detect_scene_from_channel("スクール")
        assert scene_type == "school"
        assert scene_name == "スクール"

        scene_type, scene_name = detect_scene_from_channel("school")
        assert scene_type == "school"

    def test_detect_match(self):
        """Test match channel detection."""
        scene_type, scene_name = detect_scene_from_channel("試合")
        assert scene_type == "match"
        assert scene_name == "試合"

        scene_type, scene_name = detect_scene_from_channel("match")
        assert scene_type == "match"

    def test_detect_reflection(self):
        """Test reflection channel detection."""
        scene_type, scene_name = detect_scene_from_channel("振り返り")
        assert scene_type == "reflection"
        assert scene_name == "振り返り"

        assert is_reflection_channel("振り返り") is True
        assert is_reflection_channel("壁打ち") is False

    def test_get_scene_emoji(self):
        """Test scene emoji mapping."""
        assert get_scene_emoji("wall_practice") == "🧱"
        assert get_scene_emoji("school") == "🎓"
        assert get_scene_emoji("match") == "🏆"
        assert get_scene_emoji("free_practice") == "🎾"
        assert get_scene_emoji("reflection") == "📝"


class TestObsidianManager:
    """Test ObsidianManager functionality."""

    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_vault"
            vault_path.mkdir()
            yield vault_path

    @pytest.fixture
    def obsidian_manager(self, temp_vault):
        """Create ObsidianManager instance with temp vault."""
        return ObsidianManager(vault_path=str(temp_vault))

    def test_vault_initialization(self, obsidian_manager, temp_vault):
        """Test vault directory initialization."""
        assert obsidian_manager.vault_path == temp_vault
        assert obsidian_manager.sessions_path.exists()

    def test_get_latest_memo_empty(self, obsidian_manager):
        """Test getting latest memo from empty vault."""
        result = obsidian_manager.get_latest_memo()
        assert result is None

    def test_date_extraction(self, obsidian_manager):
        """Test date extraction from text."""
        # Full date
        date1 = obsidian_manager._extract_date_from_text("2025-01-15")
        assert date1.date() == datetime(2025, 1, 15).date()

        # Short date
        date2 = obsidian_manager._extract_date_from_text("1/15")
        assert date2.month == 1
        assert date2.day == 15

        # Relative date
        date3 = obsidian_manager._extract_date_from_text("昨日")
        expected = datetime.now() - timedelta(days=1)
        assert date3.date() == expected.date()

        # Days ago
        date4 = obsidian_manager._extract_date_from_text("3日前")
        expected = datetime.now() - timedelta(days=3)
        assert date4.date() == expected.date()

    def test_create_and_retrieve_memo(self, obsidian_manager, temp_vault):
        """Test creating and retrieving a memo."""
        # Create a test memo file
        sessions_path = temp_vault / "sessions"
        sessions_path.mkdir(exist_ok=True)

        memo_content = """---
date: 2025-01-15
scene: 壁打ち
tags: [tennis, forehand]
---

# 壁打ち練習

今日はフォアハンドを練習した。
"""
        memo_file = sessions_path / "2025-01-15-143000-壁打ち.md"
        memo_file.write_text(memo_content, encoding='utf-8')

        # Retrieve latest memo
        result = obsidian_manager.get_latest_memo()
        assert result is not None
        assert result['date'] == '2025-01-15'
        assert result['scene'] == '壁打ち'
        assert 'フォアハンド' in result['body']

    def test_scene_filter(self, obsidian_manager, temp_vault):
        """Test scene filtering."""
        sessions_path = temp_vault / "sessions"
        sessions_path.mkdir(exist_ok=True)

        # Create multiple memos
        for scene in ["壁打ち", "スクール", "試合"]:
            memo_content = f"""---
date: 2025-01-15
scene: {scene}
---

# {scene}
"""
            memo_file = sessions_path / f"2025-01-15-{scene}.md"
            memo_file.write_text(memo_content, encoding='utf-8')

        # Filter by scene
        result = obsidian_manager.get_latest_memo(scene_name="壁打ち")
        assert result is not None
        assert result['scene'] == '壁打ち'

    def test_append_to_memo(self, obsidian_manager, temp_vault):
        """Test appending content to existing memo."""
        sessions_path = temp_vault / "sessions"
        sessions_path.mkdir(exist_ok=True)

        # Create original memo
        memo_content = """---
date: 2025-01-15
scene: 壁打ち
---

# 壁打ち練習

オリジナルの内容
"""
        memo_file = sessions_path / "2025-01-15-壁打ち.md"
        memo_file.write_text(memo_content, encoding='utf-8')

        # Append content
        success = obsidian_manager.append_to_memo(
            file_path=str(memo_file),
            append_text="追記の内容です",
            section_title="振り返り"
        )
        assert success is True

        # Verify append
        updated_content = memo_file.read_text(encoding='utf-8')
        assert "追記の内容です" in updated_content
        assert "振り返り" in updated_content


class TestPracticeSessionModel:
    """Test PracticeSession data model."""

    def test_create_basic_session(self):
        """Test creating a basic practice session."""
        session = PracticeSession(
            raw_transcript="今日はサーブを練習した",
            summary="サーブ練習",
            tags=["serve"]
        )

        assert session.raw_transcript == "今日はサーブを練習した"
        assert session.summary == "サーブ練習"
        assert session.tags == ["serve"]
        assert session.condition == "normal"
        assert session.status == "draft"

    def test_session_with_patterns(self):
        """Test session with success and failure patterns."""
        session = PracticeSession(
            raw_transcript="練習記録",
            success_patterns=[
                SuccessPattern(
                    description="トスを前に上げるとうまくいった",
                    context="3ゲーム目以降"
                )
            ],
            next_actions=[
                NextAction(
                    theme="トスの位置を安定させる",
                    focus_point="前方30cm"
                )
            ]
        )

        assert len(session.success_patterns) == 1
        assert session.success_patterns[0].description == "トスを前に上げるとうまくいった"
        assert len(session.next_actions) == 1
        assert session.next_actions[0].theme == "トスの位置を安定させる"


class TestFileNaming:
    """Test file naming conventions."""

    def test_unique_filenames(self):
        """Test that filenames include timestamp for uniqueness."""
        from src.storage.markdown_builder import MarkdownBuilder

        builder = MarkdownBuilder()

        # Create two sessions at different times
        session1 = PracticeSession(
            raw_transcript="First session",
            summary="Session 1"
        )
        session1.date = datetime(2025, 1, 15, 14, 30, 0)

        session2 = PracticeSession(
            raw_transcript="Second session",
            summary="Session 2"
        )
        session2.date = datetime(2025, 1, 15, 15, 45, 30)

        filename1 = builder.get_filename_for_session(session1, "壁打ち")
        filename2 = builder.get_filename_for_session(session2, "壁打ち")

        # Filenames should be different due to timestamp
        assert filename1 != filename2
        assert "2025-01-15-143000" in filename1
        assert "2025-01-15-154530" in filename2
        assert "壁打ち" in filename1
        assert "壁打ち" in filename2


class TestGitLFS:
    """Test Git LFS configuration."""

    def test_gitattributes_exists(self):
        """Test that .gitattributes file exists and contains LFS config."""
        gitattributes_path = Path(".gitattributes")
        assert gitattributes_path.exists(), ".gitattributes file should exist"

        content = gitattributes_path.read_text()

        # Check for image files
        assert "*.jpg" in content
        assert "*.png" in content
        assert "filter=lfs" in content

        # Check for video files
        assert "*.mp4" in content
        assert "*.mov" in content

        # Check for audio files
        assert "*.ogg" in content
        assert "*.mp3" in content


class TestEnvironmentConfiguration:
    """Test environment configuration."""

    def test_env_example_exists(self):
        """Test that .env.example file exists."""
        env_example = Path(".env.example")
        assert env_example.exists(), ".env.example should exist"

        content = env_example.read_text()

        # Check for required environment variables
        assert "DISCORD_BOT_TOKEN" in content
        assert "GEMINI_API_KEY" in content
        assert "GITHUB_TOKEN" in content
        assert "GITHUB_REPO" in content
        assert "OBSIDIAN_VAULT_PATH" in content
        assert "ADMIN_USER_ID" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
