"""
Scene-specific data models.

Type-safe models for different practice scenes using Pydantic.
"""
from typing import Literal, Union
from pydantic import BaseModel, Field

import discord


class SceneInfo(BaseModel):
    """Scene information with display properties."""

    type: str = Field(..., description="Scene type identifier")
    name: str = Field(..., description="Display name")
    emoji: str = Field(..., description="Emoji for visual representation")
    description: str = Field(default="", description="Scene description")

    @property
    def color(self) -> discord.Color:
        """Get Discord color for this scene."""
        color_map = {
            "wall_practice": discord.Color.blue(),
            "school": discord.Color.green(),
            "match": discord.Color.gold(),
            "free_practice": discord.Color.purple(),
            "reflection": discord.Color.orange(),
            "question": discord.Color.teal(),
            "analysis": discord.Color.dark_blue(),
        }
        return color_map.get(self.type, discord.Color.default())


class WallPracticeData(BaseModel):
    """Wall practice (壁打ち) specific data."""

    drill: str = Field(default="", description="Practice drill name")
    duration: int = Field(default=0, description="Duration in minutes")
    focus: str = Field(default="", description="Focus point")
    body_sensation: str = Field(default="", description="Body sensation awareness")
    improvement: str = Field(default="", description="Improved aspects")
    issue: str = Field(default="", description="Issues to address")
    tags: list[str] = Field(default_factory=list, description="Technical tags")
    summary: str = Field(default="", description="Session summary")
    next_action: str = Field(default="", description="Next action items")


class SchoolPracticeData(BaseModel):
    """School practice (スクール) specific data."""

    coach_feedback: str = Field(default="", description="Coach's feedback")
    new_technique: str = Field(default="", description="New technique learned")
    practice_content: str = Field(default="", description="Practice content")
    realization: str = Field(default="", description="Personal realization")
    homework: str = Field(default="", description="Homework assignment")
    tags: list[str] = Field(default_factory=list, description="Technical tags")
    summary: str = Field(default="", description="Session summary")
    next_action: str = Field(default="", description="Next action items")


class MatchData(BaseModel):
    """Match (試合) specific data."""

    opponent: str = Field(default="", description="Opponent name")
    opponent_level: str = Field(default="", description="Opponent level")
    score: str = Field(default="", description="Match score")
    result: Literal["勝ち", "負け", "不明"] = Field(
        default="不明",
        description="Match result"
    )
    good_plays: str = Field(default="", description="Good plays")
    bad_plays: str = Field(default="", description="Bad plays")
    mental: str = Field(default="", description="Mental aspects")
    strategy: str = Field(default="", description="Strategy and tactics")
    tags: list[str] = Field(default_factory=list, description="Technical tags")
    summary: str = Field(default="", description="Session summary")
    next_action: str = Field(default="", description="Next action items")


class FreePracticeData(BaseModel):
    """Free practice (フリー練習) specific data."""

    practice_content: str = Field(default="", description="Practice content")
    realization: str = Field(default="", description="Personal realization")
    issue: str = Field(default="", description="Issues to address")
    tags: list[str] = Field(default_factory=list, description="Technical tags")
    summary: str = Field(default="", description="Session summary")
    next_action: str = Field(default="", description="Next action items")


class ImageMemoData(BaseModel):
    """Image memo specific data."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    scene: str = Field(..., description="Scene name")
    input_type: Literal["image"] = Field(default="image", description="Input type")
    file_path: str = Field(..., description="Relative path to image file")
    user_comment: str = Field(default="", description="User's comment")
    tags: list[str] = Field(default_factory=list, description="Tags")


class VideoMemoData(BaseModel):
    """Video memo specific data."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    scene: str = Field(..., description="Scene name")
    input_type: Literal["video"] = Field(default="video", description="Input type")
    file_path: str = Field(..., description="Relative path to video file")
    user_comment: str = Field(default="", description="User's comment")
    tags: list[str] = Field(default_factory=list, description="Tags")


# Union type for all scene data types
SceneData = Union[
    WallPracticeData,
    SchoolPracticeData,
    MatchData,
    FreePracticeData,
    ImageMemoData,
    VideoMemoData,
    dict  # Fallback for backward compatibility
]


class SearchFilters(BaseModel):
    """Search filter criteria for memo queries."""

    keywords: list[str] = Field(default_factory=list, description="Keywords to search")
    tags: list[str] = Field(default_factory=list, description="Tags to filter by")
    scene_name: str | None = Field(default=None, description="Scene name filter")
    date_range: tuple[str, str] | None = Field(
        default=None,
        description="Date range (start, end)"
    )
    match_all_tags: bool = Field(
        default=False,
        description="Require all tags to match"
    )
