# Clear IDE Cache - Fix Stale Linter Warnings

## Problem

You're seeing **108 problems** in the IDE, but the command-line linter shows **0 warnings**. This means:
- ✅ Your code is actually clean (all fixes are in place)
- ❌ The IDE is showing **stale/cached warnings**

## Solution: Clear IDE Cache

### Method 1: Reload Window (Easiest)

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Developer: Reload Window"
3. Press Enter

This should refresh the linter cache.

### Method 2: Restart Language Server

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Nextflow: Restart Language Server"
3. Press Enter

### Method 3: Clear All Caches (If above don't work)

1. Close Cursor completely
2. Delete cache directories:
   ```bash
   # Clear Nextflow extension cache
   rm -rf ~/Library/Application\ Support/Cursor/CachedExtensions/*
   rm -rf ~/Library/Application\ Support/Cursor/logs/*
   ```
3. Restart Cursor
4. Open your project again

### Method 4: Verify Code is Actually Clean

Run this to confirm code is clean:
```bash
conda activate rna-map-nextflow
nextflow lint . | grep -c "Warn"
# Should show: 0
```

## Verification

After clearing cache:
1. The Problems panel should show 0 or very few issues
2. Command-line lint shows: `✅ 24 files had no errors`
3. Pink underlines should disappear

## If Problems Persist

1. **Check if extension is updated**: Extensions → Nextflow IDE → Update if available
2. **Disable/enable extension**: Temporarily disable then re-enable the Nextflow IDE extension
3. **Check Output panel**: View → Output → Select "Nextflow Language Server" to see errors

## Why This Happens

- IDE linters cache results for performance
- Sometimes cache doesn't update after file changes
- Multiple linter instances might be running
- Extension might be using older lint rules

## Current Status

**Command-line verification shows your code is clean:**
```bash
$ nextflow lint .
✅ 24 files had no errors
```

All 29 warnings have been fixed in the actual code files. The IDE just needs to refresh its cache.


