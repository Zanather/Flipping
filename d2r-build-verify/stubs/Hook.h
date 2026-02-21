#pragma once
// Stub: Function hooking utilities for d2r-stuff build verification
// In the real framework, this provides inline/detour hooking via MinHook or similar.

#include <cstdint>

namespace _OLD {

// Hook a function by replacing its address
inline bool HookFunction(void* target, void* detour, void** original) {
    if (original) *original = target;
    return true;
}

// Unhook a previously hooked function
inline bool UnhookFunction(void* target) {
    return true;
}

} // namespace _OLD
