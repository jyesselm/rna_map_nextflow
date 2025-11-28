cmake_minimum_required(VERSION 3.12)
project(rna_map_bit_vector_cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find pybind11
find_package(pybind11 REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/bit_vector_generator.cpp
    src/bindings.cpp
)

# Create Python module
pybind11_add_module(bit_vector_cpp ${SOURCES})

# Set output directory to lib/rna_map for easy import
set_target_properties(bit_vector_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../lib/rna_map
    PREFIX ""
)

# Compiler flags
target_compile_options(bit_vector_cpp PRIVATE
    -Wall -Wextra -O3
)

