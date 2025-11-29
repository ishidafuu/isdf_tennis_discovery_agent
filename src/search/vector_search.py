"""
Vector search module using ChromaDB for semantic similarity search.

This module provides functionality to store and query embeddings using
ChromaDB as a local vector database.
"""
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not installed. Run: pip install chromadb")

from src.search.embedding import get_embedding_generator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorSearchEngine:
    """Vector search engine using ChromaDB for semantic similarity."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize Vector Search Engine.

        Args:
            persist_directory: Directory to persist ChromaDB data

        Raises:
            ImportError: If ChromaDB is not installed
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is required for vector search. "
                "Install it with: pip install chromadb"
            )

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="tennis_memos",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

        # Initialize embedding generator
        self.embedding_generator = get_embedding_generator()

        logger.info(f"✅ Vector search initialized (DB: {self.persist_directory})")

    def add_memo(
        self,
        memo_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        document: str
    ) -> None:
        """
        Add a memo to the vector database.

        Args:
            memo_id: Unique identifier for the memo
            embedding: Embedding vector
            metadata: Metadata dictionary (e.g., date, scene, user_id, tags)
            document: Original text content

        Raises:
            ValueError: If any required parameter is invalid
        """
        if not memo_id:
            raise ValueError("memo_id cannot be empty")
        if not embedding:
            raise ValueError("embedding cannot be empty")
        if not document:
            raise ValueError("document cannot be empty")

        try:
            self.collection.add(
                ids=[memo_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[document]
            )
            logger.info(f"✅ Added memo to vector DB: {memo_id}")
        except Exception as e:
            logger.error(f"❌ Failed to add memo {memo_id}: {e}")
            raise

    def add_memos_batch(
        self,
        memo_ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        documents: List[str]
    ) -> None:
        """
        Add multiple memos to the vector database in a batch.

        Args:
            memo_ids: List of unique identifiers
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            documents: List of original text contents

        Raises:
            ValueError: If list lengths don't match or any parameter is invalid
        """
        if not (len(memo_ids) == len(embeddings) == len(metadatas) == len(documents)):
            raise ValueError("All lists must have the same length")

        try:
            self.collection.add(
                ids=memo_ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info(f"✅ Added {len(memo_ids)} memos to vector DB")
        except Exception as e:
            logger.error(f"❌ Failed to add batch: {e}")
            raise

    def update_memo(
        self,
        memo_id: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        document: Optional[str] = None
    ) -> None:
        """
        Update an existing memo in the vector database.

        Args:
            memo_id: Unique identifier for the memo
            embedding: New embedding vector (optional)
            metadata: New metadata (optional)
            document: New document text (optional)

        Raises:
            ValueError: If memo_id is empty
        """
        if not memo_id:
            raise ValueError("memo_id cannot be empty")

        try:
            self.collection.update(
                ids=[memo_id],
                embeddings=[embedding] if embedding else None,
                metadatas=[metadata] if metadata else None,
                documents=[document] if document else None
            )
            logger.info(f"✅ Updated memo in vector DB: {memo_id}")
        except Exception as e:
            logger.error(f"❌ Failed to update memo {memo_id}: {e}")
            raise

    def delete_memo(self, memo_id: str) -> None:
        """
        Delete a memo from the vector database.

        Args:
            memo_id: Unique identifier for the memo

        Raises:
            ValueError: If memo_id is empty
        """
        if not memo_id:
            raise ValueError("memo_id cannot be empty")

        try:
            self.collection.delete(ids=[memo_id])
            logger.info(f"✅ Deleted memo from vector DB: {memo_id}")
        except Exception as e:
            logger.error(f"❌ Failed to delete memo {memo_id}: {e}")
            raise

    async def search_similar_memos(
        self,
        query: str,
        limit: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memos using semantic similarity.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            where: Optional metadata filter (e.g., {"scene": "壁打ち", "date": {"$gte": "2025-01"}})

        Returns:
            List of dictionaries containing:
                - id: Memo ID
                - document: Original text
                - metadata: Memo metadata
                - distance: Similarity distance (lower = more similar)

        Raises:
            ValueError: If query is empty or search fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            # Generate query embedding
            query_embedding = await self.embedding_generator.get_query_embedding(query)

            # Perform vector search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where
            )

            # Format results
            memos = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    memos.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })

            logger.info(f"🔍 Found {len(memos)} similar memos for query: '{query[:50]}...'")
            return memos

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise ValueError(f"Failed to search similar memos: {e}")

    async def search_by_embedding(
        self,
        embedding: List[float],
        limit: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memos using a pre-computed embedding vector.

        Args:
            embedding: Query embedding vector
            limit: Maximum number of results to return
            where: Optional metadata filter

        Returns:
            List of similar memos

        Raises:
            ValueError: If embedding is empty or search fails
        """
        if not embedding:
            raise ValueError("Embedding cannot be empty")

        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit,
                where=where
            )

            # Format results
            memos = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    memos.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })

            return memos

        except Exception as e:
            logger.error(f"❌ Search by embedding failed: {e}")
            raise ValueError(f"Failed to search by embedding: {e}")

    def get_memo(self, memo_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memo by ID.

        Args:
            memo_id: Unique identifier for the memo

        Returns:
            Dictionary containing memo data, or None if not found
        """
        try:
            result = self.collection.get(ids=[memo_id])

            if result['ids']:
                return {
                    "id": result['ids'][0],
                    "document": result['documents'][0],
                    "metadata": result['metadatas'][0],
                    "embedding": result['embeddings'][0] if result.get('embeddings') else None
                }

            return None

        except Exception as e:
            logger.error(f"❌ Failed to get memo {memo_id}: {e}")
            return None

    def count_memos(self, where: Optional[Dict[str, Any]] = None) -> int:
        """
        Count the number of memos in the database.

        Args:
            where: Optional metadata filter

        Returns:
            Number of memos
        """
        try:
            if where:
                result = self.collection.get(where=where)
                return len(result['ids'])
            else:
                return self.collection.count()
        except Exception as e:
            logger.error(f"❌ Failed to count memos: {e}")
            return 0

    def clear_all(self) -> None:
        """
        Clear all memos from the database.

        WARNING: This operation is irreversible!
        """
        try:
            # Delete the collection
            self.client.delete_collection("tennis_memos")

            # Recreate empty collection
            self.collection = self.client.get_or_create_collection(
                name="tennis_memos",
                metadata={"hnsw:space": "cosine"}
            )

            logger.warning("⚠️  All memos cleared from vector DB")
        except Exception as e:
            logger.error(f"❌ Failed to clear database: {e}")
            raise


# Global instance (lazy initialization)
_vector_search_engine: Optional[VectorSearchEngine] = None


def get_vector_search_engine(persist_directory: str = "./chroma_db") -> VectorSearchEngine:
    """
    Get global VectorSearchEngine instance (singleton pattern).

    Args:
        persist_directory: Directory to persist ChromaDB data

    Returns:
        VectorSearchEngine instance
    """
    global _vector_search_engine
    if _vector_search_engine is None:
        _vector_search_engine = VectorSearchEngine(persist_directory)
    return _vector_search_engine
