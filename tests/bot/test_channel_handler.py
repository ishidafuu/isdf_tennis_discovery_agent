"""
Tests for channel_handler module.
"""
import pytest

from src.bot.channel_handler import (
    detect_scene_from_channel,
    is_reflection_channel,
    is_allowed_channel,
    get_scene_info,
)
from src.constants import SceneType


class TestIsAllowedChannel:
    """Test is_allowed_channel function."""

    def test_allowed_channels_japanese(self):
        """Test that Japanese channel names are allowed."""
        assert is_allowed_channel("壁打ち") is True
        assert is_allowed_channel("スクール") is True
        assert is_allowed_channel("試合") is True
        assert is_allowed_channel("フリー練習") is True
        assert is_allowed_channel("振り返り") is True
        assert is_allowed_channel("質問") is True
        assert is_allowed_channel("分析") is True

    def test_allowed_channels_english(self):
        """Test that English channel names are allowed."""
        assert is_allowed_channel("wall") is True
        assert is_allowed_channel("wall-practice") is True
        assert is_allowed_channel("school") is True
        assert is_allowed_channel("lesson") is True
        assert is_allowed_channel("match") is True
        assert is_allowed_channel("game") is True
        assert is_allowed_channel("free") is True
        assert is_allowed_channel("free-practice") is True
        assert is_allowed_channel("reflection") is True
        assert is_allowed_channel("review") is True
        assert is_allowed_channel("question") is True
        assert is_allowed_channel("qa") is True
        assert is_allowed_channel("analysis") is True
        assert is_allowed_channel("analytics") is True

    def test_allowed_channels_case_insensitive(self):
        """Test that channel name matching is case-insensitive."""
        assert is_allowed_channel("WALL") is True
        assert is_allowed_channel("Wall-Practice") is True
        assert is_allowed_channel("SCHOOL") is True
        assert is_allowed_channel("Match") is True

    def test_disallowed_channels(self):
        """Test that non-designated channels are not allowed."""
        assert is_allowed_channel("general") is False
        assert is_allowed_channel("random") is False
        assert is_allowed_channel("bot-commands") is False
        assert is_allowed_channel("off-topic") is False
        assert is_allowed_channel("雑談") is False
        assert is_allowed_channel("その他") is False

    def test_partial_match_allowed(self):
        """Test that partial matches work (e.g., '壁打ち-練習' contains '壁打ち')."""
        assert is_allowed_channel("壁打ち-練習") is True
        assert is_allowed_channel("試合-記録") is True
        assert is_allowed_channel("wall-practice-notes") is True


class TestDetectSceneFromChannel:
    """Test detect_scene_from_channel function."""

    def test_wall_practice_detection(self):
        """Test wall practice scene detection."""
        scene_type, scene_name = detect_scene_from_channel("壁打ち")
        assert scene_type == SceneType.WALL_PRACTICE
        assert scene_name == "壁打ち"

    def test_school_detection(self):
        """Test school scene detection."""
        scene_type, scene_name = detect_scene_from_channel("スクール")
        assert scene_type == SceneType.SCHOOL
        assert scene_name == "スクール"

    def test_match_detection(self):
        """Test match scene detection."""
        scene_type, scene_name = detect_scene_from_channel("試合")
        assert scene_type == SceneType.MATCH
        assert scene_name == "試合"

    def test_free_practice_detection(self):
        """Test free practice scene detection."""
        scene_type, scene_name = detect_scene_from_channel("フリー練習")
        assert scene_type == SceneType.FREE_PRACTICE
        assert scene_name == "フリー練習"

    def test_reflection_detection(self):
        """Test reflection scene detection."""
        scene_type, scene_name = detect_scene_from_channel("振り返り")
        assert scene_type == SceneType.REFLECTION
        assert scene_name == "振り返り"


class TestIsReflectionChannel:
    """Test is_reflection_channel function."""

    def test_reflection_channel_japanese(self):
        """Test Japanese reflection channel name."""
        assert is_reflection_channel("振り返り") is True

    def test_reflection_channel_english(self):
        """Test English reflection channel names."""
        assert is_reflection_channel("reflection") is True
        assert is_reflection_channel("review") is True

    def test_non_reflection_channel(self):
        """Test non-reflection channels."""
        assert is_reflection_channel("壁打ち") is False
        assert is_reflection_channel("スクール") is False
        assert is_reflection_channel("wall") is False


class TestGetSceneInfo:
    """Test get_scene_info function."""

    def test_scene_info_structure(self):
        """Test that SceneInfo has correct structure."""
        scene_info = get_scene_info("壁打ち")
        assert scene_info.type == SceneType.WALL_PRACTICE
        assert scene_info.name == "壁打ち"
        assert scene_info.emoji == "🧱"
        assert "基礎練習" in scene_info.description
