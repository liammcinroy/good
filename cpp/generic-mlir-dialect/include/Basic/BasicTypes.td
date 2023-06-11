#ifndef BASIC_TYPES
#define BASIC_TYPES

include "mlir/IR/AttrTypeBase.td"
include "Basic/BasicDialect.td"

// Generic type that will belong to this dialect
class Basic_Type<string name, string typeMnemonic, list<Trait> traits = []>
    : TypeDef<Basic_Dialect, name, traits> {
  let mnemonic = typeMnemonic;
}

#endif
