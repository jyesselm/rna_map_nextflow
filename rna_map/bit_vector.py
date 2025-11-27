from pathlib import Path

from rna_map.logger import get_logger

log = get_logger("BIT_VECTOR")


class BitVectorFileWriter:
    def __init__(self, path, name, sequence, data_type, start, end):
        self.start = start
        self.end = end
        self.sequence = sequence
        self.f = open(path / Path(name + "_bitvectors.txt"), "w")
        self.f.write(f"@ref\t{name}\t{sequence}\t{data_type}\n")
        self.f.write(f"@coordinates:\t{start},{end}:{len(sequence)}\n")
        self.f.write("Query_name\tBit_vector\tN_Mutations\n")

    def write_bit_vector(self, q_name, bit_vector):
        n_mutations = 0
        bit_string = ""
        for pos in range(self.start, self.end + 1):
            if pos not in bit_vector:
                bit_string += "."
            else:
                read_bit = bit_vector[pos]
                if read_bit.isalpha():
                    n_mutations += 1
                bit_string += read_bit
        self.f.write(f"{q_name}\t{bit_string}\t{n_mutations}\n")


class BitVectorFileReader:
    def __init__(self):
        pass


# BitVectorIterator moved to rna_map.analysis.bit_vector_iterator

# BitVectorGenerator moved to pipeline.bit_vector_generator
