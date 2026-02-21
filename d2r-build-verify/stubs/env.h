#pragma once
// Stub: Environment class for d2r-stuff build verification
// Manages prototype registration for JS classes.

#include "mozjs/jsapi.h"

namespace _OLD {

class Environment {
public:
    // Retrieves the prototype object for a given C++ class from the JS context
    template<typename T>
    static JSObject* GetProtoFromContext(JSContext* ctx) {
        return nullptr;
    }

    // Registers a prototype object for a given C++ class in the JS context
    template<typename T>
    static void RegisterProto(JSContext* ctx, JS::HandleObject proto) {
        // no-op in verification build
    }
};

} // namespace _OLD
