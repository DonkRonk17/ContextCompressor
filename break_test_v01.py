import sys
sys.path.insert(0, r'C:\Users\logan\OneDrive\Documents\AutoProjects\ContextCompressor')
from contextcompressor import ContextCompressor
from pathlib import Path

print("=" * 60)
print("CONTEXTCOMPRESSOR V0.1 - BREAKING TEST")
print("=" * 60)

compressor = ContextCompressor()
tests_passed = 0
tests_failed = 0

def run_test(name, func, should_fail=False):
    global tests_passed, tests_failed
    print(f"\n[TEST] {name}")
    try:
        result = func()
        if should_fail:
            print(f"  [FAIL] Expected failure, but passed: {result}")
            tests_failed += 1
        else:
            print(f"  [OK] {result}")
            tests_passed += 1
    except Exception as e:
        if should_fail:
            print(f"  [OK] Failed as expected: {e}")
            tests_passed += 1
        else:
            print(f"  [FAIL] Unexpected error: {e}")
            tests_failed += 1

# Create test files
test_dir = Path("test_files")
test_dir.mkdir(exist_ok=True)

# Test file 1: Python code
test_py = test_dir / "test.py"
test_py.write_text("""
# This is a comment
def login(username, password):
    \"\"\"Login function with authentication.\"\"\"
    if username == "admin":
        return True
    return False

def logout():
    # Logout user
    print("Logged out")

class UserManager:
    \"\"\"Manages users.\"\"\"
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)
""")

# Test file 2: Large file
large_file = test_dir / "large.txt"
large_file.write_text("Line\\n" * 10000)

# === PHASE 1: Tests that SHOULD work ===
print("\\n" + "=" * 60)
print("PHASE 1: Normal usage tests")
print("=" * 60)

run_test("Compress Python file (auto method)", 
         lambda: compressor.compress_file(test_py))

run_test("Extract relevant (query: login)", 
         lambda: compressor.compress_file(test_py, query="login"))

run_test("Strip method on Python", 
         lambda: compressor.compress_file(test_py, method="strip"))

run_test("Summary method on Python", 
         lambda: compressor.compress_file(test_py, method="summary"))

run_test("Estimate tokens", 
         lambda: f"{compressor.estimate_tokens('Hello world')} tokens")

run_test("Compress text directly", 
         lambda: compressor.compress_text("This is a test\\n" * 100))

run_test("Get stats", 
         lambda: compressor.get_stats())

# === PHASE 2: Tests that SHOULD break ===
print("\\n" + "=" * 60)
print("PHASE 2: Breaking tests (try to cause failures)")
print("=" * 60)

run_test("Nonexistent file", 
         lambda: compressor.compress_file(Path("nonexistent.txt")), 
         should_fail=True)

run_test("Empty file path", 
         lambda: compressor.compress_file(Path("")), 
         should_fail=True)

run_test("Directory instead of file", 
         lambda: compressor.compress_file(test_dir), 
         should_fail=True)

run_test("Path traversal attack (../../etc/passwd)", 
         lambda: compressor.compress_file(Path("../../etc/passwd")), 
         should_fail=False)  # Let's see what happens

run_test("Extremely long query (10,000 chars)", 
         lambda: compressor.compress_file(test_py, query="X" * 10000), 
         should_fail=False)

run_test("Binary file (.exe or similar)", 
         lambda: compressor.compress_file(Path(sys.executable)), 
         should_fail=False)  # Will it handle binary?

run_test("Empty text compression", 
         lambda: compressor.compress_text(""), 
         should_fail=False)

run_test("NULL bytes in text", 
         lambda: compressor.compress_text("Test\\x00null\\x00bytes"), 
         should_fail=False)

run_test("Unicode heavy text (emoji spam)", 
         lambda: compressor.compress_text("🚀" * 1000), 
         should_fail=False)

run_test("Extremely large text (1M chars)", 
         lambda: compressor.compress_text("X" * 1000000), 
         should_fail=False)

run_test("Invalid method name", 
         lambda: compressor.compress_file(test_py, method="invalid_method"), 
         should_fail=False)

run_test("Query with special regex chars", 
         lambda: compressor.compress_file(test_py, query=".*[]()+?{}"), 
         should_fail=False)

run_test("Nested path traversal", 
         lambda: compressor.compress_file(Path("test_files/../test_files/test.py")), 
         should_fail=False)

# === PHASE 3: Cache manipulation ===
print("\\n" + "=" * 60)
print("PHASE 3: Cache manipulation tests")
print("=" * 60)

run_test("Compress same file twice (cache hit)", 
         lambda: compressor.compress_file(test_py))

run_test("Clear cache", 
         lambda: compressor.clear_cache())

run_test("Compress after cache clear", 
         lambda: compressor.compress_file(test_py))

# === PHASE 4: Edge cases ===
print("\\n" + "=" * 60)
print("PHASE 4: Edge cases")
print("=" * 60)

# File with no extension
no_ext = test_dir / "noextension"
no_ext.write_text("File without extension")
run_test("File without extension", 
         lambda: compressor.compress_file(no_ext))

# File with unusual extension
weird_ext = test_dir / "file.xyz123"
weird_ext.write_text("Unusual extension")
run_test("Unusual file extension", 
         lambda: compressor.compress_file(weird_ext))

# Single line file
single_line = test_dir / "single.txt"
single_line.write_text("Just one line")
run_test("Single line file", 
         lambda: compressor.compress_file(single_line))

# All whitespace file
whitespace_file = test_dir / "whitespace.txt"
whitespace_file.write_text("   \\n\\n\\n   \\n")
run_test("All whitespace file", 
         lambda: compressor.compress_file(whitespace_file))


print("\\n" + "=" * 60)
print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
print("=" * 60)

if tests_failed == 0:
    print("\\n[OK] All tests passed! But let's see if vulnerabilities were found...")
else:
    print(f"\\n[FAIL] {tests_failed} tests failed!")

# Cleanup
import shutil
shutil.rmtree(test_dir)
print("\\n[CLEANUP] Test files removed")
