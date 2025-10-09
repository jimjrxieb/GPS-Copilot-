# 🔄 Windows ↔ WSL Sync Guide

**Purpose**: Sync LLM training data and documents between Windows Desktop and GP-Copilot RAG system

**Last Updated**: 2025-10-07

---

## 🎯 Quick Start

### From Windows (Easiest Way)
1. Drop files into: `C:\Users\jimmi\OneDrive\Desktop\LLM-Training\`
2. Double-click: `sync_to_gp_copilot.bat`
3. Done! Files are synced to WSL

### From WSL
```bash
cd /home/jimmie/linkops-industries/GP-copilot

# Sync Windows → WSL
./sync_windows_to_wsl.sh

# Sync WSL → Windows
./sync_wsl_to_windows.sh
```

---

## 📂 Directory Mapping

| Location | Path |
|----------|------|
| **Windows** | `C:\Users\jimmi\OneDrive\Desktop\LLM-Training\` |
| **WSL** | `/home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync/` |
| **From WSL as Windows Path** | `/mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training/` |

---

## 🛠️ Sync Scripts

### 1. Windows → WSL Sync ([sync_windows_to_wsl.sh](sync_windows_to_wsl.sh))
**When to use**: After adding files to Windows LLM-Training folder

**What it does**:
- Copies all files from Windows to WSL
- Preserves timestamps and metadata
- Only copies new/changed files (incremental)
- Excludes .git, node_modules, __pycache__, etc.

**Usage**:
```bash
./sync_windows_to_wsl.sh
```

**Output**:
```
🔄 Syncing Windows → WSL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: /mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training
Target: /home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync

📁 Files in target before sync: 0
🔄 Copying files...
✅ Sync Complete!
📊 Files in target: 8
📈 Files added/updated: 8
```

---

### 2. WSL → Windows Sync ([sync_wsl_to_windows.sh](sync_wsl_to_windows.sh))
**When to use**: After processing files in WSL, want them back in Windows

**What it does**:
- Copies all files from WSL to Windows
- Preserves timestamps and metadata
- Only copies new/changed files (incremental)
- Makes files accessible from Windows Explorer

**Usage**:
```bash
./sync_wsl_to_windows.sh
```

---

### 3. Windows Batch File ([sync_to_gp_copilot.bat](file:///C:/Users/jimmi/OneDrive/Desktop/LLM-Training/sync_to_gp_copilot.bat))
**When to use**: Quick sync from Windows without opening WSL terminal

**Location**: `C:\Users\jimmi\OneDrive\Desktop\LLM-Training\sync_to_gp_copilot.bat`

**What it does**:
- Runs `sync_windows_to_wsl.sh` from Windows
- Shows progress in Windows Command Prompt
- Pauses at end so you can see results

**Usage**:
1. Double-click `sync_to_gp_copilot.bat` in Windows Explorer
2. Wait for sync to complete
3. Press any key to close

---

## 🔄 Complete Workflow

### Scenario 1: Add New Training Data from Windows
```
1. 📁 Drop files in: C:\Users\jimmi\OneDrive\Desktop\LLM-Training\
   Examples:
   - new-k8s-training.txt
   - devsecops-questions.jsonl
   - security-best-practices.md

2. 🔄 Double-click: sync_to_gp_copilot.bat
   → Files synced to WSL

3. 🧠 Learn from files (in WSL):
   python GP-RAG/simple_learn.py
   → Files moved to processed/
   → Knowledge added to RAG system

4. ✅ Query new knowledge:
   jade chat --query "Tell me about K8s security"
```

---

### Scenario 2: Process Files in WSL, Send Back to Windows
```
1. 📝 Work on files in WSL:
   /home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync/

2. 🔄 Sync back to Windows:
   ./sync_wsl_to_windows.sh

3. ✅ Access from Windows:
   Open C:\Users\jimmi\OneDrive\Desktop\LLM-Training\
```

---

### Scenario 3: Bidirectional Sync (Keep Both in Sync)
```
# Update Windows first
1. Add/edit files on Windows side

# Sync to WSL
2. Double-click sync_to_gp_copilot.bat (or run ./sync_windows_to_wsl.sh)

# Process in WSL
3. Work on files, make changes

# Sync back to Windows
4. ./sync_wsl_to_windows.sh

# Both directories now in sync!
```

---

## 📊 Currently Synced Files

After first sync (2025-10-07):

| File | Size | Type | Purpose |
|------|------|------|---------|
| `JAMES-TDv1.txt` | 6.2K | Training | James-specific training data v1 |
| `JAMES-TRAINING-DATA.txt` | 1.6K | Training | Core James training data |
| `K8s-TD.txt` | 19K | Training | Kubernetes training data |
| `james_devsecops_20.jsonl` | 6.2K | JSONL | DevSecOps Q&A (20 examples) |
| `james_final_100.jsonl` | 66K | JSONL | Final training set (100 examples) |
| `james_k8s_common_errors_80.jsonl` | 60K | JSONL | K8s common errors (80 examples) |
| `k8s.txt` | 13K | Text | Kubernetes documentation |
| `sync_to_gp_copilot.bat` | 724B | Batch | Windows sync script |

**Total**: 8 files, ~173KB

---

## 🔒 Sync Exclusions

These file types are **automatically excluded** from sync:

```
.git/              # Git repositories
node_modules/      # Node.js dependencies
__pycache__/       # Python cache
*.pyc              # Python compiled files
.DS_Store          # macOS metadata
Thumbs.db          # Windows thumbnails
```

**Why**: These are system/cache files that don't need to be synced and would slow down transfers.

---

## 🐛 Troubleshooting

### Problem: "Windows source directory not found"
**Cause**: LLM-Training folder doesn't exist or is renamed

**Fix**:
```bash
# Check if folder exists
ls /mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training

# If not, create it
mkdir -p /mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training
```

---

### Problem: "Permission denied" when running .sh scripts
**Cause**: Scripts aren't executable

**Fix**:
```bash
chmod +x sync_windows_to_wsl.sh sync_wsl_to_windows.sh
```

---

### Problem: Sync is very slow
**Cause**: Large files or many files

**Fix**:
- rsync only copies new/changed files (incremental)
- First sync is slower, subsequent syncs are faster
- Exclude large unnecessary files by adding to rsync --exclude

---

### Problem: Files appear in WSL but not in Windows
**Cause**: Need to run reverse sync

**Fix**:
```bash
./sync_wsl_to_windows.sh
```

---

### Problem: Windows batch file doesn't work
**Cause**: WSL not installed or not running

**Fix**:
1. Check WSL is installed: `wsl --version` in PowerShell
2. Run manually in WSL terminal instead

---

## 📝 File Format Support

Both sync scripts support **all file types**:

| Format | Extension | Example Use |
|--------|-----------|-------------|
| Text | `.txt` | Training data, documentation |
| Markdown | `.md` | Guides, READMEs |
| JSONL | `.jsonl` | Structured training data |
| JSON | `.json` | Scan results, configs |
| Python | `.py` | Scripts, code examples |
| YAML | `.yaml`, `.yml` | Configs, K8s manifests |
| Code | `.js`, `.go`, `.java`, etc. | Code samples |
| Binary | `.pdf`, `.docx`, etc. | Documents (not recommended for training) |

**Recommendation**: Use `.txt`, `.md`, or `.jsonl` for RAG learning - these are parsed best.

---

## 🔗 Integration with GP-RAG

After syncing files to `windows-sync/`, you have **3 options**:

### Option 1: Simple Learning (Easiest)
```bash
cd /home/jimmie/linkops-industries/GP-copilot
python GP-RAG/simple_learn.py
```

**What happens**:
- Scans `unprocessed/windows-sync/` (and other unprocessed dirs)
- Adds all documents to vector store
- Moves processed files to `processed/`

---

### Option 2: Selective Learning (From windows-sync Only)
```bash
# Copy specific files to main unprocessed/ directory
cp GP-RAG/unprocessed/windows-sync/important-doc.md GP-RAG/unprocessed/

# Learn from that specific file
python GP-RAG/simple_learn.py
```

---

### Option 3: Keep in windows-sync/ (Don't Learn Yet)
```bash
# Just sync, don't process
./sync_windows_to_wsl.sh

# Files stay in windows-sync/ for review
# Manually decide which to learn from later
```

---

## 📈 Stats & Monitoring

### Check Sync Status
```bash
# Count files in Windows (from WSL)
find /mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training -type f | wc -l

# Count files in WSL
find /home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync -type f | wc -l

# Compare (should be equal after sync)
```

### Check Last Sync Time
```bash
# Last modified time of windows-sync directory
stat /home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync
```

### Check Sync Size
```bash
# Size of Windows directory
du -sh /mnt/c/Users/jimmi/OneDrive/Desktop/LLM-Training

# Size of WSL directory
du -sh /home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/windows-sync
```

---

## 🚀 Advanced Usage

### Sync Only Specific File Types
```bash
# Modify sync script to only sync .txt files
rsync -av --include='*.txt' --exclude='*' \
    "$WINDOWS_SOURCE/" "$WSL_TARGET/"
```

### Dry Run (Preview Without Copying)
```bash
# Test what would be copied
rsync -avn "$WINDOWS_SOURCE/" "$WSL_TARGET/"
```

### Delete Extraneous Files (Mirror Sync)
```bash
# Make WSL exactly match Windows (deletes extra files in WSL)
rsync -av --delete "$WINDOWS_SOURCE/" "$WSL_TARGET/"
```

**⚠️ Warning**: `--delete` removes files in target that don't exist in source!

---

## 🔄 Automation Ideas

### Auto-Sync Every Hour (Cron Job)
```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * cd /home/jimmie/linkops-industries/GP-copilot && ./sync_windows_to_wsl.sh >> /tmp/sync.log 2>&1
```

### Auto-Sync + Auto-Learn (Complete Pipeline)
```bash
# Create combined script
cat > auto_sync_and_learn.sh << 'EOF'
#!/bin/bash
cd /home/jimmie/linkops-industries/GP-copilot
./sync_windows_to_wsl.sh
python GP-RAG/simple_learn.py
EOF

chmod +x auto_sync_and_learn.sh
```

---

## 📚 Related Documentation

- [GP-RAG/README.md](GP-RAG/README.md) - RAG system overview
- [GP-RAG/simple_learn.py](GP-RAG/simple_learn.py) - Learning script
- [RAG_LEARNING_INTEGRATION_GUIDE.md](RAG_LEARNING_INTEGRATION_GUIDE.md) - Complete learning guide

---

## ✅ Success Criteria

You know sync is working correctly when:

1. ✅ Files appear in both Windows and WSL after sync
2. ✅ File sizes match (check with `ls -lh`)
3. ✅ Timestamps are preserved
4. ✅ No error messages during sync
5. ✅ simple_learn.py can read files from windows-sync/

---

## 🎯 Next Steps

Now that sync is set up:

1. **Test it**: Drop a test file in Windows LLM-Training, run sync
2. **Learn from it**: `python GP-RAG/simple_learn.py`
3. **Query it**: `jade chat --query "content from test file"`
4. **Use it regularly**: Keep adding training data to LLM-Training folder

---

**Created**: 2025-10-07
**Status**: ✅ Tested and Working
**Synced Files**: 8 files, ~173KB
**Integration**: Ready for GP-RAG learning pipeline
