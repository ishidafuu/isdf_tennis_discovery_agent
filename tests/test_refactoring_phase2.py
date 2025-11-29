"""
Tests for Phase 2 refactoring: Discord Embed and Media Helpers.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

import discord

from src.bot.helpers.embed_builder import SessionEmbedBuilder
from src.bot.helpers.markdown_helpers import (
    build_media_markdown,
    build_image_markdown,
    build_video_markdown,
)
from src.models.session import PracticeSession, SuccessPattern, NextAction
from src.models.scene_data import SceneInfo


class TestEmbedBuilder:
    """Test Discord Embed builder."""

    def test_build_basic_session_embed(self):
        """Test building a basic session embed."""
        session = PracticeSession(
            raw_transcript="Test transcript",
            summary="Test summary",
            tags=["serve"],
        )

        scene_info = SceneInfo(
            type="wall_practice",
            name="壁打ち",
            emoji="🧱",
            description="基礎練習",
        )

        embed = SessionEmbedBuilder.build(
            session=session,
            scene_info=scene_info,
            file_url="https://github.com/user/repo/blob/main/test.md",
        )

        assert isinstance(embed, discord.Embed)
        assert "壁打ち" in embed.title
        assert embed.description == "Test summary"

    def test_build_session_embed_with_success_patterns(self):
        """Test building embed with success patterns."""
        session = PracticeSession(
            raw_transcript="Test transcript",
            summary="Test summary",
            success_patterns=[
                SuccessPattern(description="Good serve", context="After warmup")
            ],
        )

        scene_info = SceneInfo(
            type="school",
            name="スクール",
            emoji="🎓",
        )

        embed = SessionEmbedBuilder.build(
            session=session,
            scene_info=scene_info,
            file_url="https://github.com/test.md",
        )

        # Check that success pattern is included
        field_names = [field.name for field in embed.fields]
        assert "🟩 成功パターン" in field_names

    def test_build_session_embed_with_previous_log(self):
        """Test building embed with previous log."""
        session = PracticeSession(
            raw_transcript="Test transcript",
            summary="Test summary",
        )

        scene_info = SceneInfo(
            type="match",
            name="試合",
            emoji="🏆",
        )

        previous_log = "前回: サーブが安定していた"

        embed = SessionEmbedBuilder.build(
            session=session,
            scene_info=scene_info,
            file_url="https://github.com/test.md",
            previous_log=previous_log,
        )

        # Check that previous log is included
        field_names = [field.name for field in embed.fields]
        assert "🔄 サイクル" in field_names

        # Find the cycle field and check its value
        for field in embed.fields:
            if field.name == "🔄 サイクル":
                assert previous_log in field.value

    def test_build_image_embed(self):
        """Test building an image embed."""
        date = datetime(2025, 11, 29, 14, 30)
        scene_info = SceneInfo(
            type="wall_practice",
            name="壁打ち",
            emoji="🧱",
        )

        embed = SessionEmbedBuilder.build_image_embed(
            scene_info=scene_info,
            date=date,
            filename="test_image.jpg",
            user_comment="Test comment",
            file_url="https://github.com/test.md",
        )

        assert isinstance(embed, discord.Embed)
        assert "画像メモ" in embed.title
        assert embed.description == "Test comment"

    def test_build_video_embed(self):
        """Test building a video embed."""
        date = datetime(2025, 11, 29, 14, 30)
        scene_info = SceneInfo(
            type="match",
            name="試合",
            emoji="🏆",
        )

        embed = SessionEmbedBuilder.build_video_embed(
            scene_info=scene_info,
            date=date,
            filename="test_video.mp4",
            user_comment="Good match",
            file_url="https://github.com/test.md",
        )

        assert isinstance(embed, discord.Embed)
        assert "動画メモ" in embed.title
        assert embed.description == "Good match"

    def test_build_reflection_embed(self):
        """Test building a reflection embed."""
        embed = SessionEmbedBuilder.build_reflection_embed(
            target_date="2025-11-28",
            target_scene="壁打ち",
            target_filename="2025-11-28-壁打ち.md",
            append_content="振り返りのコメント",
        )

        assert isinstance(embed, discord.Embed)
        assert "振り返りメモ" in embed.title
        assert "2025-11-28" in embed.description
        assert "壁打ち" in embed.description


class TestMarkdownHelpers:
    """Test markdown helpers."""

    def test_build_media_markdown_image(self):
        """Test building image markdown."""
        memo_data = {
            'date': '2025-11-29',
            'file_path': 'attachments/2025-11-29/test.jpg',
            'user_comment': 'Test comment',
            'tags': ['tennis', 'image'],
        }

        markdown = build_media_markdown(memo_data, "壁打ち", "image")

        assert "画像メモ" in markdown
        assert "📸 画像" in markdown
        assert memo_data['file_path'] in markdown
        assert memo_data['user_comment'] in markdown

    def test_build_media_markdown_video(self):
        """Test building video markdown."""
        memo_data = {
            'date': '2025-11-29',
            'file_path': 'attachments/2025-11-29/test.mp4',
            'user_comment': 'Test video',
            'tags': ['tennis', 'video'],
        }

        markdown = build_media_markdown(memo_data, "試合", "video")

        assert "動画メモ" in markdown
        assert "🎥 動画" in markdown
        assert memo_data['file_path'] in markdown
        assert memo_data['user_comment'] in markdown

    def test_build_image_markdown_backward_compatibility(self):
        """Test backward compatibility of build_image_markdown."""
        memo_data = {
            'date': '2025-11-29',
            'file_path': 'test.jpg',
            'user_comment': 'Test',
        }

        # Old function should still work
        markdown = build_image_markdown(memo_data, "壁打ち")

        assert "画像メモ" in markdown
        assert memo_data['file_path'] in markdown

    def test_build_video_markdown_backward_compatibility(self):
        """Test backward compatibility of build_video_markdown."""
        memo_data = {
            'date': '2025-11-29',
            'file_path': 'test.mp4',
            'user_comment': 'Test',
        }

        # Old function should still work
        markdown = build_video_markdown(memo_data, "試合")

        assert "動画メモ" in markdown
        assert memo_data['file_path'] in markdown
