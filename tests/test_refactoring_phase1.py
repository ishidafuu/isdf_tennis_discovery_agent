"""
Tests for Phase 1 refactoring: Configuration, Constants, and Type Models.
"""
import pytest
from pathlib import Path

from src.config import Settings
from src.constants import (
    SceneType,
    PracticeCondition,
    SessionStatus,
    MatchResult,
    AUDIO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    SCENE_EMOJIS,
    SCENE_DISPLAY_NAMES,
)
from src.models.scene_data import (
    SceneInfo,
    WallPracticeData,
    SchoolPracticeData,
    MatchData,
    FreePracticeData,
    ImageMemoData,
    VideoMemoData,
    SearchFilters,
)


class TestSettings:
    """Test configuration management."""

    def test_settings_can_be_created_with_minimal_values(self):
        """Test that Settings can be created with minimal required values."""
        settings = Settings(
            discord_bot_token="test_token",
            gemini_api_key="test_key",
            github_repo="user/repo",
            github_token="test_github_token",
        )

        assert settings.discord_bot_token == "test_token"
        assert settings.gemini_api_key == "test_key"
        assert settings.github_repo == "user/repo"
        assert settings.github_token == "test_github_token"

    def test_settings_has_default_values(self):
        """Test that Settings has sensible defaults."""
        settings = Settings(
            discord_bot_token="test_token",
            gemini_api_key="test_key",
            github_repo="user/repo",
            github_token="test_github_token",
        )

        assert settings.obsidian_path == "sessions"
        assert settings.obsidian_vault_path == Path("./obsidian_vault")
        assert settings.debug == False
        assert settings.max_file_size_mb == 20

    def test_max_file_size_bytes_calculation(self):
        """Test that max file size in bytes is calculated correctly."""
        settings = Settings(
            discord_bot_token="test_token",
            gemini_api_key="test_key",
            github_repo="user/repo",
            github_token="test_github_token",
            max_file_size_mb=20,
        )

        assert settings.get_max_file_size_bytes() == 20 * 1024 * 1024


class TestConstants:
    """Test constants and enums."""

    def test_scene_type_enum_values(self):
        """Test that SceneType enum has expected values."""
        assert SceneType.WALL_PRACTICE == "wall_practice"
        assert SceneType.SCHOOL == "school"
        assert SceneType.MATCH == "match"
        assert SceneType.FREE_PRACTICE == "free_practice"
        assert SceneType.REFLECTION == "reflection"
        assert SceneType.QUESTION == "question"
        assert SceneType.ANALYSIS == "analysis"

    def test_practice_condition_enum_values(self):
        """Test that PracticeCondition enum has expected values."""
        assert PracticeCondition.GOOD == "good"
        assert PracticeCondition.NORMAL == "normal"
        assert PracticeCondition.BAD == "bad"

    def test_session_status_enum_values(self):
        """Test that SessionStatus enum has expected values."""
        assert SessionStatus.DRAFT == "draft"
        assert SessionStatus.REVIEW_NEEDED == "review_needed"
        assert SessionStatus.COMPLETED == "completed"

    def test_match_result_enum_values(self):
        """Test that MatchResult enum has expected values."""
        assert MatchResult.WIN == "勝ち"
        assert MatchResult.LOSE == "負け"
        assert MatchResult.UNKNOWN == "不明"

    def test_file_extensions_are_tuples(self):
        """Test that file extensions are immutable tuples."""
        assert isinstance(AUDIO_EXTENSIONS, tuple)
        assert isinstance(IMAGE_EXTENSIONS, tuple)
        assert isinstance(VIDEO_EXTENSIONS, tuple)

    def test_scene_emojis_mapping(self):
        """Test that scene emojis are properly mapped."""
        assert SCENE_EMOJIS[SceneType.WALL_PRACTICE] == "🧱"
        assert SCENE_EMOJIS[SceneType.SCHOOL] == "🎓"
        assert SCENE_EMOJIS[SceneType.MATCH] == "🏆"
        assert SCENE_EMOJIS[SceneType.FREE_PRACTICE] == "🎾"

    def test_scene_display_names_mapping(self):
        """Test that scene display names are properly mapped."""
        assert SCENE_DISPLAY_NAMES[SceneType.WALL_PRACTICE] == "壁打ち"
        assert SCENE_DISPLAY_NAMES[SceneType.SCHOOL] == "スクール"
        assert SCENE_DISPLAY_NAMES[SceneType.MATCH] == "試合"
        assert SCENE_DISPLAY_NAMES[SceneType.FREE_PRACTICE] == "フリー練習"


class TestSceneDataModels:
    """Test scene data models."""

    def test_scene_info_creation(self):
        """Test SceneInfo model creation."""
        scene_info = SceneInfo(
            type="wall_practice",
            name="壁打ち",
            emoji="🧱",
            description="基礎練習",
        )

        assert scene_info.type == "wall_practice"
        assert scene_info.name == "壁打ち"
        assert scene_info.emoji == "🧱"
        assert scene_info.description == "基礎練習"

    def test_wall_practice_data_defaults(self):
        """Test WallPracticeData has proper defaults."""
        data = WallPracticeData()

        assert data.drill == ""
        assert data.duration == 0
        assert data.focus == ""
        assert data.tags == []
        assert data.summary == ""

    def test_school_practice_data_defaults(self):
        """Test SchoolPracticeData has proper defaults."""
        data = SchoolPracticeData()

        assert data.coach_feedback == ""
        assert data.new_technique == ""
        assert data.tags == []

    def test_match_data_defaults(self):
        """Test MatchData has proper defaults."""
        data = MatchData()

        assert data.opponent == ""
        assert data.result == "不明"
        assert data.tags == []

    def test_match_data_result_validation(self):
        """Test MatchData result field validation."""
        # Valid values should work
        data1 = MatchData(result="勝ち")
        assert data1.result == "勝ち"

        data2 = MatchData(result="負け")
        assert data2.result == "負け"

        data3 = MatchData(result="不明")
        assert data3.result == "不明"

    def test_image_memo_data_creation(self):
        """Test ImageMemoData creation."""
        data = ImageMemoData(
            date="2025-11-29",
            scene="壁打ち",
            file_path="attachments/2025-11-29/image.jpg",
            user_comment="Test comment",
            tags=["tennis", "image"],
        )

        assert data.date == "2025-11-29"
        assert data.scene == "壁打ち"
        assert data.input_type == "image"
        assert data.file_path == "attachments/2025-11-29/image.jpg"
        assert data.user_comment == "Test comment"

    def test_video_memo_data_creation(self):
        """Test VideoMemoData creation."""
        data = VideoMemoData(
            date="2025-11-29",
            scene="試合",
            file_path="attachments/2025-11-29/video.mp4",
        )

        assert data.date == "2025-11-29"
        assert data.scene == "試合"
        assert data.input_type == "video"
        assert data.file_path == "attachments/2025-11-29/video.mp4"

    def test_search_filters_defaults(self):
        """Test SearchFilters has proper defaults."""
        filters = SearchFilters()

        assert filters.keywords == []
        assert filters.tags == []
        assert filters.scene_name is None
        assert filters.date_range is None
        assert filters.match_all_tags == False

    def test_search_filters_with_values(self):
        """Test SearchFilters with custom values."""
        filters = SearchFilters(
            keywords=["フォアハンド", "サーブ"],
            tags=["serve", "forehand"],
            scene_name="壁打ち",
            match_all_tags=True,
        )

        assert filters.keywords == ["フォアハンド", "サーブ"]
        assert filters.tags == ["serve", "forehand"]
        assert filters.scene_name == "壁打ち"
        assert filters.match_all_tags == True
