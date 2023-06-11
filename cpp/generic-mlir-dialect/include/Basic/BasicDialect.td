#ifndef BASIC_BASICDIALECT_TD
#define BASIC_BASICDIALECT_TD

include "mlir/IR/OpBase.td"

// For the actual dialect namespaces and whatnot, which registers the
// operations to this particular dialect.
def Basic_Dialect : Dialect {
  let name = "basic";
  let summary = "A generic template for a MLIR dialect.";
  let description = [{
    A simple template project for custom MLIR dialects.
  }];
  let cppNamespace = "::mlir::basic";

  let useDefaultTypePrinterParser = 1;
  let extraClassDeclaration = [{
      void registerTypes();
  }];
}

// Generic operation that will belong to this dialect.
class Basic_Op<string mnemonic, list<Trait> traits = []> :
    Op<Basic_Dialect, mnemonic, traits>;

#endif
