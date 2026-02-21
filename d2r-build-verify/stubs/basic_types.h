#pragma once
// Stub: Framework basic_types.h for d2r-stuff build verification
// Provides Vector2Wrap and other JS wrapper types for blz math primitives.
// NOTE: This is the framework's basic_types.h, NOT blz/basic_types.h

#include "mozjs/jsapi.h"
#include <blz/basic_types.h>

namespace _OLD {

// Vector2Wrap: wraps blz::Vector2f into a JS object
class Vector2Wrap {
public:
    static JSObject* Instantiate(JSContext* ctx, const blz::Vector2f& vec) {
        return JS_NewPlainObject(ctx);
    }

    static JSObject* Instantiate(JSContext* ctx, const blz::Vector2i& vec) {
        return JS_NewPlainObject(ctx);
    }
};

// Vector3Wrap: wraps blz::Vector3f into a JS object
class Vector3Wrap {
public:
    static JSObject* Instantiate(JSContext* ctx, const blz::Vector3f& vec) {
        return JS_NewPlainObject(ctx);
    }
};

} // namespace _OLD
