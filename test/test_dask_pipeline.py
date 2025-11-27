"""Tests for Dask pipeline integration."""

from unittest.mock import patch, MagicMock
import os
import pytest

from rna_map.pipeline.dask_pipeline import (
    detect_environment,
    create_dask_cluster,
    run_samples_parallel,
)
from rna_map.pipeline.simple_pipeline import Sample
from pathlib import Path


def test_detect_environment_local():
    """Test environment detection for local machine."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()
        result = detect_environment()
        assert result == "local"


def test_detect_environment_hpc_sbatch():
    """Test environment detection when sbatch is available."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        result = detect_environment()
        assert result == "hpc"


def test_detect_environment_hpc_env_var():
    """Test environment detection via SLURM_JOB_ID."""
    with patch.dict(os.environ, {"SLURM_JOB_ID": "12345"}):
        result = detect_environment()
        assert result == "hpc"


def test_detect_environment_local_no_slurm():
    """Test environment detection when SLURM not available."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()
    with patch.dict(os.environ, {}, clear=True):
        result = detect_environment()
        assert result == "local"


def test_create_dask_cluster_local():
    """Test creating local Dask cluster."""
    with patch("rna_map.pipeline.dask_pipeline._create_local_cluster") as mock_create:
        mock_cluster = MagicMock()
        mock_client = MagicMock()
        mock_create.return_value = (mock_cluster, mock_client)

        cluster, client = create_dask_cluster(
            num_workers=4, environment="local"
        )

        assert cluster == mock_cluster
        assert client == mock_client
        mock_create.assert_called_once()


def test_create_dask_cluster_hpc():
    """Test creating HPC Dask cluster."""
    with patch("rna_map.pipeline.dask_pipeline._create_slurm_cluster") as mock_create:
        mock_cluster = MagicMock()
        mock_client = MagicMock()
        mock_create.return_value = (mock_cluster, mock_client)

        cluster, client = create_dask_cluster(
            num_workers=10, environment="hpc", account="test_account"
        )

        assert cluster == mock_cluster
        assert client == mock_client
        mock_create.assert_called_once()


def test_create_dask_cluster_auto_detect_local():
    """Test auto-detection creates local cluster."""
    with patch("rna_map.pipeline.dask_pipeline.detect_environment") as mock_detect:
        with patch("rna_map.pipeline.dask_pipeline._create_local_cluster") as mock_create:
            mock_detect.return_value = "local"
            mock_cluster = MagicMock()
            mock_client = MagicMock()
            mock_create.return_value = (mock_cluster, mock_client)

            cluster, client = create_dask_cluster(num_workers=4)

            mock_detect.assert_called_once()
            mock_create.assert_called_once()


def test_create_dask_cluster_auto_detect_hpc():
    """Test auto-detection creates HPC cluster."""
    with patch("rna_map.pipeline.dask_pipeline.detect_environment") as mock_detect:
        with patch("rna_map.pipeline.dask_pipeline._create_slurm_cluster") as mock_create:
            mock_detect.return_value = "hpc"
            mock_cluster = MagicMock()
            mock_client = MagicMock()
            mock_create.return_value = (mock_cluster, mock_client)

            cluster, client = create_dask_cluster(
                num_workers=10, account="test_account"
            )

            mock_detect.assert_called_once()
            mock_create.assert_called_once()


def test_run_samples_parallel_mock():
    """Test parallel sample processing with mocked Dask."""
    with patch("rna_map.pipeline.dask_pipeline.create_dask_cluster") as mock_create:
        with patch("rna_map.pipeline.dask_pipeline.Client") as mock_client_class:
            with patch("rna_map.pipeline.dask_pipeline.as_completed") as mock_as_completed:
                mock_client = MagicMock()
                mock_cluster = MagicMock()
                mock_create.return_value = (mock_cluster, mock_client)

                # Mock futures
                mock_future1 = MagicMock()
                mock_future1.result.return_value = {
                    "status": "success",
                    "sample_id": "s1",
                }
                mock_future2 = MagicMock()
                mock_future2.result.return_value = {
                    "status": "success",
                    "sample_id": "s2",
                }

                mock_client.map.return_value = [mock_future1, mock_future2]
                mock_as_completed.return_value = [mock_future1, mock_future2]

                samples = [
                    Sample(
                        sample_id="s1",
                        fasta=Path("test.fasta"),
                        fastq1=Path("test_R1.fastq"),
                    ),
                    Sample(
                        sample_id="s2",
                        fasta=Path("test.fasta"),
                        fastq1=Path("test_R1.fastq"),
                    ),
                ]

                results = run_samples_parallel(
                    samples, num_workers=2, environment="local"
                )

                assert len(results) == 2
                assert all(r["status"] == "success" for r in results)
                mock_client.map.assert_called_once()

