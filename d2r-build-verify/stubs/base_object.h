#pragma once
// Stub: BaseObject class for d2r-stuff build verification
// This is the parent framework's base class for all JS-wrapped game objects.

#include "mozjs/jsapi.h"

namespace _OLD {

class BaseObject {
public:
    static constexpr uint32_t kInternalFieldCount = 1;

    BaseObject(JSContext* ctx, JS::HandleObject obj) {}
    virtual ~BaseObject() {}

    // Retrieves the C++ object pointer stored in a JSObject's reserved slot
    static BaseObject* FromJSObject(JS::HandleValue val) {
        return nullptr;
    }

    static BaseObject* FromJSObject(JSObject* obj) {
        return nullptr;
    }
};

} // namespace _OLD
