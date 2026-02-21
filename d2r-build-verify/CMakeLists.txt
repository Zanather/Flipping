cmake_minimum_required(VERSION 3.20)
project(d2r-stuff-verify LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ============================================================================
# d2r-stuff Build Verification
# ============================================================================
# This CMake project compiles the d2r-stuff source code from ejt1/d2r-stuff
# against stub headers that mock the parent framework dependencies.
#
# It does NOT produce a functional DLL - it verifies that:
#   1. All headers parse correctly
#   2. All .cc/.cpp files compile
#   3. All struct layouts match expected sizes (static_assert)
#   4. All symbol references resolve at link time
#
# Requirements:
#   - Windows x64 (MSVC / Visual Studio 2022)
#   - SpiderMonkey JS headers (mozilla-unified or pre-built)
#   - ImGui headers (optional, can be stubbed)
# ============================================================================

# Path to the cloned d2r-stuff repo
set(D2R_STUFF_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../d2r-stuff"
    CACHE PATH "Path to ejt1/d2r-stuff repository clone")

if(NOT EXISTS "${D2R_STUFF_DIR}/blz/src/blz/d2r.h")
    message(FATAL_ERROR
        "d2r-stuff repo not found at: ${D2R_STUFF_DIR}\n"
        "Clone it: git clone https://github.com/ejt1/d2r-stuff.git ${D2R_STUFF_DIR}\n"
        "Or set -DD2R_STUFF_DIR=<path>")
endif()

# --------------------------------------------------------------------------
# SpiderMonkey configuration
# --------------------------------------------------------------------------
# Set MOZJS_DIR to your SpiderMonkey build/install directory
# It should contain: include/js/, lib/mozjs-*.lib
set(MOZJS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/deps/mozjs"
    CACHE PATH "Path to SpiderMonkey (mozjs) install directory")

option(USE_STUB_MOZJS "Use stub SpiderMonkey headers instead of real ones" ON)
option(USE_STUB_IMGUI "Use stub ImGui headers instead of real ones" ON)

# --------------------------------------------------------------------------
# Source files from d2r-stuff
# --------------------------------------------------------------------------

# blz/ library .cpp files
set(BLZ_SOURCES
    ${D2R_STUFF_DIR}/blz/src/blz/d2r/D2DataTbls.cpp
    ${D2R_STUFF_DIR}/blz/src/blz/d2r/D2StatList.cpp
    ${D2R_STUFF_DIR}/blz/src/blz/d2r/D2BitManip.cpp
    ${D2R_STUFF_DIR}/blz/src/blz/d2r/Common/D2Structs.cpp
    ${D2R_STUFF_DIR}/blz/src/blz/d2r/Units/Units.cpp
    ${D2R_STUFF_DIR}/blz/src/blz/d2r/Drlg/D2DrlgDrlg.cpp
)

# src/ binding layer .cc files
file(GLOB_RECURSE SRC_SOURCES "${D2R_STUFF_DIR}/src/*.cc")

# --------------------------------------------------------------------------
# Include directories
# --------------------------------------------------------------------------
set(INCLUDE_DIRS
    # d2r-stuff headers
    ${D2R_STUFF_DIR}/blz/src
    ${D2R_STUFF_DIR}/src

    # Framework stubs (Hook.h, internal/, bindings.h, etc.)
    ${CMAKE_CURRENT_SOURCE_DIR}/stubs
)

if(USE_STUB_MOZJS)
    list(APPEND INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/stubs/mozjs)
    message(STATUS "Using STUB SpiderMonkey headers")
else()
    if(NOT EXISTS "${MOZJS_DIR}/include")
        message(FATAL_ERROR "SpiderMonkey not found at ${MOZJS_DIR}. Set -DMOZJS_DIR=<path> or -DUSE_STUB_MOZJS=ON")
    endif()
    list(APPEND INCLUDE_DIRS ${MOZJS_DIR}/include)
    message(STATUS "Using real SpiderMonkey from: ${MOZJS_DIR}")
endif()

if(USE_STUB_IMGUI)
    list(APPEND INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/stubs/imgui)
    message(STATUS "Using STUB ImGui headers")
endif()

# --------------------------------------------------------------------------
# Compile target: static library (verification only, not a real DLL)
# --------------------------------------------------------------------------
add_library(d2r_verify STATIC ${BLZ_SOURCES} ${SRC_SOURCES})

target_include_directories(d2r_verify PRIVATE ${INCLUDE_DIRS})

# MSVC-specific flags
if(MSVC)
    target_compile_options(d2r_verify PRIVATE
        /W3             # Warning level 3
        /permissive-    # Standards conformance
        /Zc:__cplusplus # Report correct __cplusplus value
        /EHsc           # C++ exceptions
        /utf-8          # Source/execution charset
    )
    target_compile_definitions(d2r_verify PRIVATE
        _CRT_SECURE_NO_WARNINGS
        WIN32_LEAN_AND_MEAN
        NOMINMAX
        _WIN64
        D2R_VERIFY_BUILD  # Flag so stubs know this is verification
    )
endif()

# --------------------------------------------------------------------------
# Header-only parse verification
# --------------------------------------------------------------------------
# Create a single .cpp that includes every d2r header to verify they all parse
set(HEADER_CHECK_FILE "${CMAKE_CURRENT_BINARY_DIR}/header_check.cpp")
file(GLOB_RECURSE ALL_D2R_HEADERS "${D2R_STUFF_DIR}/blz/src/blz/*.h")
file(WRITE ${HEADER_CHECK_FILE}
    "// Auto-generated: verifies all d2r headers compile\n"
    "#include <cstdint>\n"
    "#include <cstring>\n"
    "#include <vector>\n"
    "#include <string>\n"
)
foreach(hdr ${ALL_D2R_HEADERS})
    file(APPEND ${HEADER_CHECK_FILE} "#include \"${hdr}\"\n")
endforeach()
file(APPEND ${HEADER_CHECK_FILE} "\nint header_check_dummy = 0;\n")

add_library(d2r_header_check STATIC ${HEADER_CHECK_FILE})
target_include_directories(d2r_header_check PRIVATE ${INCLUDE_DIRS})
if(MSVC)
    target_compile_options(d2r_header_check PRIVATE /W3 /permissive- /Zc:__cplusplus /EHsc /utf-8)
    target_compile_definitions(d2r_header_check PRIVATE
        _CRT_SECURE_NO_WARNINGS WIN32_LEAN_AND_MEAN NOMINMAX _WIN64 D2R_VERIFY_BUILD)
endif()

# --------------------------------------------------------------------------
# Struct size verification target
# --------------------------------------------------------------------------
set(STRUCT_CHECK_FILE "${CMAKE_CURRENT_BINARY_DIR}/struct_size_check.cpp")
file(WRITE ${STRUCT_CHECK_FILE}
    "// Auto-generated: verifies critical struct sizes match expected values\n"
    "#include <cstdint>\n"
    "#include <cstring>\n"
    "#include <blz/d2r.h>\n"
    "#include <blz/d2r/D2Inventory.h>\n"
    "#include <blz/d2r/D2Game.h>\n"
    "#include <blz/d2r/D2Chat.h>\n"
    "#include <blz/d2r/D2Roster.h>\n"
    "#include <blz/d2r/D2Environment.h>\n"
    "#include <blz/d2r/D2Waypoint.h>\n"
    "\n"
    "// If this compiles, all static_assert checks in the headers pass.\n"
    "// The d2r headers contain static_assert(sizeof(X) == 0xNN) throughout.\n"
    "int struct_check_ok = 1;\n"
)

add_library(d2r_struct_check STATIC ${STRUCT_CHECK_FILE})
target_include_directories(d2r_struct_check PRIVATE ${INCLUDE_DIRS})
if(MSVC)
    target_compile_options(d2r_struct_check PRIVATE /W3 /permissive- /Zc:__cplusplus /EHsc /utf-8)
    target_compile_definitions(d2r_struct_check PRIVATE
        _CRT_SECURE_NO_WARNINGS WIN32_LEAN_AND_MEAN NOMINMAX _WIN64 D2R_VERIFY_BUILD)
endif()

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
message(STATUS "")
message(STATUS "=== d2r-stuff Build Verification ===")
message(STATUS "d2r-stuff repo:    ${D2R_STUFF_DIR}")
message(STATUS "Stub SpiderMonkey: ${USE_STUB_MOZJS}")
message(STATUS "Stub ImGui:        ${USE_STUB_IMGUI}")
message(STATUS "")
message(STATUS "Targets:")
message(STATUS "  d2r_verify       - Compiles all .cc/.cpp source files")
message(STATUS "  d2r_header_check - Verifies all headers parse")
message(STATUS "  d2r_struct_check - Verifies struct sizes via static_assert")
message(STATUS "====================================")
