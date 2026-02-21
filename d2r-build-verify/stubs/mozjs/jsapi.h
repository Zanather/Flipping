#pragma once
// Stub SpiderMonkey JSAPI header for d2r-stuff build verification
// This provides the minimum type definitions and function declarations
// needed to compile the d2r-stuff JS binding layer without linking SpiderMonkey.

#include <cstdint>
#include <cstddef>
#include <cstring>
#include <stdexcept>

// Forward declarations
struct JSContext;
struct JSObject;
struct JSString;
struct JSFreeOp;
struct JSClass;
struct JSClassOps;
struct JSFunctionSpec;
struct JSPropertySpec;

typedef bool (*JSNative)(JSContext* cx, unsigned argc, JS::Value* vp);

namespace JS {

// Value type - fundamental SpiderMonkey value representation
class Value {
public:
    Value() : data_(0), tag_(0) {}

    bool isObject() const { return tag_ == 1; }
    bool isNumber() const { return tag_ == 2; }
    bool isInt32() const { return tag_ == 3; }
    bool isBoolean() const { return tag_ == 4; }
    bool isString() const { return tag_ == 5; }
    bool isNull() const { return tag_ == 0 && data_ == 0; }
    bool isUndefined() const { return tag_ == 6; }

    double toNumber() const { return static_cast<double>(data_); }
    int32_t toInt32() const { return static_cast<int32_t>(data_); }
    bool toBoolean() const { return data_ != 0; }
    JSObject* toObjectOrNull() const { return nullptr; }
    JSString* toString() const { return nullptr; }

    void setObject(JSObject& obj) { tag_ = 1; }
    void setObjectOrNull(JSObject* obj) { tag_ = obj ? 1 : 0; }
    void setNumber(double d) { tag_ = 2; data_ = static_cast<uint64_t>(d); }
    void setNumber(uint32_t n) { tag_ = 2; data_ = n; }
    void setInt32(int32_t i) { tag_ = 3; data_ = static_cast<uint64_t>(i); }
    void setBoolean(bool b) { tag_ = 4; data_ = b ? 1 : 0; }
    void setString(JSString* s) { tag_ = 5; }
    void setNull() { tag_ = 0; data_ = 0; }
    void setUndefined() { tag_ = 6; }
    void setBigInt(void* bi) { tag_ = 7; }

private:
    uint64_t data_;
    int tag_;
};

inline Value BooleanValue(bool b) { Value v; v.setBoolean(b); return v; }
inline Value ObjectOrNullValue(JSObject* obj) { Value v; v.setObjectOrNull(obj); return v; }
inline Value UndefinedValue() { Value v; v.setUndefined(); return v; }
inline Value NullValue() { Value v; v.setNull(); return v; }

inline uint32_t ToUint32(double d) { return static_cast<uint32_t>(d); }
inline bool ToUint32(JSContext*, Value, uint32_t* out) { *out = 0; return true; }
inline bool ToInt32(JSContext*, Value, int32_t* out) { *out = 0; return true; }

inline void* NumberToBigInt(JSContext*, uint64_t) { return nullptr; }

// Handle types
template<typename T>
class Handle {
public:
    Handle() : ptr_(nullptr) {}
    Handle(T* p) : ptr_(p) {}
    T& get() const { return *ptr_; }
    operator T() const { return *ptr_; }
private:
    T* ptr_;
};

template<typename T>
class MutableHandle : public Handle<T> {};

typedef Handle<JSObject*> HandleObject;
typedef Handle<Value> HandleValue;
typedef MutableHandle<JSObject*> MutableHandleObject;
typedef MutableHandle<Value> MutableHandleValue;

// Rooted types (prevent GC collection)
template<typename T>
class Rooted {
public:
    Rooted(JSContext* cx) : val_() {}
    Rooted(JSContext* cx, T init) : val_(init) {}
    T& get() { return val_; }
    const T& get() const { return val_; }
    operator T() const { return val_; }
    operator Handle<T>() const { return Handle<T>(const_cast<T*>(&val_)); }
    T* address() { return &val_; }
private:
    T val_;
};

typedef Rooted<JSObject*> RootedObject;
typedef Rooted<Value> RootedValue;

template<unsigned N>
class RootedValueArray {
public:
    RootedValueArray(JSContext* cx) {}
    Value& operator[](unsigned i) { return vals_[i]; }
private:
    Value vals_[N];
};

// Persistent rooted types
template<typename T>
class PersistentRooted {
public:
    PersistentRooted() {}
    PersistentRooted(JSContext* cx) {}
    T& get() { return val_; }
private:
    T val_;
};

class PersistentRootedObjectVector {
public:
    PersistentRootedObjectVector() {}
    PersistentRootedObjectVector(JSContext* cx) {}
};

// CallArgs
class CallArgs {
public:
    Value& operator[](unsigned i) { return args_[i]; }
    Value& thisv() { return this_; }
    Value get(unsigned i) { return args_[i]; }
    Value& rval() { return rval_; }
    unsigned length() const { return 0; }
private:
    Value args_[8];
    Value this_;
    Value rval_;
};

// Construct
inline bool Construct(JSContext*, HandleValue, RootedValueArray<2>&, MutableHandleObject*) { return true; }

// Array
inline JSObject* NewArrayObject(JSContext*, unsigned len) { return nullptr; }

// GC
inline JSObject* GetConstructor(JSContext*, HandleObject) { return nullptr; }

} // namespace JS

// JSAPI functions
inline JSObject* JS_NewPlainObject(JSContext*) { return nullptr; }
inline bool JS_DefineFunctions(JSContext*, JS::HandleObject, const JSFunctionSpec*) { return true; }
inline bool JS_DefineProperties(JSContext*, JS::HandleObject, const JSPropertySpec*) { return true; }
inline bool JS_DefineProperty(JSContext*, JS::HandleObject, const char*, int32_t, unsigned) { return true; }
inline bool JS_DefineProperty(JSContext*, JS::HandleObject, const char*, uint32_t, unsigned) { return true; }
inline bool JS_DefineProperty(JSContext*, JS::HandleObject, const char*, JS::HandleObject, unsigned) { return true; }
inline bool JS_DefineProperty(JSContext*, JS::HandleObject, const char*, JS::HandleValue, unsigned) { return true; }
inline bool JS_DefineElement(JSContext*, JS::HandleObject, uint32_t, JS::HandleObject, unsigned) { return true; }
inline bool JS_SetElement(JSContext*, JS::HandleObject, uint32_t, int32_t) { return true; }
inline bool JS_SetElement(JSContext*, JS::HandleObject, uint32_t, uint32_t) { return true; }
inline bool JS_SetElement(JSContext*, JS::HandleObject, uint32_t, JS::HandleObject) { return true; }
inline bool JS_SetElement(JSContext*, JS::HandleObject, uint32_t, JS::HandleValue) { return true; }
inline JSString* JS_NewStringCopyZ(JSContext*, const char*) { return nullptr; }
inline JSObject* JS_InitClass(JSContext*, JS::HandleObject, JSObject*, const JSClass*, JSNative, unsigned,
                               const JSPropertySpec*, const JSFunctionSpec*, const JSPropertySpec*, const JSFunctionSpec*) {
    return nullptr;
}
inline JSObject* JS_NewObjectForConstructor(JSContext*, const JSClass*, JS::CallArgs&) { return nullptr; }
inline void JS_ReportErrorUTF8(JSContext*, const char*, ...) {}

// Property/Function spec macros
#define JSPROP_ENUMERATE 0x01
#define JSPROP_PERMANENT 0x10

#define JSCLASS_HAS_RESERVED_SLOTS(n) ((n) << 8)
#define JSCLASS_FOREGROUND_FINALIZE 0x1000

struct JSClassOps {
    void* addProperty;
    void* delProperty;
    void* enumerate;
    void* newEnumerate;
    void* resolve;
    void* mayResolve;
    void (*finalize)(JSFreeOp*, JSObject*);
    void* call;
    void* hasInstance;
    void* construct;
    void* trace;
};

struct JSClass {
    const char* name;
    uint32_t flags;
    const JSClassOps* cOps;
};

struct JSFunctionSpec {
    const char* name;
    JSNative call;
    uint16_t nargs;
    uint16_t flags;
};

struct JSPropertySpec {
    const char* name;
    uint32_t flags;
    union {
        struct { JSNative getter; JSNative setter; } native;
    } u;
};

#define JS_FS_END { nullptr, nullptr, 0, 0 }
#define JS_PS_END { nullptr, 0, { { nullptr, nullptr } } }

// Exception type used in d2r-stuff
class JSException : public std::runtime_error {
public:
    JSException() : std::runtime_error("JSException") {}
};
