mkdir build 2> /dev/null
cd build
cmake .. \
  # -DENABLE_GEN_DOCS \
  # -DENABLE_OPT \
  # -DENABLE_TRANSLATE \
  # -DENABLE_PLUGIN \
  # -DLLVM_BUILD_DIR=../../llvm-project/build \
cd ..
cmake --build .  # --target=TODO
