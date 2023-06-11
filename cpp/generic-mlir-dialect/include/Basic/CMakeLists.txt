# register the OPS with TableGen
add_mlir_dialect(BasicOps basic)

add_mlir_doc(BasicDialect BasicDialect Basic/ -gen-dialect-doc)
add_mlir_doc(BasicOps BasicOps Basic/ -gen-op-doc)

# if there's transforms or passes, then add those here
# TODO: check these?

# set(LLVM_TARGET_DEFINITIONS BasicTransforms.td)
# mlir_tablegen(BasicTransforms.h.inc --gen-pass-decls)
# add_public_tablegen_target(MLIRBasicTransformsIncGen)

# set(LLVM_TARGET_DEFINITIONS BasicPasses.td)
# mlir_tablegen(BasicPasses.h.inc --gen-pass-decls)
# add_public_tablegen_target(MLIRBasicPassesIncGen)
