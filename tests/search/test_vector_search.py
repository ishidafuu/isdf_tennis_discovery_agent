"""
Tests for the vector search module.

Note: These tests require ChromaDB to be installed.
Run: pip install chromadb
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

try:
    from src.search.vector_search import VectorSearchEngine, get_vector_search_engine
    from src.search.embedding import get_embedding_generator
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for test database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="ChromaDB not installed")
class TestVectorSearchEngine:
    """Test suite for VectorSearchEngine."""

    @pytest.mark.asyncio
    async def test_add_memo(self, temp_db_dir):
        """Test adding a memo to the vector database."""
        engine = VectorSearchEngine(persist_directory=temp_db_dir)
        generator = get_embedding_generator()

        text = "今日はサーブの練習をした"
        embedding = await generator.get_embedding(text)

        engine.add_memo(
            memo_id="test-001",
            embedding=embedding,
            metadata={"date": "2025-01-01", "scene": "壁打ち"},
            document=text
        )

        # Verify memo was added
        memo = engine.get_memo("test-001")
        assert memo is not None
        assert memo["document"] == text

    @pytest.mark.asyncio
    async def test_search_similar_memos(self, temp_db_dir):
        """Test semantic similarity search."""
        engine = VectorSearchEngine(persist_directory=temp_db_dir)
        generator = get_embedding_generator()

        # Add test memos
        test_data = [
            ("memo-1", "サーブの練習をした", {"scene": "壁打ち"}),
            ("memo-2", "フォアハンドを改善した", {"scene": "スクール"}),
            ("memo-3", "サーブのトスが良くなった", {"scene": "壁打ち"}),
        ]

        for memo_id, text, metadata in test_data:
            embedding = await generator.get_embedding(text)
            engine.add_memo(memo_id, embedding, metadata, text)

        # Search for similar memos
        results = await engine.search_similar_memos("サーブのコツ", limit=2)

        assert len(results) <= 2
        # First result should be related to serve
        assert "サーブ" in results[0]["document"]

    @pytest.mark.asyncio
    async def test_update_memo(self, temp_db_dir):
        """Test updating a memo."""
        engine = VectorSearchEngine(persist_directory=temp_db_dir)
        generator = get_embedding_generator()

        text = "元のテキスト"
        embedding = await generator.get_embedding(text)
        engine.add_memo("test-001", embedding, {"version": "1"}, text)

        # Update metadata
        engine.update_memo("test-001", metadata={"version": "2"})

        memo = engine.get_memo("test-001")
        assert memo["metadata"]["version"] == "2"

    @pytest.mark.asyncio
    async def test_delete_memo(self, temp_db_dir):
        """Test deleting a memo."""
        engine = VectorSearchEngine(persist_directory=temp_db_dir)
        generator = get_embedding_generator()

        text = "削除テスト"
        embedding = await generator.get_embedding(text)
        engine.add_memo("test-001", embedding, {}, text)

        # Delete memo
        engine.delete_memo("test-001")

        memo = engine.get_memo("test-001")
        assert memo is None

    @pytest.mark.asyncio
    async def test_count_memos(self, temp_db_dir):
        """Test counting memos."""
        engine = VectorSearchEngine(persist_directory=temp_db_dir)
        generator = get_embedding_generator()

        # Add 3 memos
        for i in range(3):
            text = f"メモ {i+1}"
            embedding = await generator.get_embedding(text)
            engine.add_memo(f"memo-{i}", embedding, {}, text)

        count = engine.count_memos()
        assert count == 3

    @pytest.mark.asyncio
    async def test_filter_by_metadata(self, temp_db_dir):
        """Test filtering search results by metadata."""
        engine = VectorSearchEngine(persist_directory=temp_db_dir)
        generator = get_embedding_generator()

        # Add memos with different scenes
        test_data = [
            ("memo-1", "サーブ練習", {"scene": "壁打ち"}),
            ("memo-2", "フォアハンド", {"scene": "スクール"}),
            ("memo-3", "サーブ改善", {"scene": "壁打ち"}),
        ]

        for memo_id, text, metadata in test_data:
            embedding = await generator.get_embedding(text)
            engine.add_memo(memo_id, embedding, metadata, text)

        # Search with filter
        results = await engine.search_similar_memos(
            "サーブ",
            limit=10,
            where={"scene": "壁打ち"}
        )

        assert all(r["metadata"]["scene"] == "壁打ち" for r in results)
