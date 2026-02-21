@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: d2r-stuff Build Verification Script
:: ============================================================================
:: Clones d2r-stuff, configures CMake with stub dependencies, compiles,
:: and reports which components pass/fail verification.
::
:: Prerequisites:
::   - Visual Studio 2022 with C++ Desktop workload
::   - CMake 3.20+ (included with VS2022)
::   - Git
::
:: Usage:
::   build.bat              -- Full build (clone + configure + compile)
::   build.bat --no-clone   -- Skip clone, use existing d2r-stuff directory
::   build.bat --clean      -- Clean build directory and rebuild
::   build.bat --help       -- Show this help
:: ============================================================================

set "SCRIPT_DIR=%~dp0"
set "D2R_STUFF_DIR=%SCRIPT_DIR%d2r-stuff"
set "BUILD_DIR=%SCRIPT_DIR%build"
set "LOG_FILE=%SCRIPT_DIR%build_log.txt"
set "CLONE=1"
set "CLEAN=0"

:: Parse arguments
:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="--no-clone" (set "CLONE=0" & shift & goto :parse_args)
if /i "%~1"=="--clean" (set "CLEAN=1" & shift & goto :parse_args)
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-h" goto :show_help
shift
goto :parse_args
:args_done

:: Start logging to file
echo d2r-stuff Build Verification - %DATE% %TIME% > "%LOG_FILE%"
echo. >> "%LOG_FILE%"

echo.
echo ================================================================
echo  d2r-stuff Build Verification
echo ================================================================
echo.
echo  (Output is also saved to build_log.txt)
echo.

:: -----------------------------------------------------------------------
:: Step 1: Locate Visual Studio
:: -----------------------------------------------------------------------
echo [1/6] Locating Visual Studio 2022...

set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (
    echo ERROR: vswhere.exe not found. Install Visual Studio 2022.
    echo Download: https://visualstudio.microsoft.com/downloads/
    echo [FAIL] vswhere.exe not found >> "%LOG_FILE%"
    goto :done_fail
)

for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
    set "VS_PATH=%%i"
)

if not defined VS_PATH (
    echo ERROR: Visual Studio with C++ tools not found.
    echo Install "Desktop development with C++" workload.
    echo [FAIL] VS C++ tools not found >> "%LOG_FILE%"
    goto :done_fail
)

echo   Found: %VS_PATH%
echo [OK] VS2022: %VS_PATH% >> "%LOG_FILE%"

:: Initialize VS developer environment
call "%VS_PATH%\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to initialize VS2022 x64 environment.
    echo [FAIL] vcvars64.bat failed >> "%LOG_FILE%"
    goto :done_fail
)
echo   x64 environment initialized.

:: -----------------------------------------------------------------------
:: Step 2: Check CMake
:: -----------------------------------------------------------------------
echo.
echo [2/6] Checking CMake...

where cmake >nul 2>&1
if errorlevel 1 (
    echo ERROR: CMake not found in PATH.
    echo Install CMake or ensure VS2022 CMake is in PATH.
    echo [FAIL] CMake not found >> "%LOG_FILE%"
    goto :done_fail
)

for /f "tokens=3" %%v in ('cmake --version 2^>^&1 ^| findstr /i "version"') do (
    echo   CMake version: %%v
    echo [OK] CMake %%v >> "%LOG_FILE%"
)

:: -----------------------------------------------------------------------
:: Step 3: Clone d2r-stuff
:: -----------------------------------------------------------------------
echo.
echo [3/6] Setting up d2r-stuff source...

if "%CLONE%"=="1" (
    if exist "%D2R_STUFF_DIR%\.git" (
        echo   Repository already exists, pulling latest...
        pushd "%D2R_STUFF_DIR%"
        git pull origin master 2>nul || git pull origin main 2>nul
        popd
    ) else (
        echo   Cloning ejt1/d2r-stuff...
        git clone https://github.com/ejt1/d2r-stuff.git "%D2R_STUFF_DIR%"
        if errorlevel 1 (
            echo ERROR: Failed to clone d2r-stuff repository.
            echo   Check your internet connection and try again.
            echo [FAIL] git clone failed >> "%LOG_FILE%"
            goto :done_fail
        )
    )
) else (
    echo   Skipping clone (--no-clone specified)
)

if not exist "%D2R_STUFF_DIR%\blz\src\blz\d2r.h" (
    echo ERROR: d2r-stuff not found at %D2R_STUFF_DIR%
    echo   Clone it manually: git clone https://github.com/ejt1/d2r-stuff.git "%D2R_STUFF_DIR%"
    echo [FAIL] d2r-stuff not found >> "%LOG_FILE%"
    goto :done_fail
)

echo   Source found at: %D2R_STUFF_DIR%
echo [OK] d2r-stuff found >> "%LOG_FILE%"

:: Count source files
set "CC_COUNT=0"
for /r "%D2R_STUFF_DIR%\src" %%f in (*.cc) do set /a CC_COUNT+=1
set "CPP_COUNT=0"
for /r "%D2R_STUFF_DIR%\blz" %%f in (*.cpp) do set /a CPP_COUNT+=1
set "HDR_COUNT=0"
for /r "%D2R_STUFF_DIR%\blz" %%f in (*.h) do set /a HDR_COUNT+=1

echo   Source files: %CC_COUNT% .cc + %CPP_COUNT% .cpp + %HDR_COUNT% headers

:: -----------------------------------------------------------------------
:: Step 4: Configure CMake
:: -----------------------------------------------------------------------
echo.
echo [4/6] Configuring CMake...

if "%CLEAN%"=="1" (
    if exist "%BUILD_DIR%" (
        echo   Cleaning build directory...
        rmdir /s /q "%BUILD_DIR%"
    )
)

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

cmake -S "%SCRIPT_DIR%" -B "%BUILD_DIR%" ^
    -G "Visual Studio 17 2022" ^
    -A x64 ^
    -DD2R_STUFF_DIR="%D2R_STUFF_DIR%" ^
    -DUSE_STUB_MOZJS=ON ^
    -DUSE_STUB_IMGUI=ON

if errorlevel 1 (
    echo.
    echo ================================================================
    echo  FAIL: CMake configuration failed
    echo ================================================================
    echo  Check the error output above for details.
    echo [FAIL] CMake configure failed >> "%LOG_FILE%"
    goto :done_fail
)

echo   Configuration successful.
echo [OK] CMake configured >> "%LOG_FILE%"

:: -----------------------------------------------------------------------
:: Step 5: Build
:: -----------------------------------------------------------------------
echo.
echo [5/6] Building verification targets...

set "HEADER_PASS=0"
set "STRUCT_PASS=0"
set "SOURCE_PASS=0"

:: Build header check
echo.
echo   --- Header Parse Verification ---
cmake --build "%BUILD_DIR%" --target d2r_header_check --config Release 2>&1
if errorlevel 1 (
    echo   RESULT: FAIL - Headers contain parse errors
    set "HEADER_PASS=0"
    echo [FAIL] Header check >> "%LOG_FILE%"
) else (
    echo   RESULT: PASS - All headers parse correctly
    set "HEADER_PASS=1"
    echo [PASS] Header check >> "%LOG_FILE%"
)

:: Build struct check
echo.
echo   --- Struct Size Verification ---
cmake --build "%BUILD_DIR%" --target d2r_struct_check --config Release 2>&1
if errorlevel 1 (
    echo   RESULT: FAIL - Struct size assertions failed
    set "STRUCT_PASS=0"
    echo [FAIL] Struct check >> "%LOG_FILE%"
) else (
    echo   RESULT: PASS - All struct sizes match expected values
    set "STRUCT_PASS=1"
    echo [PASS] Struct check >> "%LOG_FILE%"
)

:: Build full source
echo.
echo   --- Full Source Compilation ---
cmake --build "%BUILD_DIR%" --target d2r_verify --config Release 2>&1
if errorlevel 1 (
    echo   RESULT: FAIL - Source compilation errors
    set "SOURCE_PASS=0"
    echo [FAIL] Source compilation >> "%LOG_FILE%"
) else (
    echo   RESULT: PASS - All source files compile successfully
    set "SOURCE_PASS=1"
    echo [PASS] Source compilation >> "%LOG_FILE%"
)

:: -----------------------------------------------------------------------
:: Step 6: Report
:: -----------------------------------------------------------------------
echo.
echo ================================================================
echo  BUILD VERIFICATION REPORT
echo ================================================================
echo.

if "%HEADER_PASS%"=="1" (
    echo   [PASS] Header parsing      - All %HDR_COUNT% headers parse without errors
) else (
    echo   [FAIL] Header parsing      - One or more headers failed to parse
)

if "%STRUCT_PASS%"=="1" (
    echo   [PASS] Struct sizes        - All static_assert size checks pass
) else (
    echo   [FAIL] Struct sizes        - Struct layout mismatches detected
)

if "%SOURCE_PASS%"=="1" (
    echo   [PASS] Source compilation  - All %CC_COUNT% .cc + %CPP_COUNT% .cpp files compile
) else (
    echo   [FAIL] Source compilation  - Compilation errors in source files
)

echo.

set /a TOTAL_PASS=%HEADER_PASS%+%STRUCT_PASS%+%SOURCE_PASS%

if "%TOTAL_PASS%"=="3" (
    echo  OVERALL: ALL CHECKS PASSED
    echo.
    echo  The d2r-stuff codebase compiles correctly against stub dependencies.
    echo  For a functional build, replace stubs with:
    echo    - Real SpiderMonkey headers + library (mozilla-central build)
    echo    - Real parent framework (Hook.h, GameLoop, Engine, etc.)
    echo    - ImGui headers + library
    echo.
    echo  Then configure with:
    echo    cmake -DUSE_STUB_MOZJS=OFF -DMOZJS_DIR=path/to/mozjs ...
) else (
    echo  OVERALL: %TOTAL_PASS%/3 CHECKS PASSED
    echo.
    echo  Review the build output above to identify failures.
    echo  Common issues:
    echo    - Struct size changes indicate D2R version mismatch
    echo    - Missing type errors indicate stub headers need updating
)

echo.
echo ================================================================
echo.
echo OVERALL: %TOTAL_PASS%/3 passed >> "%LOG_FILE%"

echo.
echo Press any key to close this window...
pause >nul
if "%TOTAL_PASS%"=="3" (exit /b 0) else (exit /b 1)

:done_fail
echo.
echo ================================================================
echo  BUILD FAILED - See errors above
echo ================================================================
echo.
echo  If the window closed too fast before, the log is saved to:
echo    %LOG_FILE%
echo.
echo Press any key to close this window...
pause >nul
exit /b 1

:show_help
echo.
echo d2r-stuff Build Verification Script
echo.
echo Usage: build.bat [options]
echo.
echo Options:
echo   --no-clone   Skip git clone, use existing d2r-stuff directory
echo   --clean      Remove build directory and rebuild from scratch
echo   --help, -h   Show this help message
echo.
echo Prerequisites:
echo   - Visual Studio 2022 with "Desktop development with C++"
echo   - CMake 3.20+ (bundled with VS2022)
echo   - Git (for cloning d2r-stuff)
echo.
echo The script will:
echo   1. Locate Visual Studio 2022 and initialize x64 environment
echo   2. Clone ejt1/d2r-stuff from GitHub (if not --no-clone)
echo   3. Configure CMake with stub SpiderMonkey and ImGui headers
echo   4. Compile three verification targets:
echo      - d2r_header_check  : Verifies all headers parse
echo      - d2r_struct_check  : Verifies struct sizes via static_assert
echo      - d2r_verify        : Compiles all .cc/.cpp source files
echo   5. Report pass/fail for each target
echo.
echo Press any key to close this window...
pause >nul
exit /b 0
