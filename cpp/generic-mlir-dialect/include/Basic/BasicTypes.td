#ifndef BASIC_BASICTYPES_TD
#define BASIC_BASICTYPES_TD

include "mlir/IR/AttrTypeBase.td"
include "Basic/BasicDialect.td"

// Generic type that will belong to this dialect
class Basic_Type<string name, string typeMnemonic, list<Trait> traits = []>
    : TypeDef<Basic_Dialect, name, traits> {
  let mnemonic = typeMnemonic;
}

#endif
