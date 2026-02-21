#pragma once
// Stub: Framework binding macros for d2r-stuff build verification
// These macros replicate the parent framework's JS binding registration system.

#include "mozjs/jsapi.h"

namespace _OLD {

// throwXxx helper functions used throughout the binding layer
inline void throwOutOfMemory(JSContext* ctx) {
    throw JSException();
}

inline void throwInternalError(JSContext* ctx, const char* fmt, ...) {
    throw JSException();
}

inline void throwNotExpectedType(JSContext* ctx, const char* name, JS::Value val, const char* expected) {
    throw JSException();
}

// NativeFunctionWrap: wraps a void(JSContext*, JS::CallArgs&) into a JSNative
template<void (*Fn)(JSContext*, JS::CallArgs&), unsigned Nargs>
bool NativeFunctionWrap(JSContext* ctx, unsigned argc, JS::Value* vp) {
    JS::CallArgs args;
    Fn(ctx, args);
    return true;
}

// _OLD_FN: creates a JSFunctionSpec entry binding a C++ method
#define _OLD_FN(name, fn, nargs) \
    { name, NativeFunctionWrap<fn, nargs>, nargs, 0 }

// _OLD_PSG: creates a read-only JSPropertySpec with a getter
#define _OLD_PSG(name, getter) \
    { name, JSPROP_ENUMERATE | JSPROP_PERMANENT, { { NativeFunctionWrap<getter, 0>, nullptr } } }

// _OLD_BINDING_INTERNAL: registers a binding init function
// In the real framework this adds to a global registry; here it's a no-op declaration.
#define _OLD_BINDING_INTERNAL(name, init_fn) \
    static bool __register##name(JSContext* ctx, JS::HandleObject target) { \
        return init_fn(ctx, target); \
    }

// DEFINE_ENUM: defines a JS object with enum constants
#define DEFINE_ENUM(ctx, enumName, target, ENUM_LIST) \
    do { \
        JS::RootedObject enumObj(ctx, JS_NewPlainObject(ctx)); \
        target; \
    } while(0)

// LOG_DEBUG macro
#define LOG_DEBUG(...) do {} while(0)

} // namespace _OLD
