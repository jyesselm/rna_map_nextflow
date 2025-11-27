"""Integration tests for new scalable pipeline.

Tests the full pipeline workflow including:
- Sample processing
- Sequential processing
- Parallel processing with Dask (mocked)
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from rna_map.core.config import BitVectorConfig, MappingConfig
from rna_map.pipeline.dask_pipeline import run_samples_parallel
from rna_map.pipeline.simple_pipeline import (
    Sample,
    process_samples,
    run_rna_map_sample,
)

TEST_DIR = Path(__file__).parent
TEST_RESOURCES = TEST_DIR / "resources" / "case_1"


@pytest.fixture
def temp_dir():
    """Create temporary directory for test output."""
    temp = Path(tempfile.mkdtemp(prefix="rna_map_pipeline_test_"))
    yield temp
    if temp.exists():
        shutil.rmtree(temp)


@pytest.fixture
def test_sample(temp_dir):
    """Create a test sample from test resources."""
    return Sample(
        sample_id="test_sample",
        fasta=TEST_RESOURCES / "test.fasta",
        fastq1=TEST_RESOURCES / "test_mate1.fastq",
        fastq2=TEST_RESOURCES / "test_mate2.fastq",
        dot_bracket=TEST_RESOURCES / "test.csv",
        output_dir=temp_dir / "test_sample",
    )


@pytest.fixture
def test_samples(temp_dir):
    """Create multiple test samples."""
    return [
        Sample(
            sample_id=f"test_sample_{i}",
            fasta=TEST_RESOURCES / "test.fasta",
            fastq1=TEST_RESOURCES / "test_mate1.fastq",
            fastq2=TEST_RESOURCES / "test_mate2.fastq",
            dot_bracket=TEST_RESOURCES / "test.csv",
            output_dir=temp_dir / f"test_sample_{i}",
        )
        for i in range(2)
    ]


from rna_map.pipeline.functions import check_program_versions


def has_external_tools():
    """Check if external tools are available."""
    try:
        check_program_versions()
        return True
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.skipif(
    not has_external_tools(),
    reason="External tools not available",
)
def test_run_rna_map_sample_integration(test_sample):
    """Test running RNA MAP on a single sample (integration test)."""
    result = run_rna_map_sample(
        sample=test_sample,
        overwrite=True,
    )

    assert result["status"] == "success"
    assert "sample_id" in result
    assert result["sample_id"] == "test_sample"
    assert "output_dir" in result
    assert Path(result["output_dir"]).exists()

    # Check that output files exist
    output_dir = Path(result["output_dir"])
    bitvector_dir = output_dir / "BitVector_Files"
    assert bitvector_dir.exists()
    assert (bitvector_dir / "summary.csv").exists()


@pytest.mark.integration
@pytest.mark.skipif(
    not has_external_tools(),
    reason="External tools not available",
)
def test_process_samples_sequential_integration(test_samples, temp_dir):
    """Test processing multiple samples sequentially (integration test)."""
    results = process_samples(
        samples=test_samples,
        overwrite=True,
    )

    assert len(results) == 2
    assert all(r["status"] == "success" for r in results)
    assert all("sample_id" in r for r in results)
    assert all("output_dir" in r for r in results)

    # Check that all output directories exist
    for result in results:
        output_dir = Path(result["output_dir"])
        assert output_dir.exists()
        bitvector_dir = output_dir / "BitVector_Files"
        assert bitvector_dir.exists()
        assert (bitvector_dir / "summary.csv").exists()


@pytest.mark.integration
def test_process_samples_sequential_mock(test_samples):
    """Test processing multiple samples sequentially (mocked, no external tools)."""
    with patch("rna_map.pipeline.simple_pipeline.run_rna_map_sample") as mock_run:
        mock_run.return_value = {
            "status": "success",
            "sample_id": "test",
            "output_dir": "/tmp/test",
        }

        results = process_samples(
            samples=test_samples,
            overwrite=True,
        )

        assert len(results) == 2
        assert mock_run.call_count == 2
        assert all(r["status"] == "success" for r in results)


@pytest.mark.integration
def test_run_samples_parallel_mock(test_samples):
    """Test parallel processing with Dask (mocked cluster)."""
    from unittest.mock import MagicMock

    with patch("rna_map.pipeline.dask_pipeline.create_dask_cluster") as mock_create:
        with patch("rna_map.pipeline.dask_pipeline.as_completed") as mock_as_completed:
            # Mock client
            mock_client = MagicMock()
            mock_client.close = lambda: None

            # Mock cluster
            mock_cluster = MagicMock()
            mock_cluster.close = lambda: None
            mock_create.return_value = (mock_cluster, mock_client)

            # Mock futures
            mock_future1 = MagicMock()
            mock_future1.result.return_value = {
                "status": "success",
                "sample_id": "test_sample_0",
                "output_dir": "/tmp/test",
            }
            mock_future2 = MagicMock()
            mock_future2.result.return_value = {
                "status": "success",
                "sample_id": "test_sample_1",
                "output_dir": "/tmp/test",
            }

            mock_client.map.return_value = [mock_future1, mock_future2]
            mock_as_completed.return_value = [mock_future1, mock_future2]

            results = run_samples_parallel(
                samples=test_samples,
                num_workers=2,
                overwrite=True,
            )

            assert len(results) == 2
            assert all(r["status"] == "success" for r in results)
            mock_client.map.assert_called_once()


@pytest.mark.integration
def test_samples_csv_roundtrip(temp_dir):
    """Test creating samples from CSV and saving results back to CSV."""
    # Create a samples CSV
    samples_df = pd.DataFrame([
        {
            "sample_id": "test1",
            "fasta": str(TEST_RESOURCES / "test.fasta"),
            "fastq1": str(TEST_RESOURCES / "test_mate1.fastq"),
            "fastq2": str(TEST_RESOURCES / "test_mate2.fastq"),
            "dot_bracket": str(TEST_RESOURCES / "test.csv"),
        },
        {
            "sample_id": "test2",
            "fasta": str(TEST_RESOURCES / "test.fasta"),
            "fastq1": str(TEST_RESOURCES / "test_mate1.fastq"),
            "fastq2": str(TEST_RESOURCES / "test_mate2.fastq"),
            "dot_bracket": "",
        },
    ])
    samples_csv = temp_dir / "samples.csv"
    samples_df.to_csv(samples_csv, index=False)

    # Load samples from CSV
    df = pd.read_csv(samples_csv)
    samples = [
        Sample(
            sample_id=row["sample_id"],
            fasta=Path(row["fasta"]),
            fastq1=Path(row["fastq1"]),
            fastq2=Path(row["fastq2"]) if pd.notna(row.get("fastq2")) and row.get("fastq2") else None,
            dot_bracket=Path(row["dot_bracket"])
            if pd.notna(row.get("dot_bracket")) and row.get("dot_bracket")
            else None,
        )
        for _, row in df.iterrows()
    ]

    assert len(samples) == 2
    assert samples[0].sample_id == "test1"
    assert samples[1].sample_id == "test2"

    # Create mock results and save to CSV
    results = [
        {"sample_id": s.sample_id, "status": "success", "output_dir": str(temp_dir / s.sample_id)}
        for s in samples
    ]
    results_df = pd.DataFrame(results)
    results_csv = temp_dir / "results.csv"
    results_df.to_csv(results_csv, index=False)

    # Verify results CSV
    assert results_csv.exists()
    results_df_loaded = pd.read_csv(results_csv)
    assert len(results_df_loaded) == 2
    assert all(results_df_loaded["status"] == "success")

