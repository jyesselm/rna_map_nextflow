"""
test running external commands
"""
import os
import pytest
import shutil
from pathlib import Path

# External module was removed - skip these tests
pytestmark = pytest.mark.skip(reason="rna_map.external module was removed in Nextflow-first restructure")

from rna_map.exception import DREEMInputException
# from rna_map.core.inputs import Inputs  # Module removed

from conftest import TEST_DATA_DIR


def setup_directories(cur_dir):
    """
    Set up the directory for testing
    """
    os.makedirs(Path(cur_dir) / "input")
    os.makedirs(Path(cur_dir) / "log")
    os.makedirs(Path(cur_dir) / "output")
    os.makedirs(Path(cur_dir) / "output" / "Mapping_Files")
    os.makedirs(Path(cur_dir) / "output" / "BitVector_Files")


def remove_directories(cur_dir):
    """
    Remove the directory for testing
    """
    shutil.rmtree(Path(cur_dir) / "input")
    shutil.rmtree(Path(cur_dir) / "log")
    shutil.rmtree(Path(cur_dir) / "output")


def get_test_inputs_paired():
    """
    Get the test inputs
    """
    test_data_dir = TEST_DATA_DIR / "case_1"
    # Return dict since Inputs class was removed
    return {
        "fasta": test_data_dir / "test.fasta",
        "fastq1": test_data_dir / "test_mate1.fastq",
        "fastq2": test_data_dir / "test_mate2.fastq",
    }


# tests #######################################################################


def test_does_program_exist():
    """
    test does_program_exist
    """
    assert does_program_exist("ls")
    assert not does_program_exist("fake")


def test_get_bowtie2_version():
    """
    test get_bowtie2_version
    """
    version = get_bowtie2_version()
    # assert version == "2.4.5"


def test_get_fastqc_version():
    """
    test get_fastqc_version
    """
    try:
        version = get_fastqc_version()
    except:
        pytest.fail("get_fastqc_version() raised ExceptionType unexpectedly!")
    # assert version == "v0.11.9"


def test_get_trim_galore_version():
    """
    test get_trim_galore_version
    """
    try:
        version = get_trim_galore_version()
    except:
        pytest.fail("get_trim_galore_version() raised ExceptionType unexpectedly!")


# assert version == "0.6.6"


def test_get_cutadapt_version():
    """
    test get_cutadapt_version
    """
    version = get_cutadapt_version()
    # assert version == "1.18" 


def test_run_command():
    """
    test run_command
    """
    cmd = "ls -l"
    out = run_command(cmd)
    assert out.output is not None
    assert out.error is None
    cmd = "fake"
    out = run_command(cmd)
    assert out.output is None
    assert out.error is not None


def test_run_fastqc():
    """
    test run_fastqc
    """
    setup_directories(os.getcwd())
    ins = get_test_inputs_paired()
    run_fastqc(ins["fastq1"], ins["fastq2"], Path("output/Mapping_Files/"))
    remove_directories(os.getcwd())


def test_run_trim_galore():
    """
    test run_trim_galore
    """
    setup_directories(os.getcwd())
    ins = get_test_inputs_paired()
    run_trim_galore(ins["fastq1"], ins["fastq2"], Path("output/Mapping_Files/"))
    remove_directories(os.getcwd())


def test_run_bowtie_build():
    """
    test run_trim_glore
    """
    setup_directories(os.getcwd())
    ins = get_test_inputs_paired()
    run_bowtie_build(ins["fasta"], "input")
    assert os.path.isfile(Path("input/test.1.bt2"))
    remove_directories(os.getcwd())


def test_validate_bt2_args():
    """
    test validate_bt2_args
    """
    args = "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p 16"
    try:
        validate_bowtie2_args(args)
    except DREEMInputException as exc:
        pytest.fail(exc)


# TODO make sure that I check for core options that should not be included
# such as -x -1 -2 -S
def test_validate_bt2_args_exceptions():
    """
    test validate_bt2_args exceptions
    """
    args = ""
    validate_bowtie2_args(args)
    # invalid boolean argument
    args = "--fake;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p 16"
    with pytest.raises(DREEMInputException):
        validate_bowtie2_args(args)
    # invalid integer argument
    args = "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-fake 16"
    with pytest.raises(DREEMInputException):
        validate_bowtie2_args(args)
    # invalid argument type
    args = "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p test"
    with pytest.raises(DREEMInputException):
        validate_bowtie2_args(args)


def test_bowtie_alignment():
    """
    test bowtie alignment
    """
    setup_directories(os.getcwd())
    ins = get_test_inputs_paired()
    run_bowtie_build(ins["fasta"], "input")
    args = "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p 16"
    run_bowtie_alignment(
        ins["fasta"], ins["fastq1"], ins["fastq2"], "input", "output/Mapping_Files", args
    )
    assert os.path.isfile(Path("output/Mapping_Files/aligned.sam"))
    assert os.path.getsize(Path("output/Mapping_Files/aligned.sam")) > 1000
    remove_directories(os.getcwd())
