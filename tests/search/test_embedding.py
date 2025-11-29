"""
Tests for the embedding generation module.
"""
import pytest
import asyncio
from src.search.embedding import EmbeddingGenerator, get_embedding_generator


@pytest.mark.asyncio
async def test_get_embedding():
    """Test basic embedding generation."""
    generator = get_embedding_generator()

    text = "今日はサーブの練習をした。トスが安定していて良かった。"
    embedding = await generator.get_embedding(text)

    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_get_query_embedding():
    """Test query embedding generation."""
    generator = get_embedding_generator()

    query = "サーブのコツ"
    embedding = await generator.get_query_embedding(query)

    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0


@pytest.mark.asyncio
async def test_batch_embed_texts():
    """Test batch embedding generation."""
    generator = get_embedding_generator()

    texts = [
        "サーブの練習",
        "フォアハンドの改善",
        "バックハンドの課題"
    ]

    embeddings = await generator.batch_embed_texts(texts, delay=0.1)

    assert len(embeddings) == len(texts)
    assert all(e is not None for e in embeddings)


@pytest.mark.asyncio
async def test_embed_memo_content():
    """Test embedding generation from memo data."""
    generator = get_embedding_generator()

    memo_data = {
        "summary": "サーブの練習",
        "tags": ["serve", "practice"],
        "success_patterns": [
            {"description": "トスが安定していた"}
        ],
        "issues": [
            {"description": "2ndサーブが弱い"}
        ],
        "next_actions": [
            {"theme": "2ndサーブの強化"}
        ]
    }

    embedding = await generator.embed_memo_content(memo_data)

    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0


@pytest.mark.asyncio
async def test_empty_text_error():
    """Test that empty text raises an error."""
    generator = get_embedding_generator()

    with pytest.raises(ValueError, match="Text cannot be empty"):
        await generator.get_embedding("")


@pytest.mark.asyncio
async def test_empty_memo_error():
    """Test that empty memo data raises an error."""
    generator = get_embedding_generator()

    with pytest.raises(ValueError, match="memo_data cannot be empty"):
        await generator.embed_memo_content({})


@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that get_embedding_generator returns the same instance."""
    generator1 = get_embedding_generator()
    generator2 = get_embedding_generator()

    assert generator1 is generator2
