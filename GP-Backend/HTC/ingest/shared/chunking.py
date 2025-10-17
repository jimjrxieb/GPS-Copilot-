#!/usr/bin/env python3
"""
Chunking Strategies
===================

Different chunking strategies for different knowledge types.
"""

from typing import List, Dict, Any
import re


class Chunker:
    """Chunk text based on strategy"""

    STRATEGIES = {
        "large": {
            "size": 1000,  # tokens (approx 750 words)
            "overlap": 200,
            "description": "For business context (meetings, sessions)"
        },
        "medium": {
            "size": 600,   # tokens (approx 450 words)
            "overlap": 100,
            "description": "For project documentation"
        },
        "small": {
            "size": 400,   # tokens (approx 300 words)
            "overlap": 50,
            "description": "For technical knowledge (Q&A, commands)"
        }
    }

    def __init__(self, strategy: str = "medium"):
        """
        Initialize chunker with strategy.

        Args:
            strategy: "large", "medium", or "small"
        """
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Invalid strategy. Choose from: {list(self.STRATEGIES.keys())}")

        self.strategy = strategy
        self.config = self.STRATEGIES[strategy]

    def chunk_by_tokens(self, text: str) -> List[str]:
        """
        Chunk text by approximate token count.

        Note: This is a simple word-based approximation.
        1 token ≈ 0.75 words for English text.
        """
        # Convert token count to word count
        words_per_chunk = int(self.config["size"] * 0.75)
        overlap_words = int(self.config["overlap"] * 0.75)

        # Split into words
        words = text.split()

        chunks = []
        i = 0
        while i < len(words):
            # Get chunk
            chunk_words = words[i:i + words_per_chunk]
            chunks.append(" ".join(chunk_words))

            # Move forward (with overlap)
            i += words_per_chunk - overlap_words

        return chunks

    def chunk_by_sections(self, text: str) -> List[str]:
        """
        Chunk by markdown sections (preserves structure).

        Better for documentation with clear sections.
        """
        # Split by markdown headers
        sections = re.split(r'\n(#{1,6}\s+.+)', text)

        chunks = []
        current_chunk = ""
        current_size = 0
        max_size = int(self.config["size"] * 0.75)  # words

        for section in sections:
            section_words = len(section.split())

            # If adding this section would exceed max size, save current chunk
            if current_size + section_words > max_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = section
                current_size = section_words
            else:
                current_chunk += "\n" + section
                current_size += section_words

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_text(self, text: str, preserve_structure: bool = False) -> List[str]:
        """
        Chunk text using configured strategy.

        Args:
            text: Text to chunk
            preserve_structure: If True, chunk by sections (markdown). Otherwise by tokens.

        Returns:
            List of text chunks
        """
        if preserve_structure:
            return self.chunk_by_sections(text)
        else:
            return self.chunk_by_tokens(text)


# Quick test
if __name__ == "__main__":
    test_text = """
# Introduction

This is a test document with multiple sections.

## Section 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section 2

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

## Section 3

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
"""

    print("Testing SMALL strategy (400 tokens):")
    chunker = Chunker("small")
    chunks = chunker.chunk_text(test_text, preserve_structure=True)
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i} ({len(chunk.split())} words):")
        print(chunk[:100] + "...")

    print("\n" + "="*60)
    print("Testing LARGE strategy (1000 tokens):")
    chunker = Chunker("large")
    chunks = chunker.chunk_text(test_text, preserve_structure=True)
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i} ({len(chunk.split())} words):")
        print(chunk[:100] + "...")
