#pragma once
// Stub: String obfuscation macro for d2r-stuff build verification
// In the real framework, XorStr encrypts string literals at compile time
// and decrypts them at runtime to evade static analysis.

// In verification build, XorStr is just a passthrough
#define XorStr(s) s
