"""
Embedding generation module for semantic search using Gemini API.

This module provides functionality to convert text into vector embeddings
for semantic similarity search and advanced analysis.
"""
import os
import asyncio
from typing import Optional
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmbeddingGenerator:
    """Generate embeddings using Gemini Embedding API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Embedding Generator.

        Args:
            api_key: Gemini API key. If None, loads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)

    async def get_embedding(self, text: str, task_type: str = "retrieval_document") -> list[float]:
        """
        Generate embedding vector from text.

        Args:
            text: Text to embed
            task_type: Task type for embedding generation. Options:
                - "retrieval_document": For documents to be retrieved
                - "retrieval_query": For search queries
                - "semantic_similarity": For similarity comparison
                - "classification": For text classification

        Returns:
            List of floats representing the embedding vector

        Raises:
            ValueError: If text is empty or API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            result = genai.embed_content(
                model='models/text-embedding-004',
                content=text,
                task_type=task_type
            )

            return result['embedding']
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {e}")

    async def get_query_embedding(self, query: str) -> list[float]:
        """
        Generate embedding for search query.

        Args:
            query: Search query text

        Returns:
            Embedding vector optimized for search queries
        """
        return await self.get_embedding(query, task_type="retrieval_query")

    async def batch_embed_texts(
        self,
        texts: list[str],
        task_type: str = "retrieval_document",
        delay: float = 0.1
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts with rate limiting.

        Args:
            texts: List of texts to embed
            task_type: Task type for embedding generation
            delay: Delay between API calls in seconds (to avoid rate limits)

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If any text fails to embed
        """
        embeddings = []

        for i, text in enumerate(texts):
            try:
                embedding = await self.get_embedding(text, task_type)
                embeddings.append(embedding)

                # Add delay to avoid rate limits (except for last item)
                if i < len(texts) - 1:
                    await asyncio.sleep(delay)

            except Exception as e:
                print(f"⚠️  Failed to embed text {i+1}/{len(texts)}: {e}")
                # Return None for failed embeddings to maintain alignment
                embeddings.append(None)

        return embeddings

    async def embed_memo_content(self, memo_data: dict) -> list[float]:
        """
        Generate embedding from memo data.

        Combines various memo fields into a single text for embedding:
        - Summary
        - Tags
        - Success patterns
        - Issues/challenges
        - Next actions

        Args:
            memo_data: Dictionary containing memo data (from structured extraction)

        Returns:
            Embedding vector for the memo

        Raises:
            ValueError: If memo_data is empty or invalid
        """
        if not memo_data:
            raise ValueError("memo_data cannot be empty")

        # Build combined text from memo fields
        text_parts = []

        # Add summary
        if summary := memo_data.get('summary'):
            text_parts.append(f"要約: {summary}")

        # Add tags
        if tags := memo_data.get('tags'):
            text_parts.append(f"タグ: {', '.join(tags)}")

        # Add success patterns
        if success_patterns := memo_data.get('success_patterns'):
            for pattern in success_patterns:
                if isinstance(pattern, dict):
                    text_parts.append(f"成功: {pattern.get('description', '')}")
                else:
                    text_parts.append(f"成功: {pattern}")

        # Add issues/challenges
        if issues := memo_data.get('issues'):
            for issue in issues:
                if isinstance(issue, dict):
                    text_parts.append(f"課題: {issue.get('description', '')}")
                else:
                    text_parts.append(f"課題: {issue}")

        # Add failure patterns
        if failure_patterns := memo_data.get('failure_patterns'):
            for pattern in failure_patterns:
                if isinstance(pattern, dict):
                    text_parts.append(f"失敗: {pattern.get('symptom', '')}")
                else:
                    text_parts.append(f"失敗: {pattern}")

        # Add next actions
        if next_actions := memo_data.get('next_actions'):
            for action in next_actions:
                if isinstance(action, dict):
                    text_parts.append(f"次回: {action.get('theme', '')}")
                else:
                    text_parts.append(f"次回: {action}")

        # Add raw text if available
        if raw_text := memo_data.get('raw_text'):
            text_parts.append(f"本文: {raw_text}")

        # Combine all parts
        combined_text = "\n".join(text_parts)

        if not combined_text.strip():
            raise ValueError("No valid text found in memo_data")

        return await self.get_embedding(combined_text)


# Global instance (lazy initialization)
_embedding_generator: Optional[EmbeddingGenerator] = None


def get_embedding_generator() -> EmbeddingGenerator:
    """
    Get global EmbeddingGenerator instance (singleton pattern).

    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
