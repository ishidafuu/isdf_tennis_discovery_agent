"""
Gemini API client for processing voice messages and extracting structured data.
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv

from src.models.session import PracticeSession
from src.ai.structured_extraction import extract_structured_data, ensure_required_fields

# Load environment variables
load_dotenv()


class GeminiClient:
    """Gemini API client for tennis practice analysis."""

    # ソクラテス式プロンプト: アドバイスではなく、気づきを促す質問を生成
    SYSTEM_PROMPT = """あなたはテニス練習のコーチングエージェントです。

**重要な原則:**
1. **No Teaching, But Coaching**: 答えを教えるのではなく、問いかけによってユーザー自身の気づきを引き出す
2. **身体感覚の言語化**: 「どう感じたか」「身体のどこを意識したか」を深掘りする
3. **構造化抽出**: 雑多な会話から「成功パターン」「失敗パターン」「次回テーマ」を抽出する

ユーザーの音声メッセージを分析し、以下を実行してください:
- 文字起こしを行う
- 成功した時の「身体感覚（Somatic Marker）」を特定する
- 失敗パターンとその原因を抽出する
- 次回の練習テーマを提案する（押し付けではなく、ユーザーの言葉から導く）
"""

    EXTRACTION_PROMPT = """以下の音声文字起こしから、構造化されたJSONデータを抽出してください。

文字起こし:
{transcript}

以下のJSON形式で出力してください:
{{
  "tags": ["技術カテゴリ（例: serve, volley, forehand等）"],
  "condition": "全体的な調子（good/normal/bad）",
  "somatic_marker": "好調時の身体感覚（例: 小指を締める感覚、背中の張り）",
  "success_patterns": [
    {{
      "description": "成功した時の感覚や技術ポイント",
      "context": "成功した状況や背景"
    }}
  ],
  "failure_patterns": [
    {{
      "symptom": "失敗の症状（何が起きたか）",
      "cause": "失敗の原因（なぜ起きたか）"
    }}
  ],
  "next_actions": [
    {{
      "theme": "次回のテーマ・課題",
      "focus_point": "特に意識すること"
    }}
  ],
  "summary": "練習の簡潔な要約（2-3文）"
}}

**重要な注意事項:**
- すべてのフィールドは必須です。値がない場合でも null ではなく、以下のデフォルト値を使用してください：
  - tags: 空配列 []
  - condition: "normal"
  - somatic_marker: "" (空文字列)
  - success_patterns: 空配列 []
  - failure_patterns: 空配列 []
  - next_actions: 空配列 []
  - summary: "" (空文字列)
- ユーザーが明示的に言及していない項目は空配列[]または空文字列""にする
- 推測や一般論は避け、ユーザーの実際の体験のみを抽出する
- JSON以外のテキストは出力しない
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key. If None, loads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def process_voice_message(
        self,
        audio_file_path: str,
        scene_type: str = "free_practice"
    ) -> tuple[PracticeSession, Dict[str, Any]]:
        """
        Process a voice message and extract structured practice session data.

        Args:
            audio_file_path: Path to the audio file (mp3, ogg, wav, etc.)
            scene_type: Scene type (wall_practice, school, match, etc.)

        Returns:
            Tuple of (PracticeSession object, scene_specific_data dict)

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If JSON extraction fails
        """
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Step 1: Transcribe audio
        print(f"📝 Transcribing audio file: {audio_path.name}")
        transcript = await self._transcribe_audio(audio_path)

        # Step 2: Extract structured data (scene-specific)
        print(f"🧠 Extracting structured data for scene: {scene_type}...")
        scene_data = await extract_structured_data(transcript, scene_type, self.model)
        scene_data = ensure_required_fields(scene_data, scene_type)

        # Step 3: Extract legacy format for PracticeSession (backward compatibility)
        session_data = await self._extract_structured_data(transcript)

        # Step 4: Create PracticeSession object
        session = PracticeSession(
            raw_transcript=transcript,
            **session_data
        )

        return session, scene_data

    async def _transcribe_audio(self, audio_path: Path) -> str:
        """
        Transcribe audio file using Gemini's multimodal capabilities.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        # Upload audio file
        audio_file = genai.upload_file(path=str(audio_path))

        # Generate transcription
        response = self.model.generate_content([
            self.SYSTEM_PROMPT,
            "以下の音声を文字起こししてください。話者の言葉をそのまま記録してください。",
            audio_file
        ])

        return response.text.strip()

    async def _extract_structured_data(self, transcript: str) -> dict:
        """
        Extract structured data from transcript using JSON mode.

        Args:
            transcript: Transcribed text

        Returns:
            Dictionary containing structured session data
        """
        prompt = self.EXTRACTION_PROMPT.format(transcript=transcript)

        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        try:
            data = json.loads(response.text)

            # Ensure required fields have default values if None
            if data.get("condition") is None:
                data["condition"] = "normal"
            if data.get("tags") is None:
                data["tags"] = []
            if data.get("success_patterns") is None:
                data["success_patterns"] = []
            if data.get("failure_patterns") is None:
                data["failure_patterns"] = []
            if data.get("next_actions") is None:
                data["next_actions"] = []

            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response.text}")

    async def process_text_message(
        self,
        text: str,
        scene_type: str = "free_practice",
        urls: list[str] = None
    ) -> tuple[PracticeSession, Dict[str, Any]]:
        """
        Process a text message and extract structured practice session data.

        Args:
            text: Text message content
            scene_type: Scene type (wall_practice, school, match, etc.)
            urls: List of URLs found in the text

        Returns:
            Tuple of (PracticeSession object, scene_specific_data dict)
        """
        # Extract structured data (scene-specific)
        print(f"🧠 Extracting structured data from text for scene: {scene_type}...")
        scene_data = await extract_structured_data(text, scene_type, self.model)
        scene_data = ensure_required_fields(scene_data, scene_type)

        # Add URLs if present
        if urls:
            scene_data['urls'] = urls

        # Extract legacy format for PracticeSession (backward compatibility)
        session_data = await self._extract_structured_data(text)

        # Create PracticeSession object
        session = PracticeSession(
            raw_transcript=text,
            **session_data
        )

        return session, scene_data

    async def is_tennis_related(self, text: str) -> bool:
        """
        Check if the given text is related to tennis.

        Args:
            text: Text to check (transcription or message content)

        Returns:
            True if tennis-related, False otherwise
        """
        prompt = f"""以下のテキストがテニスに関連する内容かどうかを判定してください。

テキスト:
{text}

**判定基準:**
- テニスの練習、試合、技術、戦術に関する内容
- テニス用語（サーブ、ボレー、ストローク、フォアハンド、バックハンド、スマッシュなど）が含まれる
- テニスコートでの出来事や経験
- テニス用具（ラケット、ボール、シューズなど）に関する内容

**注意:**
- 単に「テニス」という単語があるだけでなく、実質的にテニスについて話しているかを判定する
- 挨拶や雑談のみの内容は False とする

JSON形式で回答してください:
{{"is_tennis_related": true}} または {{"is_tennis_related": false}}
"""

        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        try:
            data = json.loads(response.text)
            return data.get("is_tennis_related", False)
        except json.JSONDecodeError:
            # JSONパースに失敗した場合は、安全側に倒してFalseを返す
            print(f"⚠️ Failed to parse tennis relevance check response: {response.text}")
            return False

    async def generate_followup_question(self, session: PracticeSession) -> str:
        """
        Generate a Socratic follow-up question to deepen reflection.

        Args:
            session: Current practice session data

        Returns:
            Follow-up question text
        """
        prompt = f"""以下の練習記録を見て、ユーザーの気づきを深めるための質問を1つ生成してください。

練習記録:
- 成功パターン: {[p.description for p in session.success_patterns]}
- 失敗パターン: {[p.symptom for p in session.failure_patterns]}
- 調子: {session.condition}

**質問の原則:**
- アドバイスではなく、問いかける
- 「身体のどこを意識しましたか？」「その時、どんな感覚でしたか？」など、感覚の言語化を促す
- 1文で簡潔に

質問のみを出力してください（説明は不要）。
"""

        response = self.model.generate_content(prompt)
        return response.text.strip()
