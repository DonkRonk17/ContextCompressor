#!/usr/bin/env python3
"""
ContextCompressor v0.1 - Smart Context Reduction for AI Agents

Intelligently compress large files/contexts to reduce token usage.
Extract relevant sections, summarize long documents, estimate savings.

Author: Team Brain (Atlas)
License: MIT
"""

import re
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

__version__ = "0.2.0"

# Maximum sizes to prevent resource exhaustion
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_TEXT_SIZE = 50 * 1024 * 1024   # 50 MB

@dataclass
class CompressionResult:
    """Result of a compression operation."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    estimated_token_savings: int
    method: str
    preview: str


class ContextCompressor:
    """
    Smart context compression for AI agents.
    
    Reduces token usage by:
    - Extracting relevant sections from large files
    - Summarizing repetitive content
    - Removing comments/whitespace intelligently
    - Caching frequently-used contexts
    """
    
    # Token estimation: ~4 chars per token (rough average)
    CHARS_PER_TOKEN = 4
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize ContextCompressor.
        
        Args:
            cache_dir: Optional directory for caching compressed contexts
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent / ".context_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Compression stats
        self.stats = {
            "compressions": 0,
            "total_original_tokens": 0,
            "total_compressed_tokens": 0,
            "cache_hits": 0
        }
    
    def _validate_file_path(self, file_path: Path) -> Path:
        """Validate file path for security."""
        file_path = Path(file_path).resolve()
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if it's a file (not directory)
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large ({file_size / 1024 / 1024:.1f} MB). Max: {MAX_FILE_SIZE / 1024 / 1024:.1f} MB")
        
        return file_path
    
    def _validate_method(self, method: str) -> str:
        """Validate compression method."""
        valid_methods = ["auto", "relevant", "summary", "strip"]
        if method not in valid_methods:
            raise ValueError(f"Invalid method '{method}'. Must be one of: {', '.join(valid_methods)}")
        return method
    
    def _validate_text_size(self, text: str) -> str:
        """Validate text size."""
        if len(text) > MAX_TEXT_SIZE:
            raise ValueError(f"Text too large ({len(text) / 1024 / 1024:.1f} MB). Max: {MAX_TEXT_SIZE / 1024 / 1024:.1f} MB")
        return text
    
    def _validate_query(self, query: Optional[str]) -> Optional[str]:
        """Validate and sanitize query."""
        if query is None:
            return None
        if len(query) > 10000:
            raise ValueError(f"Query too long ({len(query)} chars). Max: 10,000 chars")
        return query
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text."""
        return len(text) // self.CHARS_PER_TOKEN
    
    def compress_file(
        self,
        file_path: Path,
        query: Optional[str] = None,
        method: str = "auto"
    ) -> CompressionResult:
        """
        Compress a file for AI context.
        
        Args:
            file_path: Path to file to compress
            query: Optional search query to extract relevant sections
            method: Compression method ("auto", "relevant", "summary", "strip")
        
        Returns:
            CompressionResult with compression details
        """
        # Validate inputs
        file_path = self._validate_file_path(file_path)
        query = self._validate_query(query)
        method = self._validate_method(method)
        
        # Read original content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read file: {e}")
        
        # Validate content size
        original_content = self._validate_text_size(original_content)
        
        original_size = len(original_content)
        original_tokens = self.estimate_tokens(original_content)
        
        # Check cache
        cache_key = self._get_cache_key(file_path, query, method)
        cached = self._get_from_cache(cache_key)
        if cached:
            self.stats["cache_hits"] += 1
            return cached
        
        # Choose compression method
        if method == "auto":
            method = self._choose_method(file_path, original_content, query)
        
        # Compress
        if method == "relevant" and query:
            compressed = self._extract_relevant(original_content, query, file_path)
        elif method == "summary":
            compressed = self._summarize_content(original_content, file_path)
        elif method == "strip":
            compressed = self._strip_unnecessary(original_content, file_path)
        else:
            compressed = original_content  # No compression
        
        compressed_size = len(compressed)
        compressed_tokens = self.estimate_tokens(compressed)
        
        # Calculate metrics
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        token_savings = original_tokens - compressed_tokens
        
        result = CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            estimated_token_savings=token_savings,
            method=method,
            preview=compressed[:200] + "..." if len(compressed) > 200 else compressed
        )
        
        # Update stats
        self.stats["compressions"] += 1
        self.stats["total_original_tokens"] += original_tokens
        self.stats["total_compressed_tokens"] += compressed_tokens
        
        # Cache result
        self._save_to_cache(cache_key, result, compressed)
        
        return result
    
    def compress_text(
        self,
        text: str,
        query: Optional[str] = None,
        method: str = "auto"
    ) -> Tuple[str, CompressionResult]:
        """
        Compress arbitrary text content.
        
        Args:
            text: Text to compress
            query: Optional search query
            method: Compression method
        
        Returns:
            Tuple of (compressed_text, CompressionResult)
        """
        # Validate inputs
        text = self._validate_text_size(text)
        query = self._validate_query(query)
        method = self._validate_method(method)
        original_size = len(text)
        original_tokens = self.estimate_tokens(text)
        
        # Choose method
        if method == "auto":
            if query:
                method = "relevant"
            elif original_size > 10000:
                method = "summary"
            else:
                method = "strip"
        
        # Compress
        if method == "relevant" and query:
            compressed = self._extract_relevant_text(text, query)
        elif method == "summary":
            compressed = self._summarize_text(text)
        elif method == "strip":
            compressed = self._strip_whitespace(text)
        else:
            compressed = text
        
        compressed_size = len(compressed)
        compressed_tokens = self.estimate_tokens(compressed)
        
        result = CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compressed_size / original_size if original_size > 0 else 1.0,
            estimated_token_savings=original_tokens - compressed_tokens,
            method=method,
            preview=compressed[:200] + "..." if len(compressed) > 200 else compressed
        )
        
        self.stats["compressions"] += 1
        self.stats["total_original_tokens"] += original_tokens
        self.stats["total_compressed_tokens"] += compressed_tokens
        
        return compressed, result
    
    def _choose_method(self, file_path: Path, content: str, query: Optional[str]) -> str:
        """Automatically choose best compression method."""
        file_size = len(content)
        
        # If query provided, use relevant extraction
        if query:
            return "relevant"
        
        # For code files, strip comments/whitespace
        if file_path.suffix in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs']:
            return "strip"
        
        # For large files, summarize
        if file_size > 50000:  # ~12,500 tokens
            return "summary"
        
        # For markdown/text, strip whitespace
        if file_path.suffix in ['.md', '.txt', '.rst']:
            return "strip"
        
        return "strip"
    
    def _extract_relevant(self, content: str, query: str, file_path: Path) -> str:
        """Extract sections relevant to query."""
        query_lower = query.lower()
        lines = content.split('\n')
        
        relevant_sections = []
        context_window = 5  # Lines of context before/after match
        
        # Find matching lines
        matches = []
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                matches.append(i)
        
        if not matches:
            # No exact matches, return summary
            return self._summarize_content(content, file_path)
        
        # Extract with context
        extracted_lines = set()
        for match_idx in matches:
            start = max(0, match_idx - context_window)
            end = min(len(lines), match_idx + context_window + 1)
            for i in range(start, end):
                extracted_lines.add(i)
        
        # Build result
        result_lines = []
        sorted_indices = sorted(extracted_lines)
        
        last_idx = -2
        for idx in sorted_indices:
            if idx != last_idx + 1:
                result_lines.append(f"\n... (skipped {idx - last_idx - 1} lines) ...\n")
            result_lines.append(lines[idx])
            last_idx = idx
        
        return '\n'.join(result_lines)
    
    def _extract_relevant_text(self, text: str, query: str) -> str:
        """Extract relevant sections from arbitrary text."""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        query_lower = query.lower()
        
        # Find relevant paragraphs
        relevant = []
        for para in paragraphs:
            if query_lower in para.lower():
                relevant.append(para)
        
        if not relevant:
            # Return first few paragraphs as fallback
            return '\n\n'.join(paragraphs[:3])
        
        return '\n\n'.join(relevant)
    
    def _summarize_content(self, content: str, file_path: Path) -> str:
        """Summarize file content (basic implementation)."""
        lines = content.split('\n')
        
        # For code files, extract signatures/docstrings
        if file_path.suffix in ['.py', '.js', '.java']:
            return self._extract_code_structure(content, file_path.suffix)
        
        # For text files, extract headers/key lines
        summary_lines = []
        for line in lines[:50]:  # First 50 lines
            if line.strip():
                summary_lines.append(line)
        
        if len(lines) > 50:
            summary_lines.append(f"\n... (truncated {len(lines) - 50} lines) ...")
        
        return '\n'.join(summary_lines)
    
    def _summarize_text(self, text: str) -> str:
        """Summarize arbitrary text."""
        paragraphs = text.split('\n\n')
        
        # Keep first paragraph and any short paragraphs (likely headers)
        summary = [paragraphs[0]] if paragraphs else []
        
        for para in paragraphs[1:]:
            if len(para) < 200:  # Short paragraphs likely important
                summary.append(para)
        
        return '\n\n'.join(summary)
    
    def _extract_code_structure(self, content: str, file_ext: str) -> str:
        """Extract code structure (functions, classes, docstrings)."""
        lines = content.split('\n')
        structure = []
        
        if file_ext == '.py':
            # Extract class/function definitions and docstrings
            in_docstring = False
            for line in lines:
                stripped = line.strip()
                
                # Class/function definitions
                if stripped.startswith('class ') or stripped.startswith('def '):
                    structure.append(line)
                    in_docstring = True
                # Docstrings
                elif in_docstring and ('"""' in line or "'''" in line):
                    structure.append(line)
                    if line.count('"""') == 2 or line.count("'''") == 2:
                        in_docstring = False
                elif in_docstring:
                    structure.append(line)
        
        return '\n'.join(structure) if structure else content[:1000]
    
    def _strip_unnecessary(self, content: str, file_path: Path) -> str:
        """Strip comments, excessive whitespace."""
        if file_path.suffix == '.py':
            return self._strip_python(content)
        elif file_path.suffix == '.js':
            return self._strip_javascript(content)
        else:
            return self._strip_whitespace(content)
    
    def _strip_python(self, content: str) -> str:
        """Strip Python comments and docstrings."""
        lines = content.split('\n')
        stripped = []
        
        in_docstring = False
        docstring_char = None
        
        for line in lines:
            stripped_line = line.rstrip()
            
            # Check for docstrings
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    docstring_char = '"""' if '"""' in line else "'''"
                    in_docstring = True
                    if line.count(docstring_char) == 2:
                        in_docstring = False
                    continue
                else:
                    in_docstring = False
                    continue
            
            if in_docstring:
                continue
            
            # Remove comments
            if '#' in stripped_line:
                code_part = stripped_line.split('#')[0].rstrip()
                if code_part:
                    stripped.append(code_part)
            elif stripped_line:
                stripped.append(stripped_line)
        
        return '\n'.join(stripped)
    
    def _strip_javascript(self, content: str) -> str:
        """Strip JavaScript comments."""
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return self._strip_whitespace(content)
    
    def _strip_whitespace(self, text: str) -> str:
        """Strip excessive whitespace."""
        # Remove multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove trailing whitespace
        lines = [line.rstrip() for line in text.split('\n')]
        return '\n'.join(lines)
    
    def _get_cache_key(self, file_path: Path, query: Optional[str], method: str) -> str:
        """Generate cache key for compression."""
        key_parts = [str(file_path), query or "", method]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[CompressionResult]:
        """Retrieve from cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return CompressionResult(**data)
            except Exception:
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, result: CompressionResult, compressed_content: str):
        """Save to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(result.__dict__, f)
            
            # Save compressed content
            content_file = self.cache_dir / f"{cache_key}.txt"
            with open(content_file, 'w') as f:
                f.write(compressed_content)
        except Exception:
            pass  # Cache failure is non-critical
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        if self.stats["total_original_tokens"] > 0:
            overall_savings = (
                (self.stats["total_original_tokens"] - self.stats["total_compressed_tokens"]) /
                self.stats["total_original_tokens"] * 100
            )
        else:
            overall_savings = 0.0
        
        return {
            **self.stats,
            "overall_compression_percent": overall_savings,
            "cache_hit_rate": (
                self.stats["cache_hits"] / self.stats["compressions"] * 100
                if self.stats["compressions"] > 0 else 0.0
            )
        }
    
    def clear_cache(self):
        """Clear compression cache."""
        for cache_file in self.cache_dir.glob("*"):
            cache_file.unlink()
        print(f"[OK] Cache cleared: {self.cache_dir}")


def main():
    """CLI interface for ContextCompressor."""
    import sys
    
    if len(sys.argv) < 2:
        print("""
ContextCompressor v0.1 - Smart Context Reduction

USAGE:
  contextcompressor.py compress <file> [--query "search term"] [--method auto|relevant|summary|strip]
  contextcompressor.py estimate <file>
  contextcompressor.py stats
  contextcompressor.py clear-cache

EXAMPLES:
  # Compress a file
  contextcompressor.py compress large_file.py
  
  # Extract relevant sections
  contextcompressor.py compress large_file.py --query "login function"
  
  # Estimate token savings
  contextcompressor.py estimate large_file.py
  
  # View statistics
  contextcompressor.py stats

METHODS:
  auto      - Automatically choose best method (default)
  relevant  - Extract sections relevant to query
  summary   - Summarize content (good for large files)
  strip     - Remove comments/whitespace
""")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    compressor = ContextCompressor()
    
    if command == "compress":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: contextcompressor.py compress <file> [--query \"text\"] [--method auto]")
            sys.exit(1)
        
        file_path = Path(sys.argv[2])
        query = None
        method = "auto"
        
        # Parse optional arguments
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--query" and i + 1 < len(sys.argv):
                query = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--method" and i + 1 < len(sys.argv):
                method = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        result = compressor.compress_file(file_path, query, method)
        
        print(f"\n=== COMPRESSION RESULT ===")
        print(f"File: {file_path}")
        print(f"Method: {result.method}")
        print(f"Original: {result.original_size:,} chars (~{result.original_size // compressor.CHARS_PER_TOKEN:,} tokens)")
        print(f"Compressed: {result.compressed_size:,} chars (~{result.compressed_size // compressor.CHARS_PER_TOKEN:,} tokens)")
        print(f"Ratio: {result.compression_ratio:.1%}")
        print(f"Token Savings: ~{result.estimated_token_savings:,} tokens")
        print(f"\nPreview:\n{result.preview}")
    
    elif command == "estimate":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: contextcompressor.py estimate <file>")
            sys.exit(1)
        
        file_path = Path(sys.argv[2])
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        tokens = compressor.estimate_tokens(content)
        print(f"\n=== TOKEN ESTIMATE ===")
        print(f"File: {file_path}")
        print(f"Size: {len(content):,} chars")
        print(f"Estimated Tokens: ~{tokens:,}")
        print(f"Estimated Cost (Sonnet 4.5 input): ${tokens / 1_000_000 * 3:.4f}")
    
    elif command == "stats":
        stats = compressor.get_stats()
        print(f"\n=== COMPRESSION STATISTICS ===")
        print(f"Total Compressions: {stats['compressions']}")
        print(f"Original Tokens: {stats['total_original_tokens']:,}")
        print(f"Compressed Tokens: {stats['total_compressed_tokens']:,}")
        print(f"Overall Savings: {stats['overall_compression_percent']:.1f}%")
        print(f"Cache Hits: {stats['cache_hits']}")
        print(f"Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
    
    elif command == "clear-cache":
        compressor.clear_cache()
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
