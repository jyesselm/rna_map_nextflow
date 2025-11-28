#ifndef BIT_VECTOR_GENERATOR_HPP
#define BIT_VECTOR_GENERATOR_HPP

#include <string>
#include <unordered_map>
#include <vector>
#include <memory>

namespace rna_map {

// Bit vector symbols
struct BitVectorSymbols {
    static constexpr char MISS_INFO = '*';
    static constexpr char AMBIG_INFO = '?';
    static constexpr char NOMUT_BIT = '0';
    static constexpr char DEL_BIT = '1';
};

// Aligned read structure
struct AlignedRead {
    std::string qname;
    std::string flag;
    std::string rname;
    int pos;
    int mapq;
    std::string cigar;
    std::string rnext;
    int pnext;
    int tlen;
    std::string seq;
    std::string qual;
    std::string md_string;
};

// CIGAR operation
struct CigarOp {
    int length;
    char operation;
};

// Bit vector result
struct BitVectorResult {
    std::unordered_map<int, char> data;
    std::vector<AlignedRead> reads;
};

// Bit vector generator class
class BitVectorGenerator {
public:
    BitVectorGenerator(
        int qscore_cutoff = 25,
        int num_of_surbases = 10
    );
    
    // Generate bit vector from single read
    std::unordered_map<int, char> generate_single(
        const AlignedRead& read,
        const std::string& ref_seq,
        const std::unordered_map<char, int>& phred_qscores
    );
    
    // Generate bit vector from paired reads
    std::unordered_map<int, char> generate_paired(
        const AlignedRead& read1,
        const AlignedRead& read2,
        const std::string& ref_seq,
        const std::unordered_map<char, int>& phred_qscores
    );
    
    // Public test method for debugging
    bool test_is_deletion_ambiguous(
        const std::string& ref_seq,
        int pos,
        int length
    );

private:
    int qscore_cutoff_;
    int num_of_surbases_;
    
    // Parse CIGAR string
    // Valid operations: M (match), I (insertion), D (deletion), N (skipped),
    //                   S (soft clip), H (hard clip), P (padding), = (match), X (mismatch)
    // Returns empty vector if CIGAR string is empty or malformed
    std::vector<CigarOp> parse_cigar(const std::string& cigar);
    
    // Process match operation
    void process_match(
        std::unordered_map<int, char>& bitvector,
        const std::string& read_seq,
        const std::string& q_scores,
        const std::string& ref_seq,
        int& ref_pos,
        int& read_pos,
        int length,
        const std::unordered_map<char, int>& phred_qscores
    );
    
    // Process deletion operation
    void process_deletion(
        std::unordered_map<int, char>& bitvector,
        const std::string& ref_seq,
        int& ref_pos,
        int length
    );
    
    // Process soft clip operation
    void process_soft_clip(
        std::unordered_map<int, char>& bitvector,
        int& ref_pos,
        int& read_pos,
        int length,
        bool is_last_op
    );
    
    // Check if deletion is ambiguous
    bool is_deletion_ambiguous(
        const std::string& ref_seq,
        int pos,
        int length
    );
    
    // Merge paired bit vectors
    std::unordered_map<int, char> merge_paired(
        const std::unordered_map<int, char>& bv1,
        const std::unordered_map<int, char>& bv2
    );
    
    // Resolve bit conflict
    char resolve_conflict(char bit1, char bit2);
    
    // Check if mutation vs deletion
    bool is_mutation_vs_deletion(char bit1, char bit2);
};

} // namespace rna_map

#endif // BIT_VECTOR_GENERATOR_HPP

