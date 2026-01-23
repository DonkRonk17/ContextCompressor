# ContextCompressor v1.0 - Quick Start Guides

Agent-specific integration guides for fast adoption.

---

## 🔧 FORGE (Orchestrator #1, Reviewer)

**Your Use Cases:**
- Review Bolt's large codebases before approving
- Analyze project structure without reading every file
- Extract specific sections for task planning

**Quick Start:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()

# Reviewing Bolt's work
result = compressor.compress_file(
    "AutoProjects/NewProject/main.py",
    query="error handling",  # What you're reviewing
    method="relevant"
)

print(f"Original: {result.original_size // 4:,} tokens")
print(f"Compressed: {result.compressed_size // 4:,} tokens")
print(f"Saved: {result.estimated_token_savings:,} tokens")
```

**Integration Tip:** Before using `read_file` on large files, compress first!

**Expected Savings:** 70-85% per review

---

## 🗺️ ATLAS (Sonnet 4.5, Cursor)

**Your Use Cases:**
- Holy Grail automation file analysis
- Q-Mode tool development research
- Large codebase exploration

**Quick Start:**
```python
from contextcompressor import ContextCompressor

compressor = ContextCompressor()

# Before reading large files in Holy Grail
user_query = "authentication logic"
result = compressor.compress_file(
    file_path,
    query=user_query,
    method="relevant"
)

# Use compressed context instead of full file
compressed_context = get_compressed_content(result)
```

**Integration Tip:** Add to Holy Grail workflow Phase 1 (Pre-Flight Checks)

**Expected Savings:** 80-90% for targeted analysis

---

## 🌐 CLIO (Ubuntu CLI)

**Your Use Cases:**
- Log file analysis
- Documentation summarization
- System configuration review

**Quick Start:**
```bash
# Summarize large log file
python3 contextcompressor.py compress /var/log/syslog --method summary

# Find specific errors
python3 contextcompressor.py compress /var/log/app.log --query "ERROR"

# Estimate before compressing
python3 contextcompressor.py estimate /var/log/large.log
```

**Integration Tip:** Create alias for faster access:
```bash
alias cc='python3 /path/to/contextcompressor.py'
cc compress logfile.log
```

**Expected Savings:** 60-80% for logs, 70-85% for docs

---

## 🔗 NEXUS (Ubuntu CLI)

**Your Use Cases:**
- Code review before deployment
- Configuration file analysis
- Dependency investigation

**Quick Start:**
```bash
# Review code changes
python3 contextcompressor.py compress src/main.py --query "new_feature"

# Analyze config
python3 contextcompressor.py compress config.yaml --method strip

# Batch compression for multiple files
for file in src/*.py; do
    python3 contextcompressor.py compress "$file" --query "TODO"
done
```

**Integration Tip:** Compress before `git diff` analysis to focus on relevant changes

**Expected Savings:** 70-85% for targeted review

---

## ⚡ BOLT (Executor, FREE)

**Your Use Cases:**
- Large project analysis before building
- Template file review
- Documentation reading

**Quick Start:**
```bash
# When analyzing new project requirements
python contextcompressor.py compress PROJECT_SPEC.md --method summary

# Finding specific implementation details
python contextcompressor.py compress template.py --query "database"

# Estimating token cost before reading
python contextcompressor.py estimate large_codebase.py
```

**Integration Tip:** Since you're FREE, token savings aren't as critical, but speed is! Use `--method summary` for faster analysis.

**Expected Savings:** 50-70% (focus on speed, not just cost)

---

## 🎯 COMMON PATTERNS FOR ALL AGENTS

### Pattern 1: Before Reading Large Files
```python
# Instead of:
content = read_file("large_file.py")  # 10,000 tokens

# Do this:
result = compressor.compress_file("large_file.py", query="specific topic")
compressed_content = load_compressed(result)  # 1,500 tokens
# Saved: 8,500 tokens!
```

### Pattern 2: Documentation Review
```python
# Instead of:
full_docs = read_file("LONG_README.md")  # 5,000 tokens

# Do this:
result = compressor.compress_file("LONG_README.md", method="summary")
key_sections = load_compressed(result)  # 800 tokens
# Saved: 4,200 tokens!
```

### Pattern 3: Code Search
```python
# Instead of:
full_codebase = read_file("app.py")  # 15,000 tokens

# Do this:
result = compressor.compress_file("app.py", query="login function")
relevant_code = load_compressed(result)  # 2,000 tokens
# Saved: 13,000 tokens!
```

---

## 📊 Integration with TokenTracker

Track your savings!

```python
from tokentracker import TokenTracker
from contextcompressor import ContextCompressor

tracker = TokenTracker()
compressor = ContextCompressor()

# Before compression
original_tokens = compressor.estimate_tokens(full_content)
tracker.log_usage("ATLAS", "sonnet-4.5", original_tokens, 0, "Before compression")

# After compression
result = compressor.compress_file(file_path)
compressed_tokens = result.compressed_size // compressor.CHARS_PER_TOKEN
tracker.log_usage("ATLAS", "sonnet-4.5", compressed_tokens, 0, "After compression")

# See savings
print(f"Saved {result.estimated_token_savings:,} tokens!")
```

---

## 🎬 First Day Checklist

✅ Read CHEAT_SHEET.txt  
✅ Run first compression: `python contextcompressor.py compress README.md`  
✅ Verify savings: Check output for token reduction  
✅ Integrate into one workflow (pick easiest use case)  
✅ Reply to Atlas's Synapse message with your result!  

---

## 🚨 Troubleshooting

**"File not found"**
- Check path is correct
- Use absolute path if needed

**"File too large"**
- Max: 100 MB
- Use `--method summary` for huge files

**"No compression"**
- Try different method (e.g., `--method relevant --query "keyword"`)
- Check file has compressible content

**"Slow compression"**
- Normal for 1MB+ files (~1-2s)
- Result is cached for instant reuse
- Check cache hit rate: `python contextcompressor.py stats`

---

## 🎉 Success Story Template

Share your wins in Synapse!

```
🎉 ContextCompressor Success!

File: [filename]
Original: [X] tokens
Compressed: [Y] tokens
Saved: [Z] tokens ([%] reduction)

Use case: [what you were doing]
Method: [auto/relevant/summary/strip]

This would've cost $X.XX, now costs $Y.YY!
Saved: $Z.ZZ! 💰

- [Your Agent Name]
```

---

**Goal:** Make compression a habit within 3 days!  
**Result:** $40-50/month savings, Logan under budget! 🎯

**Questions?** Post to Synapse! Atlas is monitoring. 🗺️
