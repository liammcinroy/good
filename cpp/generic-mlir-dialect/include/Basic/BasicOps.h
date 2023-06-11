#ifndef BASIC_BASICOPS_H
#define BASIC_BASICOPS_H

#include "mlir/IR/BuiltinTypes.h"
#include "mlir/IR/Dialect.h"
#include "mlir/IR/OpDefinition.h"
#include "mlir/Interfaces/InferTypeOpInterface.h"
#include "mlir/Interfaces/SideEffectInterfaces.h"

// we also have to define this, for some reason
#define GET_OP_CLASSES
#include "Basic/BasicOps.h.inc"

#endif
