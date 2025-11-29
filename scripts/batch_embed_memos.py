#!/usr/bin/env python3
"""
Batch embedding script for existing practice memos.

This script reads all existing memos from the Obsidian vault and
generates embeddings for them, storing them in the ChromaDB vector database.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import re

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.search.embedding import get_embedding_generator
from src.search.vector_search import get_vector_search_engine
from src.storage.obsidian_manager import ObsidianManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_memo_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from memo filename and content.

    Args:
        file_path: Path to the memo file

    Returns:
        Dictionary containing metadata
    """
    filename = file_path.stem  # Without extension

    # Extract date and scene from filename
    # Format: YYYY-MM-DD-HHMMSS-シーン名.md
    match = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{6})-(.+)', filename)

    if match:
        date = match.group(1)
        time = match.group(2)
        scene = match.group(3)
    else:
        # Fallback: try to extract just date
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        date = date_match.group(1) if date_match else "unknown"
        time = "000000"
        scene = "不明"

    return {
        "date": date,
        "time": time,
        "scene": scene,
        "filename": filename
    }


def extract_tags_from_content(content: str) -> List[str]:
    """
    Extract tags from memo content.

    Args:
        content: Memo content

    Returns:
        List of tags
    """
    tags = []

    # Look for tags in format: #タグ or **タグ:**
    tag_patterns = [
        r'#([a-zA-Z0-9_]+)',  # #tag
        r'\*\*タグ:\*\*\s*(.+)',  # **タグ:** サーブ, フォアハンド
    ]

    for pattern in tag_patterns:
        matches = re.findall(pattern, content)
        tags.extend(matches)

    # Clean and deduplicate
    tags = list(set([t.strip() for t in tags if t.strip()]))

    return tags


async def process_memo_file(
    file_path: Path,
    embedding_generator,
    vector_engine
) -> bool:
    """
    Process a single memo file and add it to the vector database.

    Args:
        file_path: Path to the memo file
        embedding_generator: EmbeddingGenerator instance
        vector_engine: VectorSearchEngine instance

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read memo content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            logger.warning(f"⚠️  Skipping empty file: {file_path.name}")
            return False

        # Extract metadata
        metadata = extract_memo_metadata(file_path)
        tags = extract_tags_from_content(content)
        metadata['tags'] = tags

        # Generate embedding
        embedding = await embedding_generator.get_embedding(content)

        # Create unique ID from filename
        memo_id = file_path.stem

        # Add to vector database
        vector_engine.add_memo(
            memo_id=memo_id,
            embedding=embedding,
            metadata=metadata,
            document=content[:1000]  # First 1000 chars for quick preview
        )

        logger.info(f"✅ Processed: {file_path.name}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to process {file_path.name}: {e}")
        return False


async def batch_embed_all_memos(
    vault_path: str,
    db_path: str = "./chroma_db",
    delay: float = 0.2
):
    """
    Process all memos in the Obsidian vault and generate embeddings.

    Args:
        vault_path: Path to Obsidian vault
        db_path: Path to ChromaDB database
        delay: Delay between API calls (seconds)
    """
    vault_path = Path(vault_path)

    if not vault_path.exists():
        logger.error(f"❌ Vault path does not exist: {vault_path}")
        return

    logger.info(f"📂 Scanning vault: {vault_path}")

    # Find all markdown files
    memo_files = list(vault_path.rglob("*.md"))

    if not memo_files:
        logger.warning("⚠️  No markdown files found in vault")
        return

    logger.info(f"📝 Found {len(memo_files)} memo files")

    # Initialize services
    embedding_generator = get_embedding_generator()
    vector_engine = get_vector_search_engine(persist_directory=db_path)

    logger.info(f"🚀 Starting batch processing...")

    # Process each memo
    success_count = 0
    fail_count = 0

    for i, file_path in enumerate(memo_files, 1):
        logger.info(f"Processing {i}/{len(memo_files)}: {file_path.name}")

        success = await process_memo_file(
            file_path,
            embedding_generator,
            vector_engine
        )

        if success:
            success_count += 1
        else:
            fail_count += 1

        # Add delay to avoid API rate limits
        if i < len(memo_files):
            await asyncio.sleep(delay)

    # Summary
    logger.info("=" * 60)
    logger.info(f"✅ Batch processing completed!")
    logger.info(f"   Success: {success_count} memos")
    logger.info(f"   Failed: {fail_count} memos")
    logger.info(f"   Total: {len(memo_files)} memos")
    logger.info(f"   Database: {db_path}")
    logger.info("=" * 60)


async def main():
    """Main entry point."""
    # Get vault path from environment
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_vault")
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    logger.info("🎾 Tennis Discovery Agent - Batch Embedding Script")
    logger.info(f"Vault: {vault_path}")
    logger.info(f"Database: {db_path}")

    await batch_embed_all_memos(vault_path, db_path)


if __name__ == "__main__":
    asyncio.run(main())
