"""command line iterface for rna_map"""

import os
import subprocess
import sys
from pathlib import Path

import cloup

from rna_map.cli_opts import (
    bit_vector_options,
    docker_options,
    main_options,
    mapping_options,
    misc_options,
    parse_cli_args,
)
from rna_map.external import does_program_exist
from rna_map.logger import get_logger, setup_logging
from rna_map.parameters import get_default_params, parse_parameters_from_file
# Pipeline orchestration now handled by Nextflow
from rna_map.settings import get_py_path

log = get_logger("cli")


def get_logo() -> str:
    with open(get_py_path() / "resources" / "logo.txt") as f:
        return "".join(f.readlines())


# docker ######################################################################


def check_docker_image(name: str) -> bool:
    try:
        subprocess.check_output(f"docker image inspect {name}", shell=True)
    except subprocess.CalledProcessError:
        return False
    return True


def run_in_docker(args):
    """Run RNA-MAP in Docker container.

    Args:
        args: Command-line arguments dictionary
    """
    _validate_docker_setup(args)
    file_map = _get_docker_file_mapping()
    file_args = _get_docker_file_args()
    files = ["fasta", "fastq1", "fastq2", "dot_bracket", "param_file"]
    docker_cmd = _build_docker_base_cmd(args)
    dreem_cmd = _build_dreem_cmd()
    dirs = {os.getcwd(): "/data"}
    dcount = 2
    _add_file_mounts(
        args, files, file_map, file_args, dirs, docker_cmd, dreem_cmd, dcount
    )
    docker_cmd += f"{args['docker_image']} {dreem_cmd}"
    _execute_docker_command(docker_cmd)


def _validate_docker_setup(args):
    """Validate Docker setup.

    Args:
        args: Command-line arguments

    Raises:
        ValueError: If Docker is not installed or image not found
    """
    if not does_program_exist("docker"):
        raise ValueError("docker is not installed")
    if not check_docker_image(args["docker_image"]):
        raise ValueError(f"{args['docker_image']} docker image not found")


def _get_docker_file_mapping():
    """Get Docker file name mapping.

    Returns:
        Dictionary mapping file types to Docker file names
    """
    return {
        "dot_bracket": "test.csv",
        "param_file": "test.yml",
        "fasta": "test.fasta",
        "fastq1": "test_mate1.fastq",
        "fastq2": "test_mate2.fastq",
    }


def _get_docker_file_args():
    """Get Docker file argument mapping.

    Returns:
        Dictionary mapping file types to command-line arguments
    """
    return {
        "dot_bracket": "--dot-bracket",
        "param_file": "--param-file",
        "fasta": "--fasta",
        "fastq1": "--fastq1",
        "fastq2": "--fastq2",
    }


def _build_docker_base_cmd(args):
    """Build base Docker command.

    Args:
        args: Command-line arguments

    Returns:
        Base Docker command string
    """
    platform = args["docker_platform"]
    platform_str = f"--platform {platform} " if platform != "" else ""
    return f"docker run --name rna-map-cont {platform_str}-v $(pwd):/data "


def _build_dreem_cmd():
    """Build rna-map command with filtered arguments.

    Returns:
        rna-map command string
    """
    skip_dreem_args = [
        "-fa",
        "--fasta",
        "-fq1",
        "--fastq1",
        "-fq2",
        "--fastq2",
        "-db",
        "--dot-bracket",
        "-pf",
        "--param-file",
        "--docker-image",
        "--docker-platform",
    ]
    keep_args = []
    pos = 1
    while pos < len(sys.argv):
        if sys.argv[pos] in skip_dreem_args:
            pos += 2
            continue
        if sys.argv[pos] == "--docker":
            pos += 1
            continue
        keep_args.append(sys.argv[pos])
        pos += 1
    return "rna-map " + " ".join(keep_args) + " "


def _add_file_mounts(
    args, files, file_map, file_args, dirs, docker_cmd, dreem_cmd, dcount
):
    """Add file mounts to Docker command.

    Args:
        args: Command-line arguments
        files: List of file types
        file_map: File name mapping
        file_args: File argument mapping
        dirs: Directory mapping dictionary (modified in place)
        docker_cmd: Docker command string (modified in place)
        dreem_cmd: rna-map command string (modified in place)
        dcount: Directory counter (modified in place)
    """
    for f in files:
        f_path = args[f]
        if f_path is None or f_path == "":
            continue
        dir_name = os.path.abspath(os.path.dirname(f_path))
        if dir_name == os.path.abspath(os.getcwd()):
            dreem_cmd += f"{file_args[f]} {file_map[f]} "
            continue
        if dir_name not in dirs:
            dirs[dir_name] = f"/data{dcount}"
            docker_cmd += f"-v {dir_name}:/{dirs[dir_name]} "
            dcount += 1
        dreem_cmd += f"{file_args[f]} {dirs[dir_name]}/{file_map[f]} "


def _execute_docker_command(docker_cmd):
    """Execute Docker command.

    Args:
        docker_cmd: Complete Docker command string
    """
    log.info(
        " RUNNING DOCKER #####################################################\n"
        f": {docker_cmd}"
    )
    print(docker_cmd)
    subprocess.call(docker_cmd, shell=True)
    subprocess.call("docker rm rna-map-cont", shell=True)


# cli #########################################################################


@cloup.command()
@main_options()
@mapping_options()
@bit_vector_options()
@docker_options()
@misc_options()
def cli(**args):
    """Rapid analysis of RNA mutational profiling (MaP) experiments."""
    # setup logging
    if args["debug"]:
        setup_logging(debug=True)
        log.info("Debug logging is on")
    else:
        setup_logging()
    # check to see if we are running in docker
    if args["docker"]:
        print("running in docker")
        run_in_docker(args)
        return
    # log commandline options
    log.info("\n" + get_logo())
    log.info("ran at commandline as: ")
    log.info(" ".join(sys.argv))
    # setup parameters
    if args["param_file"] is not None and args["param_preset"] is not None:
        raise ValueError("cannot specify both param_file and param_preset")
    if args["param_preset"] is not None:
        param_path = os.path.join(
            get_py_path(), "resources", "presets", f"{args['param_preset']}.yml"
        )
        if not os.path.isfile(param_path):
            raise ValueError(f"preset {args['param_preset']} does not exist")
        log.info(f"using param preset: {args['param_preset']}")
        params = parse_parameters_from_file(param_path)
    elif args["param_file"] is not None:
        params = parse_parameters_from_file(args["param_file"])
    else:
        params = get_default_params()
    parse_cli_args(params, args)
    
    # Run using Nextflow
    from rna_map.cli.nextflow_wrapper import run_single_sample
    
    # Detect profile (local or slurm)
    profile = "slurm" if os.environ.get("SLURM_JOB_ID") else "local"
    
    # Extract SLURM options if available
    slurm_opts = {}
    if "account" in args:
        slurm_opts["account"] = args.pop("account", None)
    if "partition" in args:
        slurm_opts["partition"] = args.pop("partition", "normal")
    if "max_cpus" in args:
        slurm_opts["max_cpus"] = args.pop("max_cpus", 16)
    
    # Convert params to Nextflow arguments
    fasta = Path(args.pop("fasta"))
    fastq1 = Path(args.pop("fastq1"))
    fastq2 = Path(args.pop("fastq2")) if args.get("fastq2") and args["fastq2"] else None
    dot_bracket = Path(args.pop("dot_bracket")) if args.get("dot_bracket") and args["dot_bracket"] else None
    
    # Extract bit vector and mapping parameters
    bt2_alignment_args = params["map"].get("bt2_alignment_args", "")
    qscore_cutoff = params["bit_vector"].get("qscore_cutoff", 25)
    map_score_cutoff = params["bit_vector"].get("map_score_cutoff", 15)
    summary_output_only = params["bit_vector"].get("summary_output_only", False)
    tg_q_cutoff = params["map"].get("tg_q_cutoff", 20)
    
    run_single_sample(
        fasta=fasta,
        fastq1=fastq1,
        fastq2=fastq2,
        dot_bracket=dot_bracket,
        output_dir=Path(params["dirs"]["output"]),
        skip_fastqc=params["map"]["skip_fastqc"],
        skip_trim_galore=params["map"]["skip_trim_galore"],
        tg_q_cutoff=tg_q_cutoff,
        bt2_alignment_args=bt2_alignment_args,
        qscore_cutoff=qscore_cutoff,
        map_score_cutoff=map_score_cutoff,
        summary_output_only=summary_output_only,
        overwrite=params["overwrite"],
        profile=profile,
        **slurm_opts,
    )


if __name__ == "__main__":
    cli()
