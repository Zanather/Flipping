#pragma once
// Stub: Offset updater / signature scanner for d2r-stuff build verification
// Provides OffsetSignature type and OffsetUpdater interface.

#include <cstdint>
#include <string>
#include <vector>

namespace _OLD {

// Represents a single signature-based offset entry
struct OffsetSignature {
    std::string name;           // Human-readable name (e.g., "blz::d2r::sgptCameraStuff")
    void** target;              // Pointer to store the resolved address
    std::vector<std::string> patterns;  // Byte patterns with wildcards
};

// Scans the target process memory for byte pattern signatures
class OffsetUpdater {
public:
    void AddSignatures(const std::vector<OffsetSignature>& sigs) {
        // In verification build, just record them
        for (const auto& sig : sigs) {
            signatures_.push_back(sig);
        }
    }

    bool Scan() {
        // Stub: would scan D2R.exe memory in real build
        return true;
    }

private:
    std::vector<OffsetSignature> signatures_;
};

// Engine class that owns the offset updater
class Engine {
public:
    OffsetUpdater* offset_updater() { return &updater_; }

private:
    OffsetUpdater updater_;
};

} // namespace _OLD
