mkdir build 2> /dev/null
cmake -Bbuild -S. \
  # -DENABLE_GEN_DOCS \
  # -DENABLE_OPT \
  # -DENABLE_TRANSLATE \
  # -DENABLE_PLUGIN \
  # -DLLVM_BUILD_DIR=../../llvm-project/build \
cmake --build build  # --target=TODO
