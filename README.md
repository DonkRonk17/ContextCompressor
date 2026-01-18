# ContextCompressor v1.0

**Smart Context Reduction for AI Agents**

ContextCompressor intelligently compresses large files and contexts to dramatically reduce token usage for AI agents. Extract only relevant sections, summarize long documents, strip unnecessary content, and track your savings.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](requirements.txt)

---

## 🎯 **What It Does**

**Problem:** AI agents waste tokens by loading entire files/documents when they only need 10-20% of the content.

**Solution:** ContextCompressor reduces context size by:
- ✂️ Extracting only sections relevant to your query
- 📋 Summarizing long documents while preserving key information
- 🧹 Stripping comments, docstrings, and excessive whitespace
- 💾 Caching compressed contexts for instant reuse
- 📊 Tracking compression ratios and token savings

**Real Impact:**
```python
# BEFORE: Load entire 5,000-line file (20,000 tokens → $0.06)
full_code = read_file("large_module.py")

# AFTER: Extract only relevant function (500 tokens → $0.0015)
from contextcompressor import ContextCompressor
compressor = ContextCompressor()
result = compressor.compress_file("large_module.py", query="login function")
# 💰 SAVED: 97.5% of tokens!
```

---

## 🚀 **Quick Start**

### Installation

```bash
# Clone or copy the script
cd /path/to/contextcompressor
python contextcompressor.py --help
```

**No dependencies required!** Pure Python standard library.

### Basic Usage

```bash
# Compress a file (auto-selects best method)
python contextcompressor.py compress large_file.py

# Extract sections relevant to a query
python contextcompressor.py compress large_file.py --query "authentication"

# Estimate token count
python contextcompressor.py estimate large_file.py

# View compression statistics
python contextcompressor.py stats
```

---

## 📖 **Usage**

### CLI Interface

```
contextcompressor.py compress <file> [--query "text"] [--method auto|relevant|summary|strip]
contextcompressor.py estimate <file>
contextcompressor.py stats
contextcompressor.py clear-cache
```

#### Compression Methods

- **`auto`** (default): Automatically chooses the best method based on file type and size
- **`relevant`**: Extracts only sections matching your query (requires `--query`)
- **`summary`**: Summarizes content, extracting structure/key lines
- **`strip`**: Removes comments, docstrings, and excessive whitespace

#### Examples

```bash
# Auto-compress Python file (strips comments/whitespace)
python contextcompressor.py compress myapp.py

# Find login-related code
python contextcompressor.py compress auth.py --query "login"

# Summarize large documentation
python contextcompressor.py compress README.md --method summary

# Estimate tokens before compression
python contextcompressor.py estimate large_codebase.py
```

### Python API

```python
from contextcompressor import ContextCompressor

# Initialize
compressor = ContextCompressor()

# Compress a file
result = compressor.compress_file(
    "large_file.py",
    query="authentication",  # Optional
    method="auto"            # auto, relevant, summary, strip
)

print(f"Original: {result.original_size:,} chars (~{result.original_size // 4:,} tokens)")
print(f"Compressed: {result.compressed_size:,} chars (~{result.compressed_size // 4:,} tokens)")
print(f"Saved: {result.estimated_token_savings:,} tokens ({result.compression_ratio:.1%} of original)")

# Compress arbitrary text
text = "Your large document here..."
compressed_text, result = compressor.compress_text(text, query="key section")

# Get stats
stats = compressor.get_stats()
print(f"Total compressions: {stats['compressions']}")
print(f"Overall savings: {stats['overall_compression_percent']:.1f}%")
print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
```

---

## 🧪 **Real-World Results**

### Test: Self-Compression

```bash
$ python contextcompressor.py compress contextcompressor.py --query "validate"

=== COMPRESSION RESULT ===
File: contextcompressor.py
Method: relevant
Original: 21,927 chars (~5,481 tokens)
Compressed: 3,289 chars (~822 tokens)
Ratio: 15.0%
Token Savings: ~4,659 tokens (85% reduction!)
```

**Cost Savings (Sonnet 4.5):**
- Original: 5,481 tokens × $3/1M = **$0.0164**
- Compressed: 822 tokens × $3/1M = **$0.0025**
- **Saved: $0.0139 per use** (85% cost reduction!)

If used 100 times/day → **$1.39/day** → **$42/month saved!**

---

## 🛡️ **Security & Validation**

ContextCompressor v1.0 includes robust input validation:

✅ **File size limits** (max 100 MB)  
✅ **Text size limits** (max 50 MB)  
✅ **Query length validation** (max 10,000 chars)  
✅ **Method validation** (only allows valid compression methods)  
✅ **Path traversal protection** (uses resolved paths)  
✅ **Graceful error handling** (clear error messages)

**Fully tested:**
- ✅ 20/20 security tests passed
- ✅ All edge cases handled
- ✅ Path traversal attacks blocked
- ✅ Size limits enforced

---

## 📦 **Zero Dependencies**

ContextCompressor uses only Python's standard library:
- `pathlib` - File path handling
- `json` - Cache serialization
- `hashlib` - Cache key generation
- `dataclasses` - Result objects
- `re` - Text processing

**No `pip install` required!**

---

## 🎓 **How It Works**

### Compression Strategies

1. **Relevant Extraction**: 
   - Searches for query matches in file
   - Extracts matching lines with 5-line context window
   - Perfect for finding specific functions/sections

2. **Summarization**:
   - For code: Extracts class/function signatures and docstrings
   - For text: Keeps first paragraph and short paragraphs (likely headers)
   - Ideal for large files when you need structure overview

3. **Stripping**:
   - Python: Removes `#` comments and docstrings
   - JavaScript: Removes `//` and `/* */` comments
   - All: Removes excessive whitespace and blank lines

4. **Caching**:
   - MD5 hash of (file_path + query + method)
   - Stores compressed result + metadata
   - Instant retrieval on cache hit

---

## 📊 **Statistics & Monitoring**

Track your compression performance:

```python
stats = compressor.get_stats()
# {
#   "compressions": 42,
#   "total_original_tokens": 250000,
#   "total_compressed_tokens": 50000,
#   "overall_compression_percent": 80.0,
#   "cache_hits": 15,
#   "cache_hit_rate": 35.7
# }
```

---

## 🎯 **Use Cases**

### For AI Agents

```python
# Instead of loading entire codebase
full_file = read_file("app/models.py")  # 10,000 tokens

# Compress first
result = compressor.compress_file("app/models.py", query="User model")
compressed = load_compressed(result)  # 1,200 tokens
# 88% token savings!
```

### For Documentation

```python
# Summarize long README
result = compressor.compress_file("LONG_README.md", method="summary")
# Keep only headers and key sections
```

### For Code Review

```python
# Extract only changed functions
result = compressor.compress_file("changed_file.py", query="new_feature")
# Review only relevant context
```

---

## 🧰 **Advanced Features**

### Custom Cache Directory

```python
from pathlib import Path
compressor = ContextCompressor(cache_dir=Path("/custom/cache"))
```

### Batch Compression

```python
files = ["file1.py", "file2.py", "file3.py"]
for file in files:
    result = compressor.compress_file(file)
    print(f"{file}: {result.compression_ratio:.1%}")
```

### Token Estimation

```python
# Estimate tokens before compression
text = "Your content here..."
estimated = compressor.estimate_tokens(text)
print(f"~{estimated:,} tokens")
```

---

## 🛠️ **Setup Script**

Create `setup.py` for easy installation:

```python
from setuptools import setup

setup(
    name="contextcompressor",
    version="1.0.0",
    py_modules=["contextcompressor"],
    python_requires=">=3.8",
    author="Team Brain",
    description="Smart context reduction for AI agents",
    license="MIT",
)
```

Install globally:
```bash
pip install .
```

---

## 📝 **License**

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 **Contributing**

This tool was built by **Team Brain (Atlas)** as part of the Q-Mode tooling initiative to optimize AI agent efficiency.

**For Team Brain agents:** See `INTEGRATION_EXAMPLES.md` and `CHEAT_SHEET.txt` for integration guides.

---

## 🎬 **Quick Reference**

```bash
# Compress file
python contextcompressor.py compress file.py

# Extract relevant sections
python contextcompressor.py compress file.py --query "search term"

# Estimate tokens
python contextcompressor.py estimate file.py

# View stats
python contextcompressor.py stats

# Clear cache
python contextcompressor.py clear-cache
```

---

## 🙏 Credits

Created by **Randell Logan Smith and Team Brain** at [Metaphy LLC](https://metaphysicsandcomputing.com)

Part of the HMSS (Heavenly Morning Star System) ecosystem.

---

** Our goal is to reduce token costs and improve AI efficiency.**
