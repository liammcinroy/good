### Setup

See [docs](https://mlir.llvm.org/docs/Tutorials/CreatingADialect/) for details.
More useful is the
[tutorial slides](https://llvm.org/devmtg/2020-09/slides/MLIR_Tutorial.pdf).

Basically, first we'll first need to install
[LLVM](https://github.com/llvm/llvm-project). E.g. as a submodule at
[`../llvm-project`](../llvm-project). Then to set it up, we'll need to build.

```bash
cd llvm-project
mkdir build && cd build
cmake -G Ninja ../llvm \
  -DLLVM_ENABLE_PROJECTS=mlir \
  -DLLVM_BUILD_EXAMPLES=ON \
  -DLLVM_ENABLE_ASSERTIONS=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_ENABLE_RTTI=ON \
  -DLLVM_TARGETS_TO_BUILD="host"

cmake --build . --target check-mlir
```

Sometimes you might also want to change the targets in
`-DLLVM_TARGETS_TO_BUILD` to include e.g. `"NVPTX;AMDGPU"`.

Wherever you end up building LLVM, you'll need to change the appropriate
variables in [`CMakeLists.txt`](CMakeLists.txt), [`build.sh`](`build.sh`), and
[`run.sh`](`run.sh`).

### Notes

Setting up the first dialect is a huge pain. The documentation kinda sucks
too, so this will be quite the learning experience.

#### Linking

- Build LLVM/MLIR as described above, e.g. in `$LLVM_BUILD_DIR`.

- Make sure to link them correctly to this project's cmake using both of
`$LLVM_DIR = $LLVM_BUILD_DIR/lib/cmake/llvm` and
`$MLIR_DIR = $LLVM_BUILD_DIR/lib/cmake/mlir`.

- Include the relevant LLVM/MLIR packages, which will be determined by their
configuration files from `$LLVM_DIR`, `$MLIR_DIR`.

- Then add your own files

That is all of the necessary linking steps that I know of so far, but doesn't
include e.g. testing.

#### The dialect itself

Now we can actually work with MLIR, and hopefully it's not as totally tedious.

- [`include/[DialectName]/`](include/Basic/) all of the dialect
headers, [ODS files](https://mlir.llvm.org/docs/DefiningDialects/Operations/).

- [`lib/[DialectName]/`](lib/Basic/) for the source files.

    - [`lib/[DialectName]/IR/`](lib/Basic/IR/) for the source files of IR
    (e.g. operations, types, etc.)

    - [`lib/[DialectName]/Transforms/`](lib/Basic/Transforms/) for the
    source files of the transformations

    - I don't know where the passes go according to the standard.

- [`test/[DialectName/`](test/Basic/) for the test files (?)

- [`[DialectName]-opt/`](basic-opt/) I don't know what this does yet.

- [`[DialectName]-translate/`](basic-translate/) for translating files
to/from MLIR?

- [`[DialectName]-plugin/`](basic-plugin/) plugins for IDEs (?)

- [`python/`](python/) if adding python bindings.

### TODOs

- Make it follow the suggested file structure from the
[docs](https://mlir.llvm.org/docs/Tutorials/CreatingADialect/).
