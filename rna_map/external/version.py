"""Version checking utilities for external programs."""

import subprocess

from rna_map.exception import DREEMExternalProgramException
from rna_map.external.base import does_program_exist, run_command


def get_bowtie2_version() -> str:
    """Get the version of Bowtie2.

    Returns:
        Version string

    Raises:
        DREEMExternalProgramException: If Bowtie2 is not found
    """
    if not does_program_exist("bowtie2"):
        raise DREEMExternalProgramException(
            "cannot get bowtie2 version, cannot find the exe"
        )
    output = subprocess.check_output("bowtie2 --version", shell=True).decode("utf8")
    lines = output.split("\n")
    l_spl = lines[0].split()
    return l_spl[-1]


def get_fastqc_version() -> str:
    """Get the version of FastQC.

    Returns:
        Version string

    Raises:
        DREEMExternalProgramException: If FastQC is not found
        ValueError: If version cannot be parsed
    """
    if not does_program_exist("fastqc"):
        raise DREEMExternalProgramException(
            "cannot get fastqc version, cannot find the exe"
        )
    out = run_command("fastqc --version")
    if out.output is None:
        raise ValueError("cannot get fastqc version, no output returned")
    lines = out.output.split("\n")
    if len(lines) < 1:
        raise ValueError(
            f"cannot get fastqc version, output is not valid: {out.output}"
        )
    l_spl = lines[0].split()
    return l_spl[1]


def get_trim_galore_version() -> str:
    """Get the version of Trim Galore.

    Returns:
        Version string

    Raises:
        DREEMExternalProgramException: If Trim Galore is not found
        ValueError: If version cannot be parsed
    """
    if not does_program_exist("trim_galore"):
        raise DREEMExternalProgramException(
            "cannot get trim_galore version, cannot find the exe"
        )
    output = subprocess.check_output("trim_galore --version", shell=True).decode("utf8")
    lines = output.split("\n")
    if len(lines) < 4:
        raise ValueError(
            f"cannot get trim_galore version, output is not valid: {output}"
        )
    for line in lines:
        if line.find("version") != -1:
            l_spl = line.split()
            return l_spl[-1]
    return ""


def get_cutadapt_version() -> str:
    """Get the version of Cutadapt.

    Returns:
        Version string

    Raises:
        DREEMExternalProgramException: If Cutadapt is not found
    """
    if not does_program_exist("cutadapt"):
        raise DREEMExternalProgramException(
            "cannot get cutadapt version, cannot find the exe"
        )
    output = subprocess.check_output("cutadapt --version", shell=True).decode("utf8")
    return output.rstrip().lstrip()
