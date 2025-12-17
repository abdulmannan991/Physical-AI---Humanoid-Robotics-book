"""
Validation Utilities

Provides URL validation and text sanitization.

Constitution: backend/.specify/memory/constitution.md (Section 5.3)
"""

import re
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise

    Constitution Reference: FR-028 (Citation URL validation)
    """
    if not url:
        return False

    try:
        # Parse URL
        result = urlparse(url)

        # Check basic validity
        if not result.scheme and not result.path:
            return False

        # For relative URLs (like /docs/...), path must start with /
        if not result.scheme:
            return result.path.startswith('/')

        # For absolute URLs, scheme must be http or https
        if result.scheme and result.scheme not in ['http', 'https']:
            return False

        return True

    except Exception as e:
        logger.warning(f"URL validation failed for '{url}': {e}")
        return False


def validate_docusaurus_url(url: str) -> bool:
    """
    Validate that URL is a valid Docusaurus path.

    Args:
        url: URL to validate

    Returns:
        True if valid Docusaurus URL, False otherwise

    Constitution Reference: FR-009 (Citations must link to course content)
    """
    if not url:
        return False

    # Must start with /docs/
    if not url.startswith('/docs/'):
        return False

    # Should not contain query parameters or fragments (for simplicity)
    if '?' in url or '#' in url:
        # Allow fragments for section links
        if '#' in url:
            url = url.split('#')[0]
        if '?' in url:
            return False

    # Should not have file extension
    if url.endswith(('.md', '.mdx', '.html')):
        return False

    # Should not have spaces or special characters (except - and /)
    if not re.match(r'^/docs/[\w\-/]+$', url):
        return False

    return True


def sanitize_text(text: str) -> str:
    """
    Sanitize text for safe display (prevent XSS).

    Args:
        text: Raw text input

    Returns:
        Sanitized text

    Constitution Reference: Section 5.3 (Input sanitization)

    Note: More comprehensive sanitization is in core/security.py.
    This is a lightweight version for use in utilities.
    """
    if not text:
        return ""

    # Remove null bytes
    sanitized = text.replace('\x00', '')

    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_markdown_path(path: str) -> bool:
    """
    Validate that path is a valid Markdown file path.

    Args:
        path: File path to validate

    Returns:
        True if valid Markdown path, False otherwise

    Constitution Reference: Section 6 (Content ingestion)
    """
    if not path:
        return False

    # Must end with .md or .mdx
    if not (path.endswith('.md') or path.endswith('.mdx')):
        return False

    # Should not contain dangerous patterns
    dangerous_patterns = [
        '..',  # Directory traversal
        '~',   # Home directory
        '$',   # Environment variables
    ]

    for pattern in dangerous_patterns:
        if pattern in path:
            return False

    return True


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to append if truncated (default: "...")

    Returns:
        Truncated text

    Example:
        >>> truncate_text("Hello world", 8)
        "Hello..."
    """
    if not text or len(text) <= max_length:
        return text

    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix


def extract_keywords(text: str, max_keywords: int = 5) -> list[str]:
    """
    Extract keywords from text (simple extraction).

    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to extract

    Returns:
        List of keywords

    Note: This is a simple implementation. For production, consider using
    more sophisticated NLP techniques (e.g., TF-IDF, RAKE).
    """
    # Remove punctuation and convert to lowercase
    clean_text = re.sub(r'[^\w\s]', '', text.lower())

    # Split into words
    words = clean_text.split()

    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }

    # Filter and count
    word_counts = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, _ in sorted_words[:max_keywords]]

    return keywords
