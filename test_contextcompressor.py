#!/usr/bin/env python3
"""
Comprehensive test suite for ContextCompressor v1.0

Tests cover:
- Core functionality (compression methods)
- Edge cases (empty files, large files, special characters)
- Error handling (invalid inputs, file not found)
- Input validation (security, size limits)
- Python API (file and text compression)
- Statistics and caching

Run: python test_contextcompressor.py

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
Date: January 23, 2026
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from contextcompressor import ContextCompressor, CompressionResult, MAX_FILE_SIZE, MAX_TEXT_SIZE


class TestContextCompressorCore(unittest.TestCase):
    """Test core compression functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_temp_file(self, content: str, filename: str = "test.py") -> Path:
        """Create a temporary file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_initialization(self):
        """Test ContextCompressor initializes correctly."""
        compressor = ContextCompressor()
        self.assertIsNotNone(compressor)
        self.assertIsNotNone(compressor.cache_dir)
        self.assertEqual(compressor.stats["compressions"], 0)
        
    def test_initialization_custom_cache_dir(self):
        """Test initialization with custom cache directory."""
        custom_cache = Path(self.temp_dir) / "custom_cache"
        compressor = ContextCompressor(cache_dir=custom_cache)
        self.assertEqual(compressor.cache_dir, custom_cache)
        self.assertTrue(custom_cache.exists())
        
    def test_estimate_tokens(self):
        """Test token estimation."""
        text = "Hello world!"  # 12 chars
        tokens = self.compressor.estimate_tokens(text)
        self.assertEqual(tokens, 3)  # 12 // 4 = 3
        
    def test_estimate_tokens_empty(self):
        """Test token estimation with empty text."""
        tokens = self.compressor.estimate_tokens("")
        self.assertEqual(tokens, 0)
        
    def test_compress_file_auto_method(self):
        """Test file compression with auto method selection."""
        content = '''def hello():
    """Docstring to strip."""
    # Comment to strip
    return "Hello"

def world():
    """Another docstring."""
    # Another comment
    return "World"
'''
        file_path = self._create_temp_file(content, "test.py")
        result = self.compressor.compress_file(file_path, method="auto")
        
        self.assertIsInstance(result, CompressionResult)
        self.assertGreater(result.original_size, 0)
        self.assertLessEqual(result.compressed_size, result.original_size)
        self.assertEqual(result.method, "strip")  # Python files use strip
        
    def test_compress_file_relevant_method(self):
        """Test file compression with relevant method."""
        # Create a larger file where relevant extraction will reduce size
        content = '''def login_user(username, password):
    return True

def logout_user():
    return True

def process_data_one():
    # This function processes data
    return {"data": "processed"}

def process_data_two():
    # This function also processes data
    return {"data": "processed again"}
    
def process_data_three():
    # Another processing function
    return {"data": "more processing"}

def process_data_four():
    # Yet another processing function
    return {"data": "even more processing"}

def login_admin():
    # Admin login
    return True

def process_final():
    # Final processing
    return {"data": "final"}
'''
        file_path = self._create_temp_file(content, "auth.py")
        result = self.compressor.compress_file(file_path, query="login", method="relevant")
        
        self.assertEqual(result.method, "relevant")
        # Relevant extraction should find login-related sections
        self.assertIn("login", result.preview.lower())
        
    def test_compress_file_summary_method(self):
        """Test file compression with summary method."""
        content = '''# Header Line
Line 1
Line 2
''' + "\n".join([f"Line {i}" for i in range(3, 100)])  # 100 lines total
        
        file_path = self._create_temp_file(content, "large.txt")
        result = self.compressor.compress_file(file_path, method="summary")
        
        self.assertEqual(result.method, "summary")
        self.assertLess(result.compressed_size, result.original_size)
        
    def test_compress_file_strip_method(self):
        """Test file compression with strip method (Python)."""
        content = '''# This is a comment
def hello():
    """This is a docstring that should be removed."""
    # Inline comment
    return "hello"
    
# Another comment
'''
        file_path = self._create_temp_file(content, "code.py")
        result = self.compressor.compress_file(file_path, method="strip")
        
        self.assertEqual(result.method, "strip")
        self.assertLess(result.compressed_size, result.original_size)


class TestContextCompressorTextAPI(unittest.TestCase):
    """Test text compression API."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        
    def test_compress_text_basic(self):
        """Test basic text compression."""
        text = "Hello world.\n\nThis is a test.\n\n\n\nExtra whitespace."
        compressed, result = self.compressor.compress_text(text, method="strip")
        
        self.assertIsInstance(result, CompressionResult)
        self.assertIsInstance(compressed, str)
        self.assertLessEqual(len(compressed), len(text))
        
    def test_compress_text_with_query(self):
        """Test text compression with query extraction."""
        text = """First paragraph about apples.

Second paragraph about oranges and login functionality.

Third paragraph about bananas.

Fourth paragraph with login information and authentication.
"""
        compressed, result = self.compressor.compress_text(text, query="login", method="relevant")
        
        self.assertIn("login", compressed.lower())
        self.assertEqual(result.method, "relevant")
        
    def test_compress_text_summary(self):
        """Test text summarization."""
        text = "Short intro.\n\n" + "\n\n".join(["A" * 500 for _ in range(10)])
        compressed, result = self.compressor.compress_text(text, method="summary")
        
        self.assertEqual(result.method, "summary")
        self.assertLess(len(compressed), len(text))


class TestContextCompressorEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_temp_file(self, content: str, filename: str = "test.txt") -> Path:
        """Create a temporary file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
        
    def test_compress_empty_file(self):
        """Test compression of empty file."""
        file_path = self._create_temp_file("", "empty.txt")
        result = self.compressor.compress_file(file_path)
        
        self.assertEqual(result.original_size, 0)
        self.assertEqual(result.compressed_size, 0)
        
    def test_compress_single_line(self):
        """Test compression of single line file."""
        file_path = self._create_temp_file("Hello", "single.txt")
        result = self.compressor.compress_file(file_path)
        
        self.assertEqual(result.original_size, 5)
        
    def test_compress_whitespace_only(self):
        """Test compression of whitespace-only content."""
        file_path = self._create_temp_file("   \n\n   \n\t\t", "whitespace.txt")
        result = self.compressor.compress_file(file_path)
        
        self.assertIsInstance(result, CompressionResult)
        
    def test_compress_special_characters(self):
        """Test compression with special characters."""
        content = "Hello! @#$%^&*() unicode: \u00e9\u00e8\u00ea test"
        file_path = self._create_temp_file(content, "special.txt")
        result = self.compressor.compress_file(file_path)
        
        self.assertIsInstance(result, CompressionResult)
        
    def test_compress_no_query_matches(self):
        """Test compression when query has no matches."""
        content = "This file contains only text about apples and oranges."
        file_path = self._create_temp_file(content, "nomatch.txt")
        result = self.compressor.compress_file(file_path, query="xyz123nonexistent", method="relevant")
        
        # Should fall back to summary when no matches
        self.assertIsInstance(result, CompressionResult)
        
    def test_compression_ratio_calculation(self):
        """Test compression ratio is calculated correctly."""
        content = "A" * 1000
        file_path = self._create_temp_file(content, "ratio.txt")
        result = self.compressor.compress_file(file_path)
        
        expected_ratio = result.compressed_size / result.original_size
        self.assertAlmostEqual(result.compression_ratio, expected_ratio, places=5)


class TestContextCompressorErrorHandling(unittest.TestCase):
    """Test error handling and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            self.compressor.compress_file(Path("/nonexistent/path/file.txt"))
            
    def test_directory_instead_of_file(self):
        """Test error when path is a directory."""
        with self.assertRaises(ValueError):
            self.compressor.compress_file(Path(self.temp_dir))
            
    def test_invalid_method(self):
        """Test error with invalid compression method."""
        file_path = Path(self.temp_dir) / "test.txt"
        with open(file_path, 'w') as f:
            f.write("Test content")
            
        with self.assertRaises(ValueError) as context:
            self.compressor.compress_file(file_path, method="invalid_method")
            
        self.assertIn("Invalid method", str(context.exception))
        
    def test_query_too_long(self):
        """Test error when query exceeds maximum length."""
        file_path = Path(self.temp_dir) / "test.txt"
        with open(file_path, 'w') as f:
            f.write("Test content")
            
        long_query = "x" * 10001  # Exceeds 10,000 char limit
        
        with self.assertRaises(ValueError) as context:
            self.compressor.compress_file(file_path, query=long_query)
            
        self.assertIn("Query too long", str(context.exception))
        
    def test_text_too_large(self):
        """Test error when text exceeds maximum size."""
        # Create text larger than MAX_TEXT_SIZE (50 MB)
        # We'll test with a smaller size to avoid memory issues
        large_text = "x" * (MAX_TEXT_SIZE + 1)
        
        with self.assertRaises(ValueError) as context:
            self.compressor.compress_text(large_text)
            
        self.assertIn("Text too large", str(context.exception))


class TestContextCompressorStatistics(unittest.TestCase):
    """Test statistics tracking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_temp_file(self, content: str, filename: str = "test.txt") -> Path:
        """Create a temporary file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
        
    def test_stats_initial_state(self):
        """Test initial statistics state."""
        stats = self.compressor.get_stats()
        
        self.assertEqual(stats["compressions"], 0)
        self.assertEqual(stats["total_original_tokens"], 0)
        self.assertEqual(stats["total_compressed_tokens"], 0)
        self.assertEqual(stats["cache_hits"], 0)
        
    def test_stats_after_compression(self):
        """Test statistics update after compression."""
        file_path = self._create_temp_file("Hello world " * 100, "stats.txt")
        
        self.compressor.compress_file(file_path)
        stats = self.compressor.get_stats()
        
        self.assertEqual(stats["compressions"], 1)
        self.assertGreater(stats["total_original_tokens"], 0)
        
    def test_stats_multiple_compressions(self):
        """Test statistics accumulation across multiple compressions."""
        for i in range(5):
            file_path = self._create_temp_file(f"Content {i} " * 50, f"file{i}.txt")
            self.compressor.compress_file(file_path)
            
        stats = self.compressor.get_stats()
        
        self.assertEqual(stats["compressions"], 5)
        
    def test_overall_compression_percentage(self):
        """Test overall compression percentage calculation."""
        file_path = self._create_temp_file("# Comment\ndef f(): pass\n" * 100, "percent.py")
        self.compressor.compress_file(file_path, method="strip")
        
        stats = self.compressor.get_stats()
        
        self.assertIsInstance(stats["overall_compression_percent"], float)
        self.assertGreaterEqual(stats["overall_compression_percent"], 0)
        self.assertLessEqual(stats["overall_compression_percent"], 100)


class TestContextCompressorCaching(unittest.TestCase):
    """Test caching functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.compressor = ContextCompressor(cache_dir=self.cache_dir)
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_temp_file(self, content: str, filename: str = "test.txt") -> Path:
        """Create a temporary file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
        
    def test_cache_directory_creation(self):
        """Test cache directory is created."""
        self.assertTrue(self.cache_dir.exists())
        
    def test_cache_hit(self):
        """Test cache hit on repeated compression."""
        file_path = self._create_temp_file("Hello world " * 100, "cache_test.txt")
        
        # First compression - no cache
        self.compressor.compress_file(file_path, query="world")
        
        # Second compression - should hit cache
        self.compressor.compress_file(file_path, query="world")
        
        stats = self.compressor.get_stats()
        self.assertEqual(stats["cache_hits"], 1)
        
    def test_clear_cache(self):
        """Test cache clearing."""
        file_path = self._create_temp_file("Content for cache", "clear_test.txt")
        self.compressor.compress_file(file_path)
        
        # Verify cache has files
        cache_files = list(self.cache_dir.glob("*"))
        self.assertGreater(len(cache_files), 0)
        
        # Clear cache
        self.compressor.clear_cache()
        
        # Verify cache is empty
        cache_files = list(self.cache_dir.glob("*"))
        self.assertEqual(len(cache_files), 0)


class TestContextCompressorCodeProcessing(unittest.TestCase):
    """Test code-specific processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_temp_file(self, content: str, filename: str) -> Path:
        """Create a temporary file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
        
    def test_strip_python_comments(self):
        """Test Python comment stripping."""
        content = '''# This is a header comment
def hello():
    # Inline comment
    return "Hello"  # End of line comment

# Footer comment
'''
        file_path = self._create_temp_file(content, "comments.py")
        result = self.compressor.compress_file(file_path, method="strip")
        
        self.assertLess(result.compressed_size, result.original_size)
        
    def test_strip_python_docstrings(self):
        """Test Python docstring stripping."""
        content = '''def hello():
    """This is a long docstring
    that spans multiple lines
    and should be removed."""
    return "Hello"
'''
        file_path = self._create_temp_file(content, "docstrings.py")
        result = self.compressor.compress_file(file_path, method="strip")
        
        self.assertLess(result.compressed_size, result.original_size)
        
    def test_strip_javascript_comments(self):
        """Test JavaScript comment stripping."""
        content = '''// Single line comment
function hello() {
    /* Multi-line
       comment */
    return "Hello";
}
'''
        file_path = self._create_temp_file(content, "comments.js")
        result = self.compressor.compress_file(file_path, method="strip")
        
        self.assertLess(result.compressed_size, result.original_size)
        
    def test_extract_code_structure(self):
        """Test code structure extraction for Python files."""
        content = '''class MyClass:
    """Class docstring."""
    
    def method1(self):
        """Method docstring."""
        x = 1
        y = 2
        return x + y
        
    def method2(self):
        """Another method."""
        return None
'''
        file_path = self._create_temp_file(content, "structure.py")
        result = self.compressor.compress_file(file_path, method="summary")
        
        # Summary should include class and method definitions
        self.assertIsInstance(result, CompressionResult)


class TestContextCompressorIntegration(unittest.TestCase):
    """Integration tests for end-to-end workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_temp_file(self, content: str, filename: str) -> Path:
        """Create a temporary file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
        
    def test_full_workflow_file_compression(self):
        """Test complete file compression workflow."""
        # Create a realistic Python file
        content = '''#!/usr/bin/env python3
"""
Module for user authentication.
This module provides login, logout, and session management.
"""

import hashlib

class AuthManager:
    """Manages user authentication."""
    
    def __init__(self):
        """Initialize the auth manager."""
        self.sessions = {}
        
    def login(self, username, password):
        """
        Authenticate a user.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            bool: True if authenticated
        """
        # Validate input
        if not username or not password:
            return False
        
        # Check credentials (simplified)
        if username == "admin":
            self.sessions[username] = True
            return True
        return False
        
    def logout(self, username):
        """Log out a user."""
        if username in self.sessions:
            del self.sessions[username]
            return True
        return False

def main():
    """Main entry point."""
    auth = AuthManager()
    print(auth.login("admin", "password"))
    
if __name__ == "__main__":
    main()
'''
        file_path = self._create_temp_file(content, "auth.py")
        
        # Step 1: Estimate tokens
        with open(file_path, 'r') as f:
            original_tokens = self.compressor.estimate_tokens(f.read())
        
        # Step 2: Compress with query
        result = self.compressor.compress_file(file_path, query="login", method="relevant")
        
        # Step 3: Verify results
        self.assertGreater(result.estimated_token_savings, 0)
        self.assertLess(result.compressed_size, result.original_size)
        self.assertEqual(result.method, "relevant")
        
        # Step 4: Check stats
        stats = self.compressor.get_stats()
        self.assertEqual(stats["compressions"], 1)
        
    def test_batch_compression_workflow(self):
        """Test batch compression of multiple files."""
        # Create multiple files
        files = []
        for i in range(3):
            content = f"# File {i}\ndef func{i}(): pass\n" * 50
            file_path = self._create_temp_file(content, f"batch{i}.py")
            files.append(file_path)
            
        # Compress all files
        results = []
        for file_path in files:
            result = self.compressor.compress_file(file_path, method="strip")
            results.append(result)
            
        # Verify all were compressed
        self.assertEqual(len(results), 3)
        
        # Check cumulative stats
        stats = self.compressor.get_stats()
        self.assertEqual(stats["compressions"], 3)


def run_tests():
    """Run all tests with detailed output."""
    print("=" * 70)
    print("TESTING: ContextCompressor v1.0")
    print("Smart Context Reduction for AI Agents")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestContextCompressorCore,
        TestContextCompressorTextAPI,
        TestContextCompressorEdgeCases,
        TestContextCompressorErrorHandling,
        TestContextCompressorStatistics,
        TestContextCompressorCaching,
        TestContextCompressorCodeProcessing,
        TestContextCompressorIntegration,
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {result.testsRun} tests")
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"[OK] Passed: {passed}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    
    pass_rate = passed / result.testsRun * 100 if result.testsRun > 0 else 0
    print(f"Pass Rate: {pass_rate:.1f}%")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
