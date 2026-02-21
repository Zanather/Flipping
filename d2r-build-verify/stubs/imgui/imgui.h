#pragma once
// Stub: ImGui header for d2r-stuff build verification
// Only the declarations actually used by d2r-stuff are included.

#include <cstdint>

struct ImVec2 {
    float x, y;
    ImVec2() : x(0), y(0) {}
    ImVec2(float _x, float _y) : x(_x), y(_y) {}
};

struct ImVec4 {
    float x, y, z, w;
    ImVec4() : x(0), y(0), z(0), w(0) {}
    ImVec4(float _x, float _y, float _z, float _w) : x(_x), y(_y), z(_z), w(_w) {}
};

typedef unsigned int ImU32;
typedef int ImGuiCol;
typedef int ImGuiWindowFlags;

namespace ImGui {
    inline bool Begin(const char*, bool* = nullptr, ImGuiWindowFlags = 0) { return true; }
    inline void End() {}
    inline void Text(const char*, ...) {}
    inline void TextColored(const ImVec4&, const char*, ...) {}
    inline bool Button(const char*, const ImVec2& = ImVec2(0, 0)) { return false; }
    inline void SameLine(float = 0.0f, float = -1.0f) {}
    inline void Separator() {}
    inline bool CollapsingHeader(const char*, ImGuiWindowFlags = 0) { return false; }
    inline void SetNextWindowSize(const ImVec2&, int = 0) {}
    inline void SetNextWindowPos(const ImVec2&, int = 0) {}
}
