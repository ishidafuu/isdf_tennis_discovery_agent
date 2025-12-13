"""
Helper functions for posting to the output channel.
"""
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

import discord

from src.config import settings
from src.models.session import PracticeSession

if TYPE_CHECKING:
    from src.bot.client import TennisDiscoveryBot


def extract_keywords_from_session(session: PracticeSession) -> List[str]:
    """
    Extract keywords from a practice session for related memo search.

    Args:
        session: PracticeSession object

    Returns:
        List of keywords
    """
    keywords = []

    # Extract from tags
    if session.tags:
        keywords.extend(session.tags)

    # Extract from success patterns
    for pattern in session.success_patterns[:3]:
        # Extract key technical terms (simple approach: take words longer than 2 chars)
        words = pattern.description.split()
        keywords.extend([w for w in words if len(w) > 2])

    # Extract from failure patterns
    for pattern in session.failure_patterns[:3]:
        words = pattern.symptom.split()
        keywords.extend([w for w in words if len(w) > 2])

    # Remove duplicates and limit
    unique_keywords = list(set(keywords))
    return unique_keywords[:5]  # Top 5 keywords


async def get_output_channel(bot: "TennisDiscoveryBot") -> Optional[discord.TextChannel]:
    """
    Get the tennis output channel.

    Args:
        bot: TennisDiscoveryBot instance

    Returns:
        Discord TextChannel object, or None if not configured
    """
    if settings.tennis_output_channel_id is None:
        return None

    try:
        channel = bot.get_channel(settings.tennis_output_channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            return channel
    except Exception as e:
        print(f"⚠️ Failed to get output channel: {e}")

    return None


async def post_detailed_analysis(
    bot: "TennisDiscoveryBot",
    session: PracticeSession,
    user_name: str,
    timestamp: datetime
) -> Optional[discord.Message]:
    """
    Post detailed analysis to the output channel.

    Args:
        bot: TennisDiscoveryBot instance
        session: PracticeSession object with analysis data
        user_name: Discord username (not displayed, kept for compatibility)
        timestamp: Timestamp of the memo

    Returns:
        Sent message object, or None if failed
    """
    output_channel = await get_output_channel(bot)
    if output_channel is None:
        if bot.debug:
            print("⚠️ Output channel not configured, skipping detailed analysis post")
        return None

    try:
        # Build embed for detailed analysis
        embed = discord.Embed(
            title="📊 今回の気づき",
            color=discord.Color.blue(),
            timestamp=timestamp
        )

        # Add success patterns
        if session.success_patterns:
            success_text = "\n".join([
                f"• {pattern.description}"
                for pattern in session.success_patterns[:5]  # Limit to 5
            ])
            embed.add_field(
                name="✅ うまくいったこと",
                value=success_text,
                inline=False
            )

        # Add failure patterns
        if session.failure_patterns:
            failure_text = "\n".join([
                f"• **{pattern.symptom}**\n  → 原因: {pattern.cause}"
                for pattern in session.failure_patterns[:5]  # Limit to 5
            ])
            embed.add_field(
                name="❌ うまくいかなかったこと",
                value=failure_text,
                inline=False
            )

        # Search for related past memos
        keywords = extract_keywords_from_session(session)
        related_memos = []

        if keywords and bot.obsidian_manager:
            try:
                # Search for related memos using extracted keywords
                for keyword in keywords[:3]:  # Use top 3 keywords
                    results = bot.obsidian_manager.search_by_keyword(
                        keyword=keyword,
                        max_results=2
                    )
                    related_memos.extend(results)

                # Remove duplicates and limit
                seen_paths = set()
                unique_memos = []
                for memo in related_memos:
                    if memo['file_path'] not in seen_paths:
                        seen_paths.add(memo['file_path'])
                        unique_memos.append(memo)

                related_memos = unique_memos[:3]  # Top 3 related memos
            except Exception as e:
                if bot.debug:
                    print(f"⚠️ Failed to search related memos: {e}")
                related_memos = []

        # Add related insights if found
        if related_memos:
            related_text = "\n".join([
                f"• {memo.get('date', '不明')} - {memo.get('raw_text', '')[:50]}..."
                for memo in related_memos
            ])
            embed.add_field(
                name="🔗 関連する過去の気づき",
                value=related_text,
                inline=False
            )

        # Add next actions (improved: focus on areas without recent insights)
        if session.next_actions:
            next_text = "\n".join([
                f"• **{action.theme}**\n  → {action.focus_point}"
                for action in session.next_actions[:3]  # Limit to 3
            ])
            embed.add_field(
                name="🎯 取り組むべきテーマ",
                value=next_text,
                inline=False
            )

        # Add somatic marker if present
        if session.somatic_marker:
            embed.add_field(
                name="💭 身体感覚",
                value=session.somatic_marker,
                inline=False
            )

        embed.set_footer(text="Tennis Discovery Agent")

        # Send to output channel
        message = await output_channel.send(embed=embed)

        if bot.debug:
            print(f"✅ Posted detailed analysis to output channel")

        return message

    except Exception as e:
        print(f"❌ Failed to post detailed analysis: {e}")
        return None


async def post_followup_question(
    bot: "TennisDiscoveryBot",
    question: str,
    user_mention: str
) -> Optional[discord.Message]:
    """
    Post a follow-up question to the output channel.

    Args:
        bot: TennisDiscoveryBot instance
        question: Follow-up question text
        user_mention: Discord user mention (e.g., "<@123456789>")

    Returns:
        Sent message object, or None if failed
    """
    output_channel = await get_output_channel(bot)
    if output_channel is None:
        if bot.debug:
            print("⚠️ Output channel not configured, skipping follow-up question post")
        return None

    try:
        # Post follow-up question with user mention
        message = await output_channel.send(
            f"{user_mention} 💭 {question}"
        )

        if bot.debug:
            print(f"✅ Posted follow-up question to output channel")

        return message

    except Exception as e:
        print(f"❌ Failed to post follow-up question: {e}")
        return None
