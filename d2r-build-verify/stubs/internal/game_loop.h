#pragma once
// Stub: GameLoop base class for d2r-stuff build verification
// This is the parent framework's game loop abstraction that D2RLoop extends.

#include <cstdint>
#include <string>
#include <functional>

#include "internal/offset_updater.h"

namespace _OLD {

// Forward declaration
class Engine;

// Function pointer type for embedder binding registration
typedef bool (*RegisterEmbedderBindingsFn)(struct JSContext*, void*);
inline RegisterEmbedderBindingsFn s_register_embedder_bindings = nullptr;

class GameLoop {
public:
    GameLoop(Engine* engine) : engine_(engine) {}
    virtual ~GameLoop() {}

    // Factory method - implemented by the specific game loop (D2RLoop)
    static GameLoop* Create(Engine* engine);

    // Lifecycle callbacks
    virtual bool OnInitialize() = 0;
    virtual void OnShutdown() = 0;
    virtual void OnUpdate() = 0;

protected:
    Engine* engine_;
    std::string game_;
};

} // namespace _OLD
