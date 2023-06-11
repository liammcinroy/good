#include "Basic/BasicTypes.h"

#include "Basic/BasicDialect.h"
#include "llvm/ADT/TypeSwitch.h"
#include "mlir/IR/Builders.h"
#include "mlir/IR/DialectImplementation.h"

// we can't put in namespace directly, since the include depends on the
// `using` statement, stupidly enough...
using namespace mlir::basic;

#define GET_TYPEDEF_CLASSES
#include "Basic/BasicOpsTypes.cpp.inc"

void BasicDialect::registerTypes() {
  addTypes<
#define GET_TYPEDEF_LIST
#include "Basic/BasicOpsTypes.cpp.inc"
      >();
}
