"""
test sam module
"""
import os
from pathlib import Path
from rna_map.io.sam import SingleSamIterator
from rna_map.io.fasta import fasta_to_dict

from conftest import TEST_DATA_DIR


def test_single_sam_iterator():
    fa_path = TEST_DATA_DIR / "case_1" / "test.fasta"
    ref_seqs = fasta_to_dict(fa_path)
    sam_path = TEST_DATA_DIR / "case_1" / "output" / "Mapping_Files" / "aligned.sam"
    sam_iter = SingleSamIterator(sam_path, ref_seqs)
    read = next(sam_iter)[0]
    assert read.qname == "FS10000899:22:BPG61606-0731:1:1101:1200:1000"
    assert read.flag == "0"
    assert read.rname == "mttr-6-alt-h3"
    assert read.pos == 1
    assert read.mapq == 44
    assert read.cigar == "134M12S"
    assert read.rnext == "*"
    assert read.pnext == 0
    assert read.tlen == 0
