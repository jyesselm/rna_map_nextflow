#!/usr/bin/env python3
"""Update imports in lib/ directory to use lib.* instead of rna_map.*"""

import re
from pathlib import Path

LIB_DIR = Path(__file__).parent.parent / "lib"


def update_imports_in_file(file_path: Path) -> None:
    """Update imports in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # Replace rna_map imports with lib imports
    content = re.sub(r"from rna_map\.logger", "from lib.logger", content)
    content = re.sub(r"from rna_map\.exception", "from lib.exception", content)
    content = re.sub(r"from rna_map\.core\.", "from lib.core.", content)
    content = re.sub(r"from rna_map\.io\.", "from lib.io.", content)
    content = re.sub(r"from rna_map\.analysis\.", "from lib.analysis.", content)
    content = re.sub(r"from rna_map\.pipeline\.", "from lib.pipeline.", content)
    content = re.sub(r"from rna_map\.mutation_histogram", "from lib.mutation_histogram", content)
    
    # Handle relative imports within lib
    # If importing from same level, keep relative
    # If importing from different submodule, update to lib.*
    
    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {file_path}")


def main():
    """Update all Python files in lib/ directory."""
    for py_file in LIB_DIR.rglob("*.py"):
        update_imports_in_file(py_file)
    print("Import updates complete!")


if __name__ == "__main__":
    main()

