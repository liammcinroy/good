# just the version I currently have
cmake_minimum_required(VERSION 3.24.2)

project(generic-mlir-dialect LANGUAGES CXX C)

set(CMAKE_BUILD_WITH_INSTALL_NAME_DIR ON)
set(CMAKE_CXX_STANDARD 20 CACHE STRING "C++ standard to conform to")

# the LLVM and MLIR directories
set(LLVM_BUILD_DIR ../llvm-project/build)
set(LLVM_DIR ${LLVM_BUILD_DIR}/lib/cmake/llvm)
set(MLIR_DIR ${LLVM_BUILD_DIR}/lib/cmake/mlir)
set(LLVM_EXTERNAL_LIT ${LLVM_BUILD_DIR}/bin/llvm-lit)

find_package(MLIR REQUIRED CONFIG)

message(STATUS "Using MLIRConfig.cmake in: ${MLIR_DIR}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

set(LLVM_RUNTIME_OUTPUT_INTDIR ${CMAKE_BINARY_DIR}/bin)
set(LLVM_LIBRARY_OUTPUT_INTDIR ${CMAKE_BINARY_DIR}/lib)
set(MLIR_BINARY_DIR ${CMAKE_BINARY_DIR})

list(APPEND CMAKE_MODULE_PATH "${MLIR_CMAKE_DIR}")
list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")

include(TableGen)
include(AddLLVM)
include(AddMLIR)
include(HandleLLVMOptions)

include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_BINARY_DIR}/include)
link_directories(${LLVM_BUILD_LIBRARY_DIR})
add_definitions(${LLVM_DEFINITIONS})

# the actual dialect headers + source
add_subdirectory(include)
add_subdirectory(lib)

if (MLIR_ENABLE_BINDINGS_PYTHON)
  message(STATUS "Enabling Python API")
  add_subdirectory(python)
endif()

add_subdirectory(test)

if (DEFINED ENABLE_OPT)
add_subdirectory(basic-opt)
endif()

if (DEFINED ENABLE_TRANSLATE)
add_subdirectory(basic-translate)
endif()

if (DEFINED ENABLE_PLUGIN)
add_subdirectory(basic-plugin)
endif()