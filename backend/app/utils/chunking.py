"""
Text Chunking Utility

Intelligently chunks Markdown content for RAG while preserving metadata.

Constitution: backend/.specify/memory/constitution.md (Section 6)
"""

import re
import logging
from typing import List, Dict, Optional
from pathlib import Path
import frontmatter

logger = logging.getLogger(__name__)


def chunk_markdown(
    file_path: str,
    max_tokens: int = 512,
    overlap: int = 50
) -> List[Dict]:
    """
    Chunk a Markdown file into smaller pieces with metadata preservation.

    Args:
        file_path: Path to Markdown file
        max_tokens: Maximum tokens per chunk (default: 512)
        overlap: int = 50

    Returns:
        List of chunk dictionaries with metadata

    Constitution Reference: Section 6 (Intelligent chunking with metadata)

    Each chunk dict contains:
    - chunk_id: str (UUID)
    - source_file: str (relative path)
    - chapter: str (from frontmatter or inferred)
    - section: str (heading where chunk belongs)
    - url: str (derived from file path)
    - raw_text: str (chunk content)
    - token_count: int (approximate)
    """
    try:
        # Read file with frontmatter
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        content = post.content
        metadata = post.metadata

        # Extract metadata
        chapter = metadata.get('title', metadata.get('sidebar_label', 'Unknown Chapter'))
        base_url = _file_path_to_url(file_path)

        # Split by headings (## level)
        sections = _split_by_headings(content)

        # Chunk each section
        all_chunks = []
        for section_title, section_text in sections:
            section_chunks = _chunk_text(
                text=section_text,
                max_tokens=max_tokens,
                overlap=overlap
            )

            for chunk_text in section_chunks:
                chunk = {
                    "chunk_id": str(_generate_chunk_id(file_path, section_title, chunk_text)),
                    "source_file": _get_relative_path(file_path),
                    "chapter": chapter,
                    "section": section_title or chapter,
                    "url": base_url,
                    "raw_text": chunk_text,
                    "token_count": _estimate_tokens(chunk_text)
                }
                all_chunks.append(chunk)

        logger.info(f"Chunked {file_path}: {len(all_chunks)} chunks")
        return all_chunks

    except Exception as e:
        logger.error(f"Failed to chunk {file_path}: {e}")
        return []


def _split_by_headings(content: str) -> List[tuple[str, str]]:
    """
    Split Markdown content by ## headings.

    Args:
        content: Markdown content

    Returns:
        List of (section_title, section_text) tuples
    """
    # Pattern for ## headings
    heading_pattern = re.compile(r'^##\s+(.+)$', re.MULTILINE)

    sections = []
    matches = list(heading_pattern.finditer(content))

    if not matches:
        # No headings found - treat whole content as one section
        return [("", content)]

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()

        # Find end of section (next heading or end of content)
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)

        section_text = content[start:end].strip()
        sections.append((title, section_text))

    return sections


def _chunk_text(
    text: str,
    max_tokens: int,
    overlap: int
) -> List[str]:
    """
    Chunk text into smaller pieces with overlap.

    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Token overlap between chunks

    Returns:
        List of text chunks
    """
    # Split by paragraphs (double newline)
    paragraphs = re.split(r'\n\n+', text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for paragraph in paragraphs:
        para_tokens = _estimate_tokens(paragraph)

        # If single paragraph exceeds max_tokens, split it
        if para_tokens > max_tokens:
            # Save current chunk if not empty
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0

            # Split large paragraph by sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                sent_tokens = _estimate_tokens(sentence)
                if current_tokens + sent_tokens > max_tokens:
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_tokens = sent_tokens
                else:
                    current_chunk.append(sentence)
                    current_tokens += sent_tokens
            continue

        # Add paragraph to current chunk
        if current_tokens + para_tokens > max_tokens:
            # Save current chunk and start new one
            chunks.append('\n\n'.join(current_chunk))

            # Add overlap from previous chunk
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-1]  # Last paragraph
                current_chunk = [overlap_text, paragraph]
                current_tokens = _estimate_tokens(overlap_text) + para_tokens
            else:
                current_chunk = [paragraph]
                current_tokens = para_tokens
        else:
            current_chunk.append(paragraph)
            current_tokens += para_tokens

    # Add final chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def _estimate_tokens(text: str) -> int:
    """
    Estimate number of tokens (rough approximation).

    Args:
        text: Text to estimate

    Returns:
        Estimated token count

    Note: This is a rough estimate. For precise counting, use tiktoken.
    """
    # Rough approximation: 1 token ≈ 4 characters for English
    return len(text) // 4


def _generate_chunk_id(file_path: str, section: str, text: str) -> str:
    """
    Generate deterministic chunk ID from file path, section, and text hash.

    Args:
        file_path: Source file path
        section: Section title
        text: Chunk text

    Returns:
        Chunk ID (first 100 chars of text used as simple hash)
    """
    import hashlib
    import uuid

    # Create hash from file path + section + text
    content = f"{file_path}:{section}:{text[:100]}"
    hash_digest = hashlib.md5(content.encode()).hexdigest()

    # Convert to UUID format
    return str(uuid.UUID(hash_digest))


def _get_relative_path(file_path: str) -> str:
    """
    Get relative path from project root for source file tracking.

    Args:
        file_path: Absolute or relative file path

    Returns:
        Path relative to project root (one level up from backend)

    Example:
        /absolute/path/to/project/docs/intro.md → docs/intro.md
        ../docs/intro.md → docs/intro.md
    """
    path = Path(file_path).resolve()

    # Project root is one level up from backend directory
    # backend directory is where this code runs (contains app/)
    backend_dir = Path(__file__).resolve().parent.parent.parent
    project_root = backend_dir.parent

    try:
        # Try to get path relative to project root
        relative_path = path.relative_to(project_root)
        return str(relative_path)
    except ValueError:
        # If file is outside project root, just use the file name
        # This shouldn't happen in normal operation
        logger.warning(f"File {file_path} is outside project root, using filename only")
        return path.name


def _file_path_to_url(file_path: str) -> str:
    """
    Convert file path to Docusaurus URL.

    Args:
        file_path: File system path to .md file

    Returns:
        URL path for Docusaurus

    Example:
        docs/01-intro/perception-action-loop.md → /docs/01-intro/perception-action-loop
    """
    path = Path(file_path)

    # Get path relative to docs folder
    try:
        # Find 'docs' in path
        parts = path.parts
        if 'docs' in parts:
            docs_index = parts.index('docs')
            relative_parts = parts[docs_index:]
        else:
            relative_parts = parts

        # Remove .md extension
        url_parts = list(relative_parts)
        if url_parts[-1].endswith('.md') or url_parts[-1].endswith('.mdx'):
            url_parts[-1] = url_parts[-1].rsplit('.', 1)[0]

        # Join with /
        url = '/' + '/'.join(url_parts)
        return url

    except Exception:
        # Fallback: just return filename without extension
        return f"/docs/{path.stem}"
