"""
Standalone Content Ingestion Script

Runs the complete ingestion pipeline from command line.

Usage:
    python scripts/run_ingestion.py [--force-reindex] [--docs-path PATH]

Constitution: backend/.specify/memory/constitution.md (Section 6)
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ingestion import ingestion_service
from app.services.qdrant import qdrant_service
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run ingestion pipeline."""
    parser = argparse.ArgumentParser(
        description="Ingest course content into Qdrant vector database"
    )
    parser.add_argument(
        '--force-reindex',
        action='store_true',
        help="Delete existing collection and re-index from scratch"
    )
    parser.add_argument(
        '--docs-path',
        type=str,
        default=None,
        help=f"Path to docs folder (default: {settings.DOCS_PATH})"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("RAG Chatbot Content Ingestion")
    logger.info("=" * 60)
    logger.info(f"Docs path: {args.docs_path or settings.DOCS_PATH}")
    logger.info(f"Force reindex: {args.force_reindex}")
    logger.info(f"Chunk size: {settings.MAX_CHUNK_SIZE} tokens")
    logger.info(f"Chunk overlap: {settings.CHUNK_OVERLAP} tokens")
    logger.info(f"Embedding model: {settings.EMBEDDING_MODEL_NAME}")
    logger.info("=" * 60)

    try:
        # Ensure Qdrant collection exists
        if not args.force_reindex:
            logger.info("Ensuring Qdrant collection exists...")
            qdrant_service.create_collection()

        # Run ingestion
        result = await ingestion_service.run_full_ingestion(
            docs_path=args.docs_path,
            force_reindex=args.force_reindex
        )

        # Print results
        logger.info("=" * 60)
        logger.info("Ingestion Results")
        logger.info("=" * 60)
        logger.info(f"Status: {result['status'].upper()}")
        logger.info(f"Chunks ingested: {result['chunks_ingested']}")
        logger.info(f"Duration: {result['duration_seconds']}s")

        if result['errors']:
            logger.warning(f"Errors encountered: {len(result['errors'])}")
            for error in result['errors']:
                logger.warning(f"  - {error}")

        logger.info("=" * 60)

        # Exit code based on status
        if result['status'] == 'success':
            logger.info("✓ Ingestion completed successfully!")
            return 0
        elif result['status'] == 'partial_success':
            logger.warning("⚠ Ingestion completed with some errors")
            return 1
        else:
            logger.error("✗ Ingestion failed")
            return 2

    except KeyboardInterrupt:
        logger.warning("\nIngestion interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
