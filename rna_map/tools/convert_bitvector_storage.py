"""Tool to convert between bit vector storage formats."""

import json
from pathlib import Path
from typing import Any

from rna_map.io.bit_vector_storage import StorageFormat, create_storage_writer
from rna_map.logger import get_logger

log = get_logger("TOOLS.CONVERT_STORAGE")


def parse_text_bitvector_file(file_path: Path) -> tuple[dict[str, Any], list[dict]]:
    """Parse text format bitvector file.

    Args:
        file_path: Path to text bitvector file

    Returns:
        Tuple of (metadata dict, list of bitvector records)
    """
    metadata: dict[str, Any] = {}
    records: list[dict] = []

    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("@ref"):
                parts = line.split("\t")
                if len(parts) >= 4:
                    metadata["name"] = parts[1]
                    metadata["sequence"] = parts[2]
                    metadata["data_type"] = parts[3]
            elif line.startswith("@coordinates:"):
                parts = line.split("\t")[1].split(":")
                coords = parts[0].split(",")
                metadata["start"] = int(coords[0])
                metadata["end"] = int(coords[1])
                metadata["length"] = int(parts[1])
            elif line.startswith("Query_name"):
                continue  # Header line
            else:
                parts = line.split("\t")
                if len(parts) >= 3:
                    records.append(
                        {
                            "qname": parts[0],
                            "bit_vector": parts[1],
                            "n_mutations": int(parts[2]),
                        }
                    )

    return metadata, records


def convert_text_to_json(
    text_file: Path, output_dir: Path, ref_name: str
) -> Path:
    """Convert text format to JSON format.

    Args:
        text_file: Path to text bitvector file
        output_dir: Output directory
        ref_name: Reference sequence name

    Returns:
        Path to created JSON file
    """
    metadata, records = parse_text_bitvector_file(text_file)

    json_writer = create_storage_writer(StorageFormat.JSON, output_dir)

    # Convert text records to JSON format
    for record in records:
        bit_string = record["bit_vector"]
        bit_vector: dict[int, str] = {}
        start = metadata.get("start", 1)

        for i, bit in enumerate(bit_string, start=start):
            if bit != ".":
                bit_vector[i] = bit

        # Create dummy reads for JSON format
        reads = [
            type(
                "Read",
                (),
                {
                    "rname": ref_name,
                    "mapq": 0,
                    "seq": "",
                },
            )()
        ]

        json_writer.write_bit_vector(record["qname"], bit_vector, reads)

    json_writer.close()
    return output_dir / "muts.json"


def convert_json_to_text(
    json_file: Path, output_dir: Path, ref_name: str, sequence: str
) -> Path:
    """Convert JSON format to text format.

    Args:
        json_file: Path to JSON bitvector file
        output_dir: Output directory
        ref_name: Reference sequence name
        sequence: Reference sequence

    Returns:
        Path to created text file
    """
    with open(json_file) as f:
        data = json.load(f)

    if not data:
        raise ValueError("JSON file is empty")

    # Get metadata from first record
    first_record = data[0]
    rname = first_record[0]
    start = 1
    end = len(sequence)

    text_writer = create_storage_writer(
        StorageFormat.TEXT,
        output_dir,
        name=ref_name,
        sequence=sequence,
        data_type="DMS",
        start=start,
        end=end,
    )

    for record in data:
        qname = f"read_{record[0]}"  # JSON doesn't store qname, use index
        muts = record[5] if len(record) > 5 else {}
        dels = record[6] if len(record) > 6 else {}
        ambigs = record[7] if len(record) > 7 else {}

        # Reconstruct bit vector
        bit_vector: dict[int, str] = {}
        for pos, base in muts.items():
            bit_vector[int(pos)] = base
        for pos, _ in dels.items():
            bit_vector[int(pos)] = "1"
        for pos, _ in ambigs.items():
            bit_vector[int(pos)] = "?"

        # Create dummy reads
        reads = [
            type(
                "Read",
                (),
                {
                    "rname": rname,
                    "mapq": record[1] if len(record) > 1 else 0,
                    "seq": "",
                },
            )()
        ]

        text_writer.write_bit_vector(qname, bit_vector, reads)

    text_writer.close()
    return output_dir / f"{ref_name}_bitvectors.txt"


def convert_storage_format(
    input_dir: Path,
    output_dir: Path,
    from_format: StorageFormat,
    to_format: StorageFormat,
    ref_name: str | None = None,
    sequence: str | None = None,
) -> None:
    """Convert bit vector storage between formats.

    Args:
        input_dir: Input directory containing bitvector files
        output_dir: Output directory for converted files
        from_format: Source storage format
        to_format: Target storage format
        ref_name: Reference name (required for JSON->TEXT)
        sequence: Reference sequence (required for JSON->TEXT)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if from_format == StorageFormat.TEXT and to_format == StorageFormat.JSON:
        # Find all text files
        text_files = list(input_dir.glob("*_bitvectors.txt"))
        if not text_files:
            raise ValueError(f"No text bitvector files found in {input_dir}")

        for text_file in text_files:
            ref = ref_name or text_file.stem.replace("_bitvectors", "")
            log.info(f"Converting {text_file.name} to JSON format")
            convert_text_to_json(text_file, output_dir, ref)

    elif from_format == StorageFormat.JSON and to_format == StorageFormat.TEXT:
        json_file = input_dir / "muts.json"
        if not json_file.exists():
            raise ValueError(f"JSON file not found: {json_file}")

        if not ref_name or not sequence:
            raise ValueError(
                "ref_name and sequence required for JSON->TEXT conversion"
            )

        log.info(f"Converting {json_file.name} to TEXT format")
        convert_json_to_text(json_file, output_dir, ref_name, sequence)

    else:
        raise ValueError(f"Conversion from {from_format} to {to_format} not supported")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert bit vector storage formats"
    )
    parser.add_argument("input_dir", type=Path, help="Input directory")
    parser.add_argument("output_dir", type=Path, help="Output directory")
    parser.add_argument(
        "--from-format",
        choices=["text", "json"],
        default="text",
        help="Source format (default: text)",
    )
    parser.add_argument(
        "--to-format",
        choices=["text", "json"],
        default="json",
        help="Target format (default: json)",
    )
    parser.add_argument("--ref-name", help="Reference name (for JSON->TEXT)")
    parser.add_argument("--sequence", help="Reference sequence (for JSON->TEXT)")

    args = parser.parse_args()

    from_fmt = StorageFormat.TEXT if args.from_format == "text" else StorageFormat.JSON
    to_fmt = StorageFormat.TEXT if args.to_format == "text" else StorageFormat.JSON

    convert_storage_format(
        args.input_dir,
        args.output_dir,
        from_fmt,
        to_fmt,
        args.ref_name,
        args.sequence,
    )

