"""Tests for pipeline CLI commands."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from click.testing import CliRunner

from rna_map.cli.pipeline import pipeline
from rna_map.pipeline.simple_pipeline import Sample


@pytest.fixture
def mock_samples():
    """Create mock samples for testing."""
    return [
        Sample(
            sample_id="test1",
            fasta=Path("test1.fasta"),
            fastq1=Path("test1_R1.fastq"),
            fastq2=Path("test1_R2.fastq"),
            dot_bracket=Path("test1.db"),
        ),
        Sample(
            sample_id="test2",
            fasta=Path("test2.fasta"),
            fastq1=Path("test2_R1.fastq"),
            fastq2=None,
            dot_bracket=None,
        ),
    ]


@pytest.fixture
def mock_samples_csv(tmp_path):
    """Create a mock samples CSV file."""
    csv_path = tmp_path / "samples.csv"
    df = pd.DataFrame([
        {
            "sample_id": "test1",
            "fasta": "test1.fasta",
            "fastq1": "test1_R1.fastq",
            "fastq2": "test1_R2.fastq",
            "dot_bracket": "test1.db",
        },
        {
            "sample_id": "test2",
            "fasta": "test2.fasta",
            "fastq1": "test2_R1.fastq",
            "fastq2": "",
            "dot_bracket": "",
        },
    ])
    df.to_csv(csv_path, index=False)
    return csv_path


def test_demultiplex_command(mock_samples, tmp_path):
    """Test demultiplex command."""
    fastq1 = tmp_path / "test_R1.fastq"
    fastq2 = tmp_path / "test_R2.fastq"
    barcodes_csv = tmp_path / "barcodes.csv"
    output_dir = tmp_path / "demultiplexed"

    # Create mock files
    fastq1.write_text("@read1\nACGT\n+\nIIII\n")
    fastq2.write_text("@read1\nACGT\n+\nIIII\n")
    barcodes_df = pd.DataFrame([
        {"barcode": "AAAA", "sample_id": "test1"},
        {"barcode": "TTTT", "sample_id": "test2"},
    ])
    barcodes_df.to_csv(barcodes_csv, index=False)

    runner = CliRunner()
    with patch("rna_map.cli.pipeline.demultiplex_fastq") as mock_demux:
        mock_demux.return_value = mock_samples
        with patch("pandas.DataFrame.to_csv") as mock_csv:
            result = runner.invoke(
                pipeline,
                [
                    "demultiplex",
                    str(fastq1),
                    str(fastq2),
                    str(barcodes_csv),
                    "--output-dir",
                    str(output_dir),
                ],
            )
            assert result.exit_code == 0
            mock_demux.assert_called_once()
            mock_csv.assert_called_once()


def test_run_command_sequential(mock_samples_csv):
    """Test run command with sequential processing."""
    runner = CliRunner()
    with patch("rna_map.cli.pipeline.process_samples") as mock_process:
        mock_process.return_value = [
            {"sample_id": "test1", "status": "success"},
            {"sample_id": "test2", "status": "success"},
        ]
        with patch("pandas.DataFrame.to_csv") as mock_csv:
            result = runner.invoke(
                pipeline,
                [
                    "run",
                    str(mock_samples_csv),
                    "--num-workers",
                    "10",
                    "--sequential",
                ],
            )
            assert result.exit_code == 0
            mock_process.assert_called_once()
            mock_csv.assert_called_once()


def test_run_command_parallel(mock_samples_csv):
    """Test run command with parallel processing."""
    runner = CliRunner()
    with patch("rna_map.cli.pipeline.run_samples_parallel") as mock_parallel:
        mock_parallel.return_value = [
            {"sample_id": "test1", "status": "success"},
            {"sample_id": "test2", "status": "success"},
        ]
        with patch("pandas.DataFrame.to_csv") as mock_csv:
            result = runner.invoke(
                pipeline,
                [
                    "run",
                    str(mock_samples_csv),
                    "--num-workers",
                    "10",
                ],
            )
            assert result.exit_code == 0
            mock_parallel.assert_called_once()
            mock_csv.assert_called_once()


def test_full_command(tmp_path):
    """Test full pipeline command."""
    fastq1 = tmp_path / "test_R1.fastq"
    fastq2 = tmp_path / "test_R2.fastq"
    barcodes_csv = tmp_path / "barcodes.csv"

    # Create mock files
    fastq1.write_text("@read1\nACGT\n+\nIIII\n")
    fastq2.write_text("@read1\nACGT\n+\nIIII\n")
    barcodes_df = pd.DataFrame([
        {"barcode": "AAAA", "sample_id": "test1"},
    ])
    barcodes_df.to_csv(barcodes_csv, index=False)

    mock_samples = [
        Sample(
            sample_id="test1",
            fasta=Path("test1.fasta"),
            fastq1=Path("test1_R1.fastq"),
            fastq2=Path("test1_R2.fastq"),
        ),
    ]

    runner = CliRunner()
    with patch("rna_map.cli.pipeline.demultiplex_fastq") as mock_demux:
        mock_demux.return_value = mock_samples
        with patch("rna_map.cli.pipeline.run_samples_parallel") as mock_parallel:
            mock_parallel.return_value = [
                {"sample_id": "test1", "status": "success"},
            ]
            with patch("pandas.DataFrame.to_csv") as mock_csv:
                result = runner.invoke(
                    pipeline,
                    [
                        "full",
                        str(fastq1),
                        str(fastq2),
                        str(barcodes_csv),
                        "--num-workers",
                        "10",
                    ],
                )
                assert result.exit_code == 0
                mock_demux.assert_called_once()
                mock_parallel.assert_called_once()
                assert mock_csv.call_count == 1

