"""Setup script for C++ bit vector module using pybind11."""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
from setuptools.command.build_ext import build_ext as _build_ext
from pathlib import Path
import shutil
import glob

# Get the project root directory
project_root = Path(__file__).parent.parent
cpp_dir = project_root / "cpp"
include_dir = cpp_dir / "include"
src_dir = cpp_dir / "src"
pipeline_dir = project_root / "lib" / "rna_map" / "pipeline"

class BuildExtWithCopy(_build_ext):
    """Custom build_ext that copies .so file to pipeline directory."""
    def run(self):
        super().run()
        # Find the built .so file
        build_lib = Path(self.build_lib)
        so_files = list(build_lib.rglob("bit_vector_cpp*.so"))
        if not so_files:
            # Also check inplace build
            so_files = list(cpp_dir.glob("bit_vector_cpp*.so"))
        
        if so_files:
            so_file = so_files[0]
            # Copy to pipeline directory with expected name
            pipeline_dir.mkdir(parents=True, exist_ok=True)
            target = pipeline_dir / "_bit_vector_cpp_impl.so"
            shutil.copy2(so_file, target)
            print(f"Copied {so_file.name} to {target}")

ext_modules = [
    Pybind11Extension(
        "bit_vector_cpp",
        [
            str(src_dir / "bit_vector_generator.cpp"),
            str(src_dir / "bindings.cpp"),
        ],
        include_dirs=[str(include_dir)],
        cxx_std=17,
        language="c++",
    ),
]

setup(
    name="rna_map_bit_vector_cpp",
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExtWithCopy},
    zip_safe=False,
    options={"build_ext": {"inplace": True}},
)

