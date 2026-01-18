import sys
sys.path.insert(0, r'C:\Users\logan\OneDrive\Documents\AutoProjects\ContextCompressor')
from contextcompressor import ContextCompressor
from pathlib import Path

print("=" * 60)
print("CONTEXTCOMPRESSOR V0.2 - SECURITY & VALIDATION TEST")
print("=" * 60)

compressor = ContextCompressor()
tests_passed = 0
tests_failed = 0

def run_test(name, func, should_fail=False, expected_error=None):
    global tests_passed, tests_failed
    print(f"\n[TEST-{'BLOCK' if should_fail else 'PASS'}] {name}")
    try:
        result = func()
        if should_fail:
            print(f"  [FAIL] Expected to fail, but passed: {result}")
            tests_failed += 1
        else:
            print(f"  [OK] Passed")
            tests_passed += 1
    except Exception as e:
        if should_fail:
            if expected_error and expected_error in str(e):
                print(f"  [OK] Blocked correctly: {e}")
                tests_passed += 1
            else:
                print(f"  [FAIL] Blocked, but unexpected error: {e}")
                tests_failed += 1
        else:
            print(f"  [FAIL] Unexpected error: {e}")
            tests_failed += 1

# Create test files
test_dir = Path("test_files")
test_dir.mkdir(exist_ok=True)

test_py = test_dir / "test.py"
test_py.write_text("def test():\\n    pass\\n" * 100)

# === PHASE 1: Valid usage (should PASS) ===
print("\\n" + "=" * 60)
print("PHASE 1: Valid usage (should PASS)")
print("=" * 60)

run_test("Normal compression (auto)", 
         lambda: compressor.compress_file(test_py))

run_test("Compress with query", 
         lambda: compressor.compress_file(test_py, query="test"))

run_test("Strip method", 
         lambda: compressor.compress_file(test_py, method="strip"))

run_test("Compress text directly", 
         lambda: compressor.compress_text("Test text\\n" * 100))

# === PHASE 2: Invalid usage (should BLOCK) ===
print("\\n" + "=" * 60)
print("PHASE 2: Invalid usage (should BLOCK)")
print("=" * 60)

run_test("Nonexistent file", 
         lambda: compressor.compress_file(Path("nonexistent.txt")), 
         should_fail=True, expected_error="File not found")

run_test("Directory instead of file", 
         lambda: compressor.compress_file(test_dir), 
         should_fail=True, expected_error="not a file")

run_test("Invalid method name", 
         lambda: compressor.compress_file(test_py, method="invalid"), 
         should_fail=True, expected_error="Invalid method")

run_test("Query too long (10,001 chars)", 
         lambda: compressor.compress_file(test_py, query="X" * 10001), 
         should_fail=True, expected_error="Query too long")

run_test("Text too large (51 MB)", 
         lambda: compressor.compress_text("X" * (51 * 1024 * 1024)), 
         should_fail=True, expected_error="Text too large")

# Create large file
large_file = test_dir / "large.bin"
large_file.write_bytes(b"X" * (101 * 1024 * 1024))  # 101 MB

run_test("File too large (101 MB)", 
         lambda: compressor.compress_file(large_file), 
         should_fail=True, expected_error="File too large")

# === PHASE 3: Security tests ===
print("\\n" + "=" * 60)
print("PHASE 3: Security tests")
print("=" * 60)

run_test("Path traversal (../..) - SHOULD FAIL OR RESOLVE SAFELY", 
         lambda: compressor.compress_file(Path("../../etc/passwd")), 
         should_fail=True, expected_error="File not found")

run_test("Empty query (should pass)", 
         lambda: compressor.compress_file(test_py, query=""))

run_test("None query (should pass)", 
         lambda: compressor.compress_file(test_py, query=None))

run_test("Empty text (should pass)", 
         lambda: compressor.compress_text(""))

run_test("Unicode heavy text (should pass)", 
         lambda: compressor.compress_text("🚀" * 1000))

# === PHASE 4: Edge cases ===
print("\\n" + "=" * 60)
print("PHASE 4: Edge cases")
print("=" * 60)

# File with no extension
no_ext = test_dir / "noextension"
no_ext.write_text("No extension file")
run_test("File without extension", 
         lambda: compressor.compress_file(no_ext))

# Single char file
single_char = test_dir / "single.txt"
single_char.write_text("X")
run_test("Single character file", 
         lambda: compressor.compress_file(single_char))

# All whitespace
whitespace = test_dir / "whitespace.txt"
whitespace.write_text("   \\n\\n  ")
run_test("All whitespace file", 
         lambda: compressor.compress_file(whitespace))

# Test methods explicitly
run_test("Explicit 'relevant' method", 
         lambda: compressor.compress_file(test_py, method="relevant", query="test"))

run_test("Explicit 'summary' method", 
         lambda: compressor.compress_file(test_py, method="summary"))


print("\\n" + "=" * 60)
print(f"FINAL RESULTS: {tests_passed} passed, {tests_failed} failed")
print("=" * 60)

# Cleanup
import shutil
shutil.rmtree(test_dir)
print("\\n[CLEANUP] Test files removed")

if tests_failed == 0:
    print("\\n[OK] v0.2 IS HARDENED! All validation working!")
    sys.exit(0)
else:
    print(f"\\n[FAIL] {tests_failed} tests failed! v0.2 needs more work.")
    sys.exit(1)
