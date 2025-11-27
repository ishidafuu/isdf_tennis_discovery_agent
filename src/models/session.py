"""
Tennis practice session data models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SuccessPattern(BaseModel):
    """成功パターン（再現したい良い感覚）"""
    description: str = Field(..., description="成功時の身体感覚や技術ポイント")
    context: Optional[str] = Field(None, description="成功した状況・背景")


class FailurePattern(BaseModel):
    """失敗パターン（起きやすいミスと原因）"""
    symptom: str = Field(..., description="失敗の症状（何が起きたか）")
    cause: Optional[str] = Field(None, description="失敗の原因（なぜ起きたか）")


class NextAction(BaseModel):
    """次回アクション（次回試すこと）"""
    theme: str = Field(..., description="次回のテーマ・課題")
    focus_point: Optional[str] = Field(None, description="特に意識すること")


class PracticeSession(BaseModel):
    """練習セッション全体のデータ"""
    date: datetime = Field(default_factory=datetime.now, description="練習日時")
    tags: list[str] = Field(default_factory=list, description="技術タグ（serve, volley等）")
    condition: Optional[str] = Field(default="normal", description="全体的な調子（good/normal/bad）")

    # 身体感覚（検索の肝）
    somatic_marker: Optional[str] = Field(None, description="好調時の主観的な身体感覚")

    # 構造化データ
    success_patterns: list[SuccessPattern] = Field(default_factory=list, description="成功パターンのリスト")
    failure_patterns: list[FailurePattern] = Field(default_factory=list, description="失敗パターンのリスト")
    next_actions: list[NextAction] = Field(default_factory=list, description="次回アクションのリスト")

    # メタデータ
    raw_transcript: str = Field(default="", description="音声の文字起こし（生データ）")
    summary: Optional[str] = Field(None, description="AIによる要約")
    status: str = Field(default="draft", description="ステータス（draft/review_needed/completed）")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-11-26T14:30:00",
                "tags": ["serve", "volley"],
                "condition": "good",
                "somatic_marker": "小指を締める感覚、背中の張り",
                "success_patterns": [
                    {
                        "description": "トスを上げる左手の脱力で、自然な回旋が生まれた",
                        "context": "3ゲーム目以降、リラックスできてから"
                    }
                ],
                "failure_patterns": [
                    {
                        "symptom": "トスが安定しない",
                        "cause": "打つ前に息が止まっている"
                    }
                ],
                "next_actions": [
                    {
                        "theme": "トスアップ時の呼吸を意識する",
                        "focus_point": "上げる瞬間に息を吐く"
                    }
                ],
                "status": "review_needed"
            }
        }
