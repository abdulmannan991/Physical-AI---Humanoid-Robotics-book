"""
Content Ingestion Service

Parses Markdown files, chunks content, generates embeddings, and stores in Qdrant.

Constitution: backend/.specify/memory/constitution.md (Section 6)
"""

import logging
from pathlib import Path
from typing import List, Dict
import glob

from app.core.config import settings
from app.utils.chunking import chunk_markdown
from app.services.embeddings import embeddings_service
from app.services.qdrant import qdrant_service

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Content ingestion service.

    Handles parsing, chunking, embedding, and storing course content.
    """

    def __init__(self):
        """Initialize ingestion service."""
        # Resolve the docs path relative to the backend directory
        # This allows "../docs" to work when running from backend/
        docs_path_raw = settings.DOCS_PATH
        if not Path(docs_path_raw).is_absolute():
            # Get backend directory (where this service runs from)
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.docs_path = str((backend_dir / docs_path_raw).resolve())
        else:
            self.docs_path = docs_path_raw

        self.file_patterns = settings.INGESTION_FILE_PATTERNS.split(",")
        self.exclude_patterns = settings.INGESTION_EXCLUDE_PATTERNS.split(",")
        logger.info(f"Ingestion service initialized (docs_path={self.docs_path})")

    def parse_docs_folder(self, docs_path: str = None) -> List[Dict]:
        """
        Parse all Markdown files in docs folder.

        Args:
            docs_path: Optional custom docs path (defaults to config value)

        Returns:
            List of chunk dictionaries with metadata

        Constitution Reference: Section 6 (Content ingestion from /docs)
        """
        if docs_path is None:
            docs_path = self.docs_path

        all_chunks = []
        parsed_files = 0
        failed_files = []

        try:
            # Find all Markdown files
            md_files = self._find_markdown_files(docs_path)
            logger.info(f"Found {len(md_files)} Markdown files in {docs_path}")

            for md_file in md_files:
                try:
                    # Chunk the file
                    chunks = chunk_markdown(
                        file_path=md_file,
                        max_tokens=settings.MAX_CHUNK_SIZE,
                        overlap=settings.CHUNK_OVERLAP
                    )

                    all_chunks.extend(chunks)
                    parsed_files += 1

                    logger.debug(f"Parsed {md_file}: {len(chunks)} chunks")

                except Exception as e:
                    logger.error(f"Failed to parse {md_file}: {e}")
                    failed_files.append(md_file)

            logger.info(
                f"Parsed {parsed_files} files, {len(all_chunks)} total chunks "
                f"({len(failed_files)} files failed)"
            )

            if failed_files:
                logger.warning(f"Failed files: {failed_files}")

            return all_chunks

        except Exception as e:
            logger.error(f"Failed to parse docs folder: {e}")
            return []

    def _find_markdown_files(self, docs_path: str) -> List[str]:
        """
        Find all Markdown files in docs folder.

        Args:
            docs_path: Path to docs folder

        Returns:
            List of file paths
        """
        md_files = []

        # Search for each pattern
        for pattern in self.file_patterns:
            pattern = pattern.strip()
            search_pattern = f"{docs_path}/**/{pattern}"

            files = glob.glob(search_pattern, recursive=True)
            md_files.extend(files)

        # Filter out excluded patterns
        filtered_files = []
        for file in md_files:
            should_exclude = False
            for exclude_pattern in self.exclude_patterns:
                if exclude_pattern.strip() in file:
                    should_exclude = True
                    break

            if not should_exclude:
                filtered_files.append(file)

        # Deduplicate
        return list(set(filtered_files))

    async def embed_and_store(self, chunks: List[Dict]) -> int:
        """
        Generate embeddings and store chunks in Qdrant.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Number of chunks successfully stored

        Constitution Reference: Section 6 (Idempotent ingestion)

        Note: This operation is idempotent - chunks with same ID will be updated.
        """
        if not chunks:
            logger.warning("No chunks to embed and store")
            return 0

        try:
            # Extract text from chunks for batch embedding
            texts = [chunk["raw_text"] for chunk in chunks]

            logger.info(f"Generating embeddings for {len(texts)} chunks...")

            # Generate embeddings in batch
            embeddings = embeddings_service.generate_embeddings_batch(
                texts=texts,
                input_type="search_document"
            )

            if not embeddings:
                logger.error("Failed to generate embeddings")
                return 0

            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding

            # Store in Qdrant
            logger.info(f"Storing {len(chunks)} chunks in Qdrant...")
            success = qdrant_service.upsert_chunks(chunks)

            if success:
                logger.info(f"Successfully stored {len(chunks)} chunks")
                return len(chunks)
            else:
                logger.error("Failed to store chunks in Qdrant")
                return 0

        except Exception as e:
            logger.error(f"Failed to embed and store chunks: {e}")
            return 0

    async def run_full_ingestion(
        self,
        docs_path: str = None,
        force_reindex: bool = True
    ) -> Dict[str, any]:
        """
        Run complete ingestion pipeline.

        Args:
            docs_path: Optional custom docs path
            force_reindex: If True, delete collection and re-index from scratch (default: True)

        Returns:
            Dictionary with ingestion stats

        Constitution Reference: Section 6 (Content ingestion pipeline)
        """
        import time
        start_time = time.time()

        errors = []

        try:
            # Step 1: Force reindex (always recreate collection to avoid vector size mismatch)
            if force_reindex:
                logger.warning("Force reindex - deleting and recreating collection")
                print("🔄 Recreating Qdrant collection (force reset)...")
                qdrant_service.delete_collection()
                time.sleep(1)  # Give Qdrant time to fully delete
                qdrant_service.create_collection()

            # Step 2: Parse docs folder
            logger.info("Step 1/3: Parsing Markdown files...")
            chunks = self.parse_docs_folder(docs_path)

            if not chunks:
                error_msg = "No chunks parsed from docs folder"
                logger.error(error_msg)
                errors.append(error_msg)
                return {
                    "status": "failed",
                    "chunks_ingested": 0,
                    "duration_seconds": time.time() - start_time,
                    "errors": errors
                }

            logger.info(f"Parsed {len(chunks)} chunks")

            # Step 3: Embed and store
            logger.info("Step 2/3: Generating embeddings...")
            logger.info("Step 3/3: Storing in Qdrant...")
            chunks_stored = await self.embed_and_store(chunks)

            # Calculate results
            duration = time.time() - start_time
            status = "success" if chunks_stored == len(chunks) else "partial_success"

            if chunks_stored < len(chunks):
                errors.append(
                    f"Only {chunks_stored}/{len(chunks)} chunks stored successfully"
                )

            result = {
                "status": status,
                "chunks_ingested": chunks_stored,
                "duration_seconds": round(duration, 2),
                "errors": errors
            }

            logger.info(
                f"Ingestion complete: {result['status']}, "
                f"{result['chunks_ingested']} chunks, "
                f"{result['duration_seconds']}s"
            )

            # Get final collection count for verification
            stats = qdrant_service.get_collection_stats()
            if stats:
                final_count = stats.get('points_count', 0)
                print(f"✅ Total documents in DB: {final_count}")
            else:
                print("⚠️ Could not retrieve collection stats")

            return result

        except Exception as e:
            error_msg = f"Ingestion failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

            return {
                "status": "failed",
                "chunks_ingested": 0,
                "duration_seconds": time.time() - start_time,
                "errors": errors
            }


# Global ingestion service instance
ingestion_service = IngestionService()


async def main():
    """
    Main entry point for running ingestion from command line.

    Usage:
        python -m app.services.ingestion
    """
    print("Ingestion started...")
    print("=" * 60)

    try:
        # Initialize service
        service = IngestionService()

        # Run full ingestion
        result = await service.run_full_ingestion()

        # Display results
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Chunks ingested: {result['chunks_ingested']}")
        print(f"Duration: {result['duration_seconds']}s")

        if result.get('errors'):
            print(f"\nErrors encountered:")
            for error in result['errors']:
                print(f"  - {error}")

        print("=" * 60)
        print("Ingestion complete!")

        # Exit with appropriate status code
        if result['status'] == 'success':
            return 0
        elif result['status'] == 'partial_success':
            print("\nWarning: Partial success - some chunks may not have been ingested")
            return 1
        else:
            print("\nError: Ingestion failed")
            return 1

    except Exception as e:
        print("=" * 60)
        print(f"Fatal error during ingestion: {e}")
        print("=" * 60)
        logger.exception("Fatal error in main()")
        return 1


if __name__ == "__main__":
    import asyncio
    import sys

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
