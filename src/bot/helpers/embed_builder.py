"""
Discord Embed builder for practice session results.

Centralizes Discord Embed creation logic to avoid duplication.
"""
from typing import Optional
from datetime import datetime

import discord

from src.models.session import PracticeSession
from src.models.scene_data import SceneInfo


class SessionEmbedBuilder:
    """Builder for creating Discord Embeds for practice sessions."""

    @staticmethod
    def build(
        session: PracticeSession,
        scene_info: SceneInfo,
        file_url: str,
        previous_log: Optional[str] = None,
        extra_fields: Optional[list[dict]] = None,
        custom_title: Optional[str] = None,
        custom_description: Optional[str] = None,
    ) -> discord.Embed:
        """
        Build a Discord Embed for a practice session.

        Args:
            session: Practice session data
            scene_info: Scene information (type, name, emoji, etc.)
            file_url: GitHub URL of the saved file
            previous_log: Optional previous log summary
            extra_fields: Optional extra fields to add
            custom_title: Optional custom title (overrides default)
            custom_description: Optional custom description

        Returns:
            Discord Embed object
        """
        # Build title
        title = custom_title or f"{scene_info.emoji} {scene_info.name}の記録を保存しました"

        # Build description
        description = custom_description or session.summary or "記録しました"

        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=scene_info.color,
        )

        # Add previous log (cycle) if available
        if previous_log:
            embed.add_field(
                name="🔄 サイクル",
                value=previous_log,
                inline=False
            )

        # Add somatic marker if available
        if session.somatic_marker:
            embed.add_field(
                name="🎯 身体感覚",
                value=session.somatic_marker,
                inline=False
            )

        # Add success patterns if available
        if session.success_patterns:
            success_text = "\n".join([
                f"• {p.description}" for p in session.success_patterns[:3]
            ])
            embed.add_field(
                name="🟩 成功パターン",
                value=success_text,
                inline=False
            )

        # Add failure patterns if available
        if session.failure_patterns:
            failure_text = "\n".join([
                f"• {p.symptom}" for p in session.failure_patterns[:3]
            ])
            embed.add_field(
                name="🟥 失敗パターン",
                value=failure_text,
                inline=False
            )

        # Add next actions if available
        if session.next_actions:
            next_text = "\n".join([
                f"• {a.theme}" for a in session.next_actions[:3]
            ])
            embed.add_field(
                name="🟦 次回のテーマ",
                value=next_text,
                inline=False
            )

        # Add extra fields if provided
        if extra_fields:
            for field in extra_fields:
                embed.add_field(**field)

        # Add GitHub link
        embed.add_field(
            name="📁 GitHub",
            value=f"[ファイルを見る]({file_url})",
            inline=False
        )

        # Add footer with date
        date_str = session.date.strftime('%Y年%m月%d日')
        embed.set_footer(text=f"📅 {date_str}")

        return embed

    @staticmethod
    def build_image_embed(
        scene_info: SceneInfo,
        date: datetime,
        filename: str,
        user_comment: str,
        file_url: str,
    ) -> discord.Embed:
        """
        Build a Discord Embed for an image memo.

        Args:
            scene_info: Scene information
            date: Date of the memo
            filename: Image filename
            user_comment: User's comment
            file_url: GitHub URL of the saved file

        Returns:
            Discord Embed object
        """
        description = user_comment or "画像を記録しました"

        embed = discord.Embed(
            title=f"{scene_info.emoji} {scene_info.name}の画像メモを保存しました",
            description=description,
            color=discord.Color.purple(),
        )

        embed.add_field(
            name="📸 画像ファイル",
            value=f"`{filename}`",
            inline=False
        )

        if user_comment:
            embed.add_field(
                name="💭 コメント",
                value=user_comment,
                inline=False
            )

        embed.add_field(
            name="📁 GitHub",
            value=f"[ファイルを見る]({file_url})",
            inline=False
        )

        date_str = date.strftime("%Y-%m-%d")
        embed.set_footer(text=f"📅 {date_str}")

        return embed

    @staticmethod
    def build_video_embed(
        scene_info: SceneInfo,
        date: datetime,
        filename: str,
        user_comment: str,
        file_url: str,
    ) -> discord.Embed:
        """
        Build a Discord Embed for a video memo.

        Args:
            scene_info: Scene information
            date: Date of the memo
            filename: Video filename
            user_comment: User's comment
            file_url: GitHub URL of the saved file

        Returns:
            Discord Embed object
        """
        description = user_comment or "動画を記録しました"

        embed = discord.Embed(
            title=f"{scene_info.emoji} {scene_info.name}の動画メモを保存しました",
            description=description,
            color=discord.Color.orange(),
        )

        embed.add_field(
            name="🎥 動画ファイル",
            value=f"`{filename}`",
            inline=False
        )

        if user_comment:
            embed.add_field(
                name="💭 コメント",
                value=user_comment,
                inline=False
            )

        embed.add_field(
            name="📁 GitHub",
            value=f"[ファイルを見る]({file_url})",
            inline=False
        )

        date_str = date.strftime("%Y-%m-%d")
        embed.set_footer(text=f"📅 {date_str}")

        return embed

    @staticmethod
    def build_reflection_embed(
        target_date: str,
        target_scene: str,
        target_filename: str,
        append_content: str,
        file_url: Optional[str] = None,
        other_candidates: Optional[list[dict]] = None,
    ) -> discord.Embed:
        """
        Build a Discord Embed for a reflection memo.

        Args:
            target_date: Date of the target memo
            target_scene: Scene of the target memo
            target_filename: Filename of the target memo
            append_content: Content that was appended
            file_url: Optional GitHub URL
            other_candidates: Optional list of other matching memos

        Returns:
            Discord Embed object
        """
        embed = discord.Embed(
            title="📝 振り返りメモを追記しました",
            description=f"**{target_date}** の **{target_scene}** メモに追記",
            color=discord.Color.gold(),
        )

        embed.add_field(
            name="📄 追記したメモ",
            value=f"`{target_filename}`",
            inline=False
        )

        # Truncate content if too long
        max_length = 200
        truncated_content = append_content[:max_length]
        if len(append_content) > max_length:
            truncated_content += "..."

        embed.add_field(
            name="💭 追記内容",
            value=truncated_content,
            inline=False
        )

        if file_url:
            embed.add_field(
                name="📁 GitHub",
                value=f"[ファイルを見る]({file_url})",
                inline=False
            )

        # Show other candidates if there were multiple matches
        if other_candidates and len(other_candidates) > 0:
            other_memos = "\n".join([
                f"• {m.get('date')} - {m.get('scene', '不明')}"
                for m in other_candidates[:2]  # Show up to 2 more
            ])
            embed.add_field(
                name="ℹ️ 他の候補",
                value=f"次のメモも見つかりました:\n{other_memos}",
                inline=False
            )

        return embed
