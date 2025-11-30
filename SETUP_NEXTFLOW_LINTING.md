# Setting Up Nextflow Linting in Cursor

## The Problem
You're seeing pink wavy underlines everywhere because the Nextflow language server isn't working properly. This happens when:
1. The Nextflow extension isn't installed
2. The extension can't find Nextflow or Java
3. The language server isn't configured correctly

## Quick Fix (3 Steps)

### Step 1: Install Nextflow Extension

1. Open Extensions in Cursor:
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
   - Or click the Extensions icon in the sidebar

2. Search for "Nextflow IDE" or "nextflow.nextflow-ide"

3. Install the extension by nextflow

### Step 2: Verify Configuration

I've already created `.vscode/settings.json` with the correct paths. It should point to:
- **Nextflow**: `/opt/homebrew/Caskroom/miniconda/base/envs/rna-map-nextflow/bin/nextflow`
- **Java**: `/opt/homebrew/opt/openjdk`

### Step 3: Reload Cursor

After installing the extension:
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Developer: Reload Window"
3. Press Enter

The language server should now start and the pink underlines should disappear (or show real errors instead of false positives).

## Verify It's Working

After reloading, check:
1. Open the Output panel: View → Output (or `Cmd+Shift+U`)
2. Select "Nextflow Language Server" from the dropdown
3. You should see messages like "Language server started" or similar

## If It Still Doesn't Work

### Option 1: Check Extension Output
1. Open Output panel (`Cmd+Shift+U`)
2. Select "Nextflow Language Server"
3. Look for error messages - they'll tell you what's wrong

### Option 2: Use Command-Line Linting Instead

If the IDE extension continues to have issues, you can lint from the terminal:

```bash
# Activate conda environment
conda activate rna-map-nextflow

# Lint your workflow
nextflow lint main.nf

# Or lint all files
./lint.sh
```

### Option 3: Manual Configuration

If the automatic configuration doesn't work, you can manually set the paths in Cursor:
1. Press `Cmd+,` to open Settings
2. Search for "nextflow"
3. Set:
   - `Nextflow: Server Path` to your Nextflow executable
   - `Java: Home` to your Java installation

## Requirements Summary

✅ **Java**: Already installed (Java 23) at `/opt/homebrew/opt/openjdk`
✅ **Nextflow**: Already installed in conda env at `/opt/homebrew/Caskroom/miniconda/base/envs/rna-map-nextflow/bin/nextflow`
❓ **Extension**: You need to install the Nextflow IDE extension in Cursor

## Next Steps

1. Install the Nextflow IDE extension
2. Reload Cursor
3. The linting should work properly!

If you still have issues after installing the extension and reloading, let me know and we can troubleshoot further.

