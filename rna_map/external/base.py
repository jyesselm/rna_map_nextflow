"""Base utilities for external command execution."""

from dataclasses import dataclass
import shutil
import subprocess

from rna_map.exception import DREEMExternalProgramException
from rna_map.logger import get_logger

log = get_logger("EXTERNAL.BASE")


@dataclass(frozen=True, order=True)
class ProgOutput:
    """Stores the output of an external program.

    Attributes:
        output: Standard output from the program
        error: Error output from the program
    """

    output: str | None
    error: str | None


def does_program_exist(prog_name: str) -> bool:
    """Check if a program exists in PATH.

    Args:
        prog_name: Name of the program to check

    Returns:
        True if program exists, False otherwise
    """
    return shutil.which(prog_name) is not None


def run_command(cmd: str) -> ProgOutput:
    """Run a shell command and return the output.

    Args:
        cmd: Command to run

    Returns:
        ProgOutput with output and error messages
    """
    output, error_msg = None, None
    try:
        output = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT
        ).decode("utf8")
    except subprocess.CalledProcessError as exc:
        error_msg = exc.output.decode("utf8")
    return ProgOutput(output, error_msg)


def run_named_command(method_name: str, cmd: str) -> ProgOutput:
    """Run a command with logging.

    Args:
        method_name: Name of the method/command
        cmd: Command to run

    Returns:
        ProgOutput with command results

    Raises:
        DREEMExternalProgramException: If command fails
    """
    log.info(f"running {method_name}")
    log.debug(cmd)
    out = run_command(cmd)
    if out.error is not None:
        log.error(f"error running command: {method_name}")
        raise DREEMExternalProgramException(out.error)
    log.info(f"{method_name} ran without errors")
    return out
