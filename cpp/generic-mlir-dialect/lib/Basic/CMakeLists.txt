add_subdirectory(IR)
add_subdirectory(Transforms)

# also add the source, and depedencies, for Transforms / Passes if applicable
add_mlir_dialect_library(MLIRBasic
        BasicDialect.cpp
        IR/BasicTypes.cpp
        IR/BasicOps.cpp

        ADDITIONAL_HEADER_DIRS
        ${PROJECT_SOURCE_DIR}/include/Basic

        DEPENDS
        MLIRBasicOpsIncGen

        LINK_LIBS PUBLIC
        MLIRIR
        MLIRInferTypeOpInterface
        )
