"""Generate baseline and current outputs and compare them.

This script:
1. Generates baseline output on main branch
2. Generates current output on current branch
3. Compares summary.csv and mutation_histos.json
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd


def run_command(cmd: str, check: bool = True) -> tuple[str, str]:
    """Run a shell command and return output.

    Args:
        cmd: Command to run
        check: Whether to raise on non-zero exit

    Returns:
        Tuple of (stdout, stderr)
    """
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=check
    )
    return result.stdout, result.stderr


def get_current_branch() -> str:
    """Get current git branch name.

    Returns:
        Branch name
    """
    stdout, _ = run_command("git rev-parse --abbrev-ref HEAD")
    return stdout.strip()


def generate_baseline_output(baseline_dir: Path) -> bool:
    """Generate baseline output on main branch.

    Args:
        baseline_dir: Directory to save baseline output

    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("STEP 1: Generating baseline output on main branch")
    print("=" * 60)

    # Check current branch
    current_branch = get_current_branch()
    print(f"\nCurrent branch: {current_branch}")

    # Checkout main branch (stash changes if needed)
    print("\nChecking out main branch...")
    try:
        # Check if there are uncommitted changes
        stdout, _ = run_command("git status --porcelain", check=False)
        if stdout.strip():
            print("WARNING: Uncommitted changes detected. Stashing...")
            run_command("git stash push -m 'Temporary stash for comparison'")
            stashed = True
        else:
            stashed = False

        run_command("git checkout main")
        print("✓ Switched to main branch")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to checkout main branch: {e}")
        print("\nPlease commit or stash your changes first, then run again.")
        return False

    # Clean up any existing output
    if Path("output").exists():
        shutil.rmtree(Path("output"))
    if Path("input").exists():
        shutil.rmtree(Path("input"))
    if Path("log").exists():
        shutil.rmtree(Path("log"))

    # Run rna-map
    print("\nRunning rna-map on main branch...")
    cmd = (
        "rna-map -fa test/resources/case_1/test.fasta "
        "-fq1 test/resources/case_1/test_mate1.fastq "
        "-fq2 test/resources/case_1/test_mate2.fastq"
    )
    try:
        stdout, stderr = run_command(cmd)
        if stderr:
            print(f"Warnings/Errors: {stderr}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to run rna-map: {e}")
        print(f"stderr: {e.stderr}")
        return False

    # Copy output to baseline directory
    if not Path("output/BitVector_Files").exists():
        print("ERROR: output/BitVector_Files not found")
        # Restore branch if we stashed
        if stashed:
            run_command("git checkout " + current_branch, check=False)
            run_command("git stash pop", check=False)
        return False

    baseline_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        Path("output/BitVector_Files"),
        baseline_dir,
        dirs_exist_ok=True,
    )
    print(f"\n✓ Baseline output saved to: {baseline_dir}")

    # Restore original branch
    print(f"\nRestoring branch: {current_branch}")
    run_command(f"git checkout {current_branch}")
    if stashed:
        run_command("git stash pop", check=False)
        print("✓ Restored stashed changes")

    return True


def generate_current_output(current_dir: Path) -> bool:
    """Generate current output on current branch.

    Args:
        current_dir: Directory to save current output

    Returns:
        True if successful, False otherwise
    """
    print("\n" + "=" * 60)
    print("STEP 2: Generating current output on current branch")
    print("=" * 60)

    current_branch = get_current_branch()
    print(f"\nCurrent branch: {current_branch}")

    # Run pipeline directly using Python API
    print("\nRunning pipeline...")
    import tempfile
    temp_base = Path(tempfile.mkdtemp(prefix="rna_map_comparison_"))
    temp_output = temp_base / "output"
    temp_input = temp_base / "input"
    temp_log = temp_base / "log"

    try:
        from rna_map.pipeline import run
        from rna_map.parameters import get_default_params

        test_resources = Path("test/resources/case_1")
        params = get_default_params()
        params["dirs"]["output"] = str(temp_output.absolute())
        params["dirs"]["input"] = str(temp_input.absolute())
        params["dirs"]["log"] = str(temp_log.absolute())
        params["overwrite"] = True

        run(
            fasta=test_resources / "test.fasta",
            fastq1=test_resources / "test_mate1.fastq",
            fastq2=test_resources / "test_mate2.fastq",
            dot_bracket=Path(""),
            params=params,
        )

        # Copy output to current directory
        bitvector_dir = temp_output / "BitVector_Files"
        if not bitvector_dir.exists():
            print("ERROR: BitVector_Files directory not found")
            return False

        current_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(bitvector_dir, current_dir, dirs_exist_ok=True)
        print(f"\n✓ Current output saved to: {current_dir}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to generate current output: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up temp directory
        if temp_base.exists():
            shutil.rmtree(temp_base)


def compare_outputs(baseline_dir: Path, current_dir: Path) -> bool:
    """Compare baseline and current outputs.

    Args:
        baseline_dir: Directory with baseline output
        current_dir: Directory with current output

    Returns:
        True if outputs match, False otherwise
    """
    print("\n" + "=" * 60)
    print("STEP 3: Comparing outputs")
    print("=" * 60)

    # Use the comparison script
    cmd = f"python test/compare_outputs.py {baseline_dir} {current_dir}"
    try:
        stdout, stderr = run_command(cmd)
        print(stdout)
        if stderr:
            print(f"Warnings: {stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Comparison failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def main():
    """Main function to generate and compare outputs."""
    # Create comparison directories
    comparison_dir = Path("comparison_outputs")
    baseline_dir = comparison_dir / "baseline"
    current_dir = comparison_dir / "current"

    print("RNA-MAP Output Comparison")
    print("=" * 60)
    print(f"Baseline will be saved to: {baseline_dir}")
    print(f"Current will be saved to: {current_dir}")
    print()

    # Step 1: Generate baseline
    if not generate_baseline_output(baseline_dir):
        print("\n✗ Failed to generate baseline output")
        sys.exit(1)

    # Step 2: Generate current output
    if not generate_current_output(current_dir):
        print("\n✗ Failed to generate current output")
        sys.exit(1)

    # Step 3: Compare
    if not compare_outputs(baseline_dir, current_dir):
        print("\n✗ Outputs do not match")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ COMPARISON COMPLETE")
    print("=" * 60)
    print(f"\nBaseline output: {baseline_dir}")
    print(f"Current output: {current_dir}")
    print("\nBoth summary.csv and mutation_histos.json should match!")


if __name__ == "__main__":
    main()

