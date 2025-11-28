#include "bit_vector_generator.hpp"
#include <regex>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <cctype>

namespace rna_map {

BitVectorGenerator::BitVectorGenerator(int qscore_cutoff, int num_of_surbases)
    : qscore_cutoff_(qscore_cutoff), num_of_surbases_(num_of_surbases) {}

std::vector<CigarOp> BitVectorGenerator::parse_cigar(const std::string& cigar) {
    std::vector<CigarOp> ops;
    
    // Handle empty CIGAR string
    if (cigar.empty() || cigar == "*") {
        return ops;
    }
    
    // Valid CIGAR operations: M, I, D, N, S, H, P, =, X
    // Pattern matches: one or more digits followed by a valid CIGAR operation
    std::regex pattern(R"((\d+)([MIDNSHPX=]))");
    std::sregex_iterator iter(cigar.begin(), cigar.end(), pattern);
    std::sregex_iterator end;
    
    for (; iter != end; ++iter) {
        std::smatch match = *iter;
        CigarOp op;
        op.length = std::stoi(match[1].str());
        op.operation = match[2].str()[0];
        
        // Validate length is positive
        if (op.length <= 0) {
            continue;
        }
        
        ops.push_back(op);
    }
    
    // Validate that we parsed at least one operation
    // If the CIGAR string is non-empty but we got no operations,
    // it might be malformed, but we'll return empty vector
    // (caller should handle this appropriately)
    
    return ops;
}

void BitVectorGenerator::process_match(
    std::unordered_map<int, char>& bitvector,
    const std::string& read_seq,
    const std::string& q_scores,
    const std::string& ref_seq,
    int& ref_pos,
    int& read_pos,
    int length,
    const std::unordered_map<char, int>& phred_qscores
) {
    int ref_len = static_cast<int>(ref_seq.length());
    int read_len = static_cast<int>(read_seq.length());
    int qual_len = static_cast<int>(q_scores.length());
    
    for (int i = 0; i < length; ++i) {
        // Bounds checking
        if (read_pos >= read_len || read_pos >= qual_len) break;
        if (ref_pos < 1 || ref_pos > ref_len) {
            ref_pos++;
            read_pos++;
            continue;
        }
        
        char q_char = q_scores[read_pos];
        int qscore = (phred_qscores.find(q_char) != phred_qscores.end()) 
                     ? phred_qscores.at(q_char) : 0;
        
        if (qscore > qscore_cutoff_) {
            if (read_seq[read_pos] != ref_seq[ref_pos - 1]) {
                bitvector[ref_pos] = read_seq[read_pos];
            } else {
                bitvector[ref_pos] = BitVectorSymbols::NOMUT_BIT;
            }
        } else {
            bitvector[ref_pos] = BitVectorSymbols::AMBIG_INFO;
        }
        ref_pos++;
        read_pos++;
    }
}

void BitVectorGenerator::process_deletion(
    std::unordered_map<int, char>& bitvector,
    const std::string& ref_seq,
    int& ref_pos,
    int length
) {
    // Mark positions before deletion end as ambiguous
    for (int i = 0; i < length - 1; ++i) {
        bitvector[ref_pos] = BitVectorSymbols::AMBIG_INFO;
        ref_pos++;
    }
    
    // Check if deletion is ambiguous
    bool is_ambig = is_deletion_ambiguous(ref_seq, ref_pos, length);
    if (is_ambig) {
        bitvector[ref_pos] = BitVectorSymbols::AMBIG_INFO;
    } else {
        bitvector[ref_pos] = BitVectorSymbols::DEL_BIT;
    }
    ref_pos++;
}

void BitVectorGenerator::process_soft_clip(
    std::unordered_map<int, char>& bitvector,
    int& ref_pos,
    int& read_pos,
    int length,
    bool is_last_op
) {
    read_pos += length;
    if (is_last_op) {
        for (int i = 0; i < length; ++i) {
            bitvector[ref_pos] = BitVectorSymbols::MISS_INFO;
            ref_pos++;
        }
    }
}

bool BitVectorGenerator::is_deletion_ambiguous(
    const std::string& ref_seq,
    int pos,
    int length
) {
    int seq_len = static_cast<int>(ref_seq.length());
    if (seq_len == 0 || pos < 1 || pos > seq_len) {
        return false;
    }
    
    int orig_del_start = pos - length + 1;
    int orig_sur_start = orig_del_start - num_of_surbases_;
    int orig_sur_end = pos + num_of_surbases_;
    
    // Extract surrounding sequence (handle bounds checking)
    // Python: ref_seq[orig_sur_start - 1 : orig_del_start - 1] + ref_seq[i:orig_sur_end]
    // First part: ref_seq[orig_sur_start - 1 : orig_del_start - 1] (exclusive end)
    int start_idx_raw = orig_sur_start - 1;
    int end_idx = orig_del_start - 1;
    int len1 = 0;
    int start_idx = 0;
    
    if (start_idx_raw < 0) {
        // Negative index: Python wraps it to seq_len + start_idx_raw
        int wrapped_start = seq_len + start_idx_raw;
        if (wrapped_start >= end_idx) {
            len1 = 0;  // Empty string (wrapped start >= end)
        } else {
            // Valid slice: Python returns ref_seq[0:end_idx] when start is negative and wrapped < end
            start_idx = 0;
            len1 = std::min(end_idx, seq_len);
        }
    } else {
        start_idx = std::min(start_idx_raw, seq_len);
        len1 = std::max(0, std::min(end_idx, seq_len) - start_idx);
    }
    
    // Second part: ref_seq[i:orig_sur_end] - Python uses pos directly as 0-based index (exclusive end)
    int pos_idx = std::max(0, std::min(pos, seq_len));  // pos used directly as 0-based index
    int end_idx2 = std::min(orig_sur_end, seq_len);
    int len2 = std::max(0, end_idx2 - pos_idx);
    
    std::string part1 = (len1 > 0) ? ref_seq.substr(start_idx, len1) : "";
    std::string orig_sur_seq = part1 + ref_seq.substr(pos_idx, len2);
    
    // Check alternative deletion positions
    for (int new_del_end = pos - length; new_del_end <= pos + length; ++new_del_end) {
        if (new_del_end == pos) continue;
        if (new_del_end < 1 || new_del_end > seq_len) continue;
        
        int new_del_start = new_del_end - length + 1;
        if (new_del_start < 1) continue;
        
        // First part: ref_seq[orig_sur_start - 1 : new_del_start - 1]
        int new_start_idx_raw = orig_sur_start - 1;
        int new_end_idx = new_del_start - 1;
        int new_len1 = 0;
        int new_start_idx = 0;
        
        if (new_start_idx_raw < 0) {
            int wrapped_start = seq_len + new_start_idx_raw;
            if (wrapped_start >= new_end_idx) {
                new_len1 = 0;
            } else {
                new_start_idx = 0;
                new_len1 = std::min(new_end_idx, seq_len);
            }
        } else {
            new_start_idx = std::min(new_start_idx_raw, seq_len);
            new_len1 = std::max(0, std::min(new_end_idx, seq_len) - new_start_idx);
        }
        
        // Second part: ref_seq[new_del_end:orig_sur_end] - Python uses new_del_end directly as 0-based index
        int new_pos_idx = std::max(0, std::min(new_del_end, seq_len));  // new_del_end used directly as 0-based
        int new_end_idx2 = std::min(orig_sur_end, seq_len);
        int new_len2 = std::max(0, new_end_idx2 - new_pos_idx);
        
        std::string new_part1 = (new_len1 > 0) ? ref_seq.substr(new_start_idx, new_len1) : "";
        std::string sur_seq = new_part1 + ref_seq.substr(new_pos_idx, new_len2);
        
        if (sur_seq == orig_sur_seq) {
            return true;
        }
    }
    return false;
}

bool BitVectorGenerator::test_is_deletion_ambiguous(
    const std::string& ref_seq,
    int pos,
    int length
) {
    return is_deletion_ambiguous(ref_seq, pos, length);
}

std::unordered_map<int, char> BitVectorGenerator::generate_single(
    const AlignedRead& read,
    const std::string& ref_seq,
    const std::unordered_map<char, int>& phred_qscores
) {
    std::unordered_map<int, char> bitvector;
    int ref_pos = read.pos;
    int read_pos = 0;
    
    auto cigar_ops = parse_cigar(read.cigar);
    
    for (size_t i = 0; i < cigar_ops.size(); ++i) {
        const auto& op = cigar_ops[i];
        bool is_last = (i == cigar_ops.size() - 1);
        
        switch (op.operation) {
            case 'M':  // Match or mismatch
            case '=':  // Sequence match
            case 'X':  // Sequence mismatch
                process_match(bitvector, read.seq, read.qual, ref_seq,
                            ref_pos, read_pos, op.length, phred_qscores);
                break;
            case 'D':  // Deletion
            case 'N':  // Skipped region (similar to deletion)
                process_deletion(bitvector, ref_seq, ref_pos, op.length);
                break;
            case 'I':  // Insertion
                read_pos += op.length;
                break;
            case 'S':  // Soft clipping
                process_soft_clip(bitvector, ref_pos, read_pos, op.length, is_last);
                break;
            case 'H':  // Hard clipping (doesn't consume read or reference)
            case 'P':  // Padding (doesn't consume read or reference)
                // Skip these operations - they don't affect alignment
                break;
            default:
                // Unknown operation - skip (should not happen with valid regex)
                break;
        }
    }
    
    return bitvector;
}

std::unordered_map<int, char> BitVectorGenerator::merge_paired(
    const std::unordered_map<int, char>& bv1,
    const std::unordered_map<int, char>& bv2
) {
    std::unordered_map<int, char> merged(bv1);
    
    for (const auto& [pos, bit] : bv2) {
        if (merged.find(pos) == merged.end()) {
            merged[pos] = bit;
        } else if (merged[pos] != bit) {
            merged[pos] = resolve_conflict(merged[pos], bit);
        }
    }
    
    return merged;
}

char BitVectorGenerator::resolve_conflict(char bit1, char bit2) {
    std::string bits = {bit1, bit2};
    
    // If one is no mutation, prefer no mutation
    if (bits.find(BitVectorSymbols::NOMUT_BIT) != std::string::npos) {
        return BitVectorSymbols::NOMUT_BIT;
    }
    
    // If one is ambiguous, prefer the other
    if (bits.find(BitVectorSymbols::AMBIG_INFO) != std::string::npos) {
        return (bit1 == BitVectorSymbols::AMBIG_INFO) ? bit2 : bit1;
    }
    
    // If one is missing, prefer the other
    if (bits.find(BitVectorSymbols::MISS_INFO) != std::string::npos) {
        return (bit1 == BitVectorSymbols::MISS_INFO) ? bit2 : bit1;
    }
    
    // If both are bases and different, mark as ambiguous
    if (bits.find('A') != std::string::npos || bits.find('C') != std::string::npos ||
        bits.find('G') != std::string::npos || bits.find('T') != std::string::npos) {
        if (is_mutation_vs_deletion(bit1, bit2)) {
            return BitVectorSymbols::AMBIG_INFO;
        }
        // Two different bases
        if ((bit1 == 'A' || bit1 == 'C' || bit1 == 'G' || bit1 == 'T') &&
            (bit2 == 'A' || bit2 == 'C' || bit2 == 'G' || bit2 == 'T') &&
            bit1 != bit2) {
            return BitVectorSymbols::AMBIG_INFO;
        }
    }
    
    return bit1;
}

bool BitVectorGenerator::is_mutation_vs_deletion(char bit1, char bit2) {
    bool bit1_is_base = (bit1 == 'A' || bit1 == 'C' || bit1 == 'G' || bit1 == 'T');
    bool bit2_is_base = (bit2 == 'A' || bit2 == 'C' || bit2 == 'G' || bit2 == 'T');
    bool bit1_is_del = (bit1 == BitVectorSymbols::DEL_BIT);
    bool bit2_is_del = (bit2 == BitVectorSymbols::DEL_BIT);
    
    return (bit1_is_del && bit2_is_base) || (bit1_is_base && bit2_is_del);
}

std::unordered_map<int, char> BitVectorGenerator::generate_paired(
    const AlignedRead& read1,
    const AlignedRead& read2,
    const std::string& ref_seq,
    const std::unordered_map<char, int>& phred_qscores
) {
    auto bv1 = generate_single(read1, ref_seq, phred_qscores);
    auto bv2 = generate_single(read2, ref_seq, phred_qscores);
    return merge_paired(bv1, bv2);
}

// Note: SAM file parsing is handled in Python, C++ only processes bit vectors

} // namespace rna_map

