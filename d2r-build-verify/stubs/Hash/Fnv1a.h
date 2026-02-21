#pragma once
// Stub: FNV-1a hash function for d2r-stuff build verification

#include <cstdint>
#include <cstring>

namespace _OLD {

constexpr uint32_t Fnv1a32(const char* str, uint32_t hash = 0x811c9dc5) {
    return (*str == 0) ? hash : Fnv1a32(str + 1, (hash ^ static_cast<uint32_t>(*str)) * 0x01000193);
}

constexpr uint64_t Fnv1a64(const char* str, uint64_t hash = 0xcbf29ce484222325ULL) {
    return (*str == 0) ? hash : Fnv1a64(str + 1, (hash ^ static_cast<uint64_t>(*str)) * 0x00000100000001B3ULL);
}

} // namespace _OLD
