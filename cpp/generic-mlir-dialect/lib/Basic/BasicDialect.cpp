#include "Basic/BasicDialect.h"

#include "Basic/BasicOps.h"
#include "Basic/BasicTypes.h"

// we can't put in namespace directly, since the include depends on the
// `using` statement, stupidly enough...
using namespace mlir;
using namespace basic;

#include "Basic/BasicOpsDialect.cpp.inc"

void BasicDialect::initialize() {
  addOperations<
#define GET_OP_LIST
#include "Basic/BasicOps.cpp.inc"
      >();
  registerTypes();
}
