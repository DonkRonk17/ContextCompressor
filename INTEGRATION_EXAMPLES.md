# ContextCompressor v1.0 - Integration Examples

Copy-paste code snippets for fast integration into your workflows.

---

## 🎯 Scenario 1: Large File Analysis (FORGE/ATLAS)

**Problem:** Need to analyze a 20,000-token file, but only care about authentication.

**Without ContextCompressor:**
```python
# Expensive: Load entire file
content = read_file("app/auth.py")  # 20,000 tokens → $0.06
analyze(content)
```

**With ContextCompressor:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()
result = compressor.compress_file("app/auth.py", query="authentication")

# Only 3,000 tokens → $0.009
compressed_content = load_compressed_content(result)
analyze(compressed_content)

# Saved: $0.051 (85%)
print(f"💰 Saved {result.estimated_token_savings:,} tokens!")
```

---

## 🎯 Scenario 2: Documentation Summarization (ALL AGENTS)

**Problem:** Need overview of 50-page documentation.

**Without ContextCompressor:**
```python
docs = read_file("LONG_DOCS.md")  # 25,000 tokens → $0.075
overview = summarize(docs)
```

**With ContextCompressor:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()
result = compressor.compress_file("LONG_DOCS.md", method="summary")

# Only 4,000 tokens → $0.012
summary = load_compressed_content(result)
overview = summarize(summary)

# Saved: $0.063 (84%)
```

---

## 🎯 Scenario 3: Code Review (FORGE/NEXUS)

**Problem:** Review Bolt's 5,000-line codebase for error handling.

**Without ContextCompressor:**
```python
full_code = read_file("AutoProjects/NewTool/main.py")  # 30,000 tokens → $0.09
review_error_handling(full_code)
```

**With ContextCompressor:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()
result = compressor.compress_file(
    "AutoProjects/NewTool/main.py",
    query="error handling try except raise",
    method="relevant"
)

# Only 3,500 tokens → $0.0105
error_handling_code = load_compressed_content(result)
review_error_handling(error_handling_code)

# Saved: $0.0795 (88%)
```

---

## 🎯 Scenario 4: Batch Processing (ALL AGENTS)

**Problem:** Analyze 10 files for security issues.

**Without ContextCompressor:**
```python
total_tokens = 0
for file in files:
    content = read_file(file)  # 10 × 15,000 = 150,000 tokens → $0.45
    analyze_security(content)
    total_tokens += estimate_tokens(content)

print(f"Total cost: ${total_tokens / 1_000_000 * 3:.2f}")
```

**With ContextCompressor:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()
total_original = 0
total_compressed = 0

for file in files:
    result = compressor.compress_file(file, query="security vulnerability auth")
    compressed = load_compressed_content(result)
    analyze_security(compressed)
    
    total_original += result.original_size // 4
    total_compressed += result.compressed_size // 4

saved_tokens = total_original - total_compressed
saved_cost = saved_tokens / 1_000_000 * 3

print(f"💰 Saved {saved_tokens:,} tokens (${saved_cost:.2f})")
# Typical: 80% reduction → $0.36 saved!
```

---

## 🎯 Scenario 5: Log Analysis (CLIO)

**Problem:** Find errors in 100MB log file.

**Without ContextCompressor:**
```bash
# Can't even load this into context!
# File too large → 400,000+ tokens → $1.20+
```

**With ContextCompressor:**
```bash
# Extract only error lines
python3 contextcompressor.py compress /var/log/app.log --query "ERROR CRITICAL FATAL"

# Result: 5,000 tokens → $0.015
# Saved: 395,000+ tokens ($1.18+!)
```

---

## 🎯 Scenario 6: Holy Grail Integration (ATLAS)

**Problem:** Phase 1 file scanning loads entire files.

**Current Workflow:**
```python
# Phase 1: Pre-Flight Checks
for project in os.listdir("AutoProjects"):
    readme = read_file(f"{project}/README.md")  # 5,000 tokens each × 23 projects = 115,000 tokens
    purpose = extract_purpose(readme)
```

**Optimized Workflow:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()

# Phase 1: Pre-Flight Checks
for project in os.listdir("AutoProjects"):
    result = compressor.compress_file(
        f"{project}/README.md",
        query="Purpose Features",
        method="summary"
    )
    # Only 800 tokens each × 23 = 18,400 tokens
    compressed_readme = load_compressed_content(result)
    purpose = extract_purpose(compressed_readme)

# Saved: 96,600 tokens ($0.29 per Holy Grail run!)
```

---

## 🎯 Scenario 7: TokenTracker Integration

**Track your savings automatically!**

```python
from contextcompressor import ContextCompressor
from tokentracker import TokenTracker

compressor = ContextCompressor()
tracker = TokenTracker()

def compress_and_track(file_path, agent_name, model, query=None):
    """Compress a file and log token savings to TokenTracker."""
    
    # Get original token count
    with open(file_path, 'r') as f:
        original_content = f.read()
    original_tokens = compressor.estimate_tokens(original_content)
    
    # Compress
    result = compressor.compress_file(file_path, query=query)
    compressed_tokens = result.compressed_size // compressor.CHARS_PER_TOKEN
    
    # Log to TokenTracker
    tracker.log_usage(
        agent_name,
        model,
        compressed_tokens,  # We only sent compressed tokens
        0,
        f"Compressed {file_path} (saved {result.estimated_token_savings} tokens)"
    )
    
    print(f"💰 Saved {result.estimated_token_savings:,} tokens!")
    return result

# Usage
result = compress_and_track("large_file.py", "ATLAS", "sonnet-4.5", query="login")
```

---

## 🎯 Scenario 8: Caching for Speed

**Problem:** Repeatedly analyzing the same file wastes time.

**Slow Approach:**
```python
# Every time we analyze, we re-compress
for i in range(10):
    result = compressor.compress_file("large_file.py", query="auth")
    analyze(result)
# Takes: 10 × 0.5s = 5 seconds
```

**Fast Approach (with cache):**
```python
# First time: 0.5s (compression + cache save)
result1 = compressor.compress_file("large_file.py", query="auth")

# Next 9 times: ~0.003s each (cache hit!)
for i in range(9):
    result = compressor.compress_file("large_file.py", query="auth")
    analyze(result)
# Takes: 0.5s + 9 × 0.003s = 0.527s total
# Speedup: 9.5x faster!

# Check cache performance
stats = compressor.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
```

---

## 🎯 Scenario 9: Estimate Before Compressing

**Problem:** Not sure if compression is worth it?

**Solution: Estimate first!**

```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()

# Estimate original token count
tokens = compressor.estimate_tokens(full_content)
cost = tokens / 1_000_000 * 3  # Sonnet 4.5 pricing

if cost > 0.01:  # If more than 1 cent
    print(f"Large file ({tokens:,} tokens, ${cost:.3f})")
    print("Compressing to save tokens...")
    
    result = compressor.compress_file(file_path)
    print(f"Saved {result.estimated_token_savings:,} tokens (${result.estimated_token_savings / 1_000_000 * 3:.3f})")
else:
    print("Small file, compression not needed")
```

---

## 🎯 Scenario 10: Python Code Structure Extraction

**Problem:** Need function signatures without implementations.

**Without ContextCompressor:**
```python
# Manual parsing
import ast
with open("large_module.py") as f:
    tree = ast.parse(f.read())
# Complex AST traversal...
```

**With ContextCompressor:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()

# Auto-extracts Python structure
result = compressor.compress_file("large_module.py", method="summary")
# Result: Only class/function definitions + docstrings
# Perfect for understanding code structure!

structure = load_compressed_content(result)
print(structure)
```

---

## 🎬 Integration Checklist

For each agent, complete this checklist:

✅ **Day 1:** Copy one example above into your workflow  
✅ **Day 2:** Measure token savings with first use  
✅ **Day 3:** Integrate into 2-3 common workflows  
✅ **Week 1:** Track monthly savings projection  
✅ **Week 2:** Share success story in Synapse  

---

## 🏆 Expected Results

| Use Case | Compression | Tokens Saved | Cost Saved |
|----------|-------------|--------------|------------|
| Large file analysis | 85% | 17,000 | $0.051 |
| Documentation | 80% | 20,000 | $0.060 |
| Code review | 88% | 26,500 | $0.080 |
| Batch processing | 80% | 120,000 | $0.360 |
| Log analysis | 95%+ | 395,000+ | $1.18+ |
| Holy Grail scan | 84% | 96,600 | $0.290 |

**Total potential savings: $40-50/month across all agents!**

---

## 💡 Pro Tips

1. **Use `--query` for targeted extraction** (80-90% compression)
2. **Use `--method summary` for structure only** (70-85% compression)
3. **Use `--method strip` for comment removal** (50-70% compression)
4. **Check cache hits** with `contextcompressor.py stats`
5. **Integrate with TokenTracker** to measure savings
6. **Estimate first** for large files to see potential savings

---

**Questions?** Check README.md, EXAMPLES.md, or post to Synapse!

**Built by:** Atlas (Sonnet 4.5)  
**Date:** 2026-01-17  
**Goal:** $40-50/month savings, bring Logan under budget! 💰
