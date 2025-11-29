"""
Application constants and enums.

Centralizes magic numbers, strings, and configuration values.
"""
from enum import Enum
from typing import Final

# ==============================================================================
# File Size Limits
# ==============================================================================

MAX_FILE_SIZE_BYTES: Final[int] = 20 * 1024 * 1024  # 20MB

# ==============================================================================
# File Extensions
# ==============================================================================

AUDIO_EXTENSIONS: Final[tuple[str, ...]] = (
    ".ogg", ".mp3", ".wav", ".m4a", ".opus", ".webm"
)

IMAGE_EXTENSIONS: Final[tuple[str, ...]] = (
    ".jpg", ".jpeg", ".png", ".gif"
)

VIDEO_EXTENSIONS: Final[tuple[str, ...]] = (
    ".mp4", ".mov", ".avi", ".webm"
)

# ==============================================================================
# Markdown Section Titles
# ==============================================================================

SECTION_TITLE_REFLECTION: Final[str] = "振り返り・追記"
SECTION_TITLE_TRANSCRIPT: Final[str] = "文字起こし全文"
SECTION_TITLE_SUMMARY: Final[str] = "練習サマリー"
SECTION_TITLE_SUCCESS: Final[str] = "Success: 再現したい良い感覚"
SECTION_TITLE_FAILURE: Final[str] = "Warning: 起きやすいミスと原因"
SECTION_TITLE_NEXT_ACTION: Final[str] = "Next Action: 次回試すこと"

# ==============================================================================
# Practice Session Status
# ==============================================================================

class SessionStatus(str, Enum):
    """Practice session status."""
    DRAFT = "draft"
    REVIEW_NEEDED = "review_needed"
    COMPLETED = "completed"


# ==============================================================================
# Practice Condition
# ==============================================================================

class PracticeCondition(str, Enum):
    """Overall practice condition."""
    GOOD = "good"
    NORMAL = "normal"
    BAD = "bad"


# ==============================================================================
# Scene Types
# ==============================================================================

class SceneType(str, Enum):
    """Practice scene types."""
    WALL_PRACTICE = "wall_practice"
    SCHOOL = "school"
    MATCH = "match"
    FREE_PRACTICE = "free_practice"
    REFLECTION = "reflection"
    QUESTION = "question"
    ANALYSIS = "analysis"


# ==============================================================================
# Scene Emojis
# ==============================================================================

SCENE_EMOJIS: Final[dict[str, str]] = {
    SceneType.WALL_PRACTICE: "🧱",
    SceneType.SCHOOL: "🎓",
    SceneType.MATCH: "🏆",
    SceneType.FREE_PRACTICE: "🎾",
    SceneType.REFLECTION: "📝",
    SceneType.QUESTION: "❓",
    SceneType.ANALYSIS: "📊",
}

# ==============================================================================
# Scene Display Names
# ==============================================================================

SCENE_DISPLAY_NAMES: Final[dict[str, str]] = {
    SceneType.WALL_PRACTICE: "壁打ち",
    SceneType.SCHOOL: "スクール",
    SceneType.MATCH: "試合",
    SceneType.FREE_PRACTICE: "フリー練習",
    SceneType.REFLECTION: "振り返り",
    SceneType.QUESTION: "質問",
    SceneType.ANALYSIS: "分析",
}

# ==============================================================================
# Scene Descriptions
# ==============================================================================

SCENE_DESCRIPTIONS: Final[dict[str, str]] = {
    SceneType.WALL_PRACTICE: "基礎練習・反復ドリル",
    SceneType.SCHOOL: "コーチの指導あり",
    SceneType.MATCH: "実戦・練習試合",
    SceneType.FREE_PRACTICE: "友人との自由練習",
    SceneType.REFLECTION: "後日の追記・補足",
    SceneType.QUESTION: "過去の記録を検索して質問に回答",
    SceneType.ANALYSIS: "統計分析・パターン発見",
}

# ==============================================================================
# Channel Name Mappings
# ==============================================================================

CHANNEL_TO_SCENE: Final[dict[str, tuple[str, str]]] = {
    # Japanese names
    "壁打ち": (SceneType.WALL_PRACTICE, SCENE_DISPLAY_NAMES[SceneType.WALL_PRACTICE]),
    "スクール": (SceneType.SCHOOL, SCENE_DISPLAY_NAMES[SceneType.SCHOOL]),
    "試合": (SceneType.MATCH, SCENE_DISPLAY_NAMES[SceneType.MATCH]),
    "フリー練習": (SceneType.FREE_PRACTICE, SCENE_DISPLAY_NAMES[SceneType.FREE_PRACTICE]),
    "振り返り": (SceneType.REFLECTION, SCENE_DISPLAY_NAMES[SceneType.REFLECTION]),
    "質問": (SceneType.QUESTION, SCENE_DISPLAY_NAMES[SceneType.QUESTION]),
    "分析": (SceneType.ANALYSIS, SCENE_DISPLAY_NAMES[SceneType.ANALYSIS]),

    # English names
    "wall": (SceneType.WALL_PRACTICE, SCENE_DISPLAY_NAMES[SceneType.WALL_PRACTICE]),
    "wall-practice": (SceneType.WALL_PRACTICE, SCENE_DISPLAY_NAMES[SceneType.WALL_PRACTICE]),
    "school": (SceneType.SCHOOL, SCENE_DISPLAY_NAMES[SceneType.SCHOOL]),
    "lesson": (SceneType.SCHOOL, SCENE_DISPLAY_NAMES[SceneType.SCHOOL]),
    "match": (SceneType.MATCH, SCENE_DISPLAY_NAMES[SceneType.MATCH]),
    "game": (SceneType.MATCH, SCENE_DISPLAY_NAMES[SceneType.MATCH]),
    "free": (SceneType.FREE_PRACTICE, SCENE_DISPLAY_NAMES[SceneType.FREE_PRACTICE]),
    "free-practice": (SceneType.FREE_PRACTICE, SCENE_DISPLAY_NAMES[SceneType.FREE_PRACTICE]),
    "reflection": (SceneType.REFLECTION, SCENE_DISPLAY_NAMES[SceneType.REFLECTION]),
    "review": (SceneType.REFLECTION, SCENE_DISPLAY_NAMES[SceneType.REFLECTION]),
    "question": (SceneType.QUESTION, SCENE_DISPLAY_NAMES[SceneType.QUESTION]),
    "qa": (SceneType.QUESTION, SCENE_DISPLAY_NAMES[SceneType.QUESTION]),
    "analysis": (SceneType.ANALYSIS, SCENE_DISPLAY_NAMES[SceneType.ANALYSIS]),
    "analytics": (SceneType.ANALYSIS, SCENE_DISPLAY_NAMES[SceneType.ANALYSIS]),
}

# ==============================================================================
# Match Results
# ==============================================================================

class MatchResult(str, Enum):
    """Match result."""
    WIN = "勝ち"
    LOSE = "負け"
    UNKNOWN = "不明"


# ==============================================================================
# Default Values
# ==============================================================================

DEFAULT_TAG: Final[str] = "tennis"
DEFAULT_SCENE_NAME: Final[str] = "その他"
DEFAULT_CONDITION: Final[str] = PracticeCondition.NORMAL

# ==============================================================================
# Gemini API Limits
# ==============================================================================

GEMINI_FREE_TIER_DAILY_REQUESTS: Final[int] = 1500
GEMINI_REQUESTS_PER_MEMO: Final[int] = 2  # transcribe + extract

# ==============================================================================
# Search and Analysis
# ==============================================================================

DEFAULT_SEARCH_LIMIT: Final[int] = 10
DEFAULT_RECENT_DAYS: Final[int] = 30
SIMILARITY_THRESHOLD: Final[float] = 0.7

# ==============================================================================
# Discord Message Lengths
# ==============================================================================

DISCORD_EMBED_FIELD_MAX_LENGTH: Final[int] = 1024
DISCORD_EMBED_DESCRIPTION_MAX_LENGTH: Final[int] = 4096
DISCORD_MESSAGE_CONTENT_MIN_LENGTH: Final[int] = 10
