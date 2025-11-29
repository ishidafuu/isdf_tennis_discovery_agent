"""
Helper functions for retrieving and formatting previous practice logs.
"""
from typing import Optional
import re


def get_previous_log_summary(obsidian_manager, scene_name: str, debug: bool = False) -> Optional[str]:
    """
    Get previous log summary for the same scene.

    Args:
        obsidian_manager: ObsidianManager instance
        scene_name: Scene display name
        debug: Debug mode flag

    Returns:
        Formatted summary string or None
    """
    try:
        previous_memo = obsidian_manager.get_latest_memo(scene_name=scene_name)

        if not previous_memo:
            return None

        # Extract key information
        date = previous_memo.get('date', '不明')
        next_action = None
        somatic_marker = previous_memo.get('somatic_marker', '')

        # Try to extract next_action from body (various formats)
        body = previous_memo.get('body', '')

        # Look for next_action patterns in body
        if '## 次回' in body or '## Next Action' in body:
            # Extract text after "次回" header
            pattern = r'## (?:次回|Next Action)[^\n]*\n(.+?)(?=\n##|\Z)'
            match = re.search(pattern, body, re.DOTALL)
            if match:
                next_action = match.group(1).strip()

        # Build summary
        summary_parts = [f"📅 前回: {date}"]

        if somatic_marker:
            summary_parts.append(f"🎯 前回の身体感覚: {somatic_marker[:50]}...")

        if next_action:
            # Limit length
            next_action_short = next_action[:100] + "..." if len(next_action) > 100 else next_action
            summary_parts.append(f"📝 前回の課題:\n{next_action_short}")

        return "\n".join(summary_parts)

    except Exception as e:
        if debug:
            print(f"Error getting previous log: {e}")
        return None
