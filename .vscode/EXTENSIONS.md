# Nextflow IDE Setup for Cursor/VS Code

## Required Extensions

1. **Nextflow IDE** - The official Nextflow extension for VS Code/Cursor
   - Extension ID: `nextflow.nextflow-ide`
   - Provides syntax highlighting, linting, and language server support

## Installation Steps

### 1. Install the Extension

In Cursor/VS Code:
- Open Extensions (Cmd+Shift+X)
- Search for "Nextflow IDE"
- Install the extension by nextflow

### 2. Configure Java Path

The Nextflow language server requires Java. Your Java is installed at:
```
/opt/homebrew/opt/openjdk
```

This is already configured in `.vscode/settings.json`.

### 3. Configure Nextflow Path

The Nextflow executable is in your conda environment:
```
/opt/homebrew/Caskroom/miniconda/base/envs/rna-map-nextflow/bin/nextflow
```

This is already configured in `.vscode/settings.json`.

### 4. Reload Window

After installing the extension:
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type "Reload Window" and select it
- This will restart the language server with the new configuration

## Troubleshooting

### If you still see pink underlines:

1. **Check extension is installed:**
   - Open Extensions panel
   - Verify "Nextflow IDE" is installed and enabled

2. **Check language server is running:**
   - Open Output panel (View → Output)
   - Select "Nextflow Language Server" from the dropdown
   - Look for any error messages

3. **Verify Nextflow is accessible:**
   ```bash
   conda activate rna-map-nextflow
   nextflow -version
   ```

4. **Check Java version:**
   ```bash
   java -version
   ```
   Should be Java 11+ (you have Java 23, which is fine)

### Alternative: Use Nextflow CLI linting

If the IDE extension isn't working, you can use command-line linting:
```bash
conda activate rna-map-nextflow
nextflow lint main.nf
```

## Current Configuration

Your `.vscode/settings.json` is configured with:
- Nextflow server path pointing to conda environment
- Java home configured
- File associations for `.nf` files
- Editor settings for Nextflow files

