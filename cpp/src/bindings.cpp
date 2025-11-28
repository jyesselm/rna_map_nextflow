#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "bit_vector_generator.hpp"

namespace py = pybind11;
using namespace rna_map;

PYBIND11_MODULE(bit_vector_cpp, m) {
    m.doc() = "C++ bit vector generation module";
    
    // AlignedRead
    py::class_<AlignedRead>(m, "AlignedRead")
        .def(py::init<>())
        .def_readwrite("qname", &AlignedRead::qname)
        .def_readwrite("flag", &AlignedRead::flag)
        .def_readwrite("rname", &AlignedRead::rname)
        .def_readwrite("pos", &AlignedRead::pos)
        .def_readwrite("mapq", &AlignedRead::mapq)
        .def_readwrite("cigar", &AlignedRead::cigar)
        .def_readwrite("rnext", &AlignedRead::rnext)
        .def_readwrite("pnext", &AlignedRead::pnext)
        .def_readwrite("tlen", &AlignedRead::tlen)
        .def_readwrite("seq", &AlignedRead::seq)
        .def_readwrite("qual", &AlignedRead::qual)
        .def_readwrite("md_string", &AlignedRead::md_string);
    
    // BitVectorResult
    py::class_<BitVectorResult>(m, "BitVectorResult")
        .def(py::init<>())
        .def_readwrite("data", &BitVectorResult::data)
        .def_readwrite("reads", &BitVectorResult::reads);
    
    // BitVectorGenerator
    py::class_<BitVectorGenerator>(m, "BitVectorGenerator")
        .def(py::init<int, int>(),
             py::arg("qscore_cutoff") = 25,
             py::arg("num_of_surbases") = 10)
        .def("generate_single", &BitVectorGenerator::generate_single,
             "Generate bit vector from single read",
             py::arg("read"), py::arg("ref_seq"), py::arg("phred_qscores"))
        .def("generate_paired", &BitVectorGenerator::generate_paired,
             "Generate bit vector from paired reads",
             py::arg("read1"), py::arg("read2"), py::arg("ref_seq"), py::arg("phred_qscores"))
        .def("test_is_deletion_ambiguous", &BitVectorGenerator::test_is_deletion_ambiguous,
             "Test deletion ambiguity check",
             py::arg("ref_seq"), py::arg("pos"), py::arg("length"));
}

