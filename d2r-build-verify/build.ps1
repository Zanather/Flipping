#Requires -Version 5.1
<#
.SYNOPSIS
    d2r-stuff Build Verification Script (PowerShell)

.DESCRIPTION
    Clones d2r-stuff, configures CMake with stub dependencies, compiles all
    source files, and reports verification results.

.PARAMETER NoClone
    Skip git clone, use existing d2r-stuff directory.

.PARAMETER Clean
    Remove build directory and rebuild from scratch.

.PARAMETER D2RStuffDir
    Custom path to d2r-stuff repository (default: ./d2r-stuff).

.EXAMPLE
    .\build.ps1
    .\build.ps1 -NoClone
    .\build.ps1 -Clean -D2RStuffDir "C:\repos\d2r-stuff"
#>
param(
    [switch]$NoClone,
    [switch]$Clean,
    [string]$D2RStuffDir
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $D2RStuffDir) {
    $D2RStuffDir = Join-Path $ScriptDir "d2r-stuff"
}
$BuildDir = Join-Path $ScriptDir "build"

function Write-Header($msg) {
    Write-Host "`n$('=' * 64)" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "$('=' * 64)" -ForegroundColor Cyan
}

function Write-Step($num, $total, $msg) {
    Write-Host "`n[$num/$total] $msg" -ForegroundColor Yellow
}

function Write-Pass($msg) {
    Write-Host "  [PASS] $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "  [FAIL] $msg" -ForegroundColor Red
}

Write-Header "d2r-stuff Build Verification"

# -----------------------------------------------------------------------
# Step 1: Locate Visual Studio
# -----------------------------------------------------------------------
Write-Step 1 6 "Locating Visual Studio 2022..."

$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $vswhere)) {
    Write-Fail "vswhere.exe not found. Install Visual Studio 2022."
    exit 1
}

$vsPath = & $vswhere -latest -products * `
    -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
    -property installationPath 2>$null | Select-Object -First 1

if (-not $vsPath) {
    Write-Fail "Visual Studio with C++ tools not found."
    exit 1
}

Write-Host "  Found: $vsPath" -ForegroundColor Gray

# Initialize VS environment
$vcvars = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
if (-not (Test-Path $vcvars)) {
    Write-Fail "vcvars64.bat not found at: $vcvars"
    exit 1
}

# Import VS environment variables into PowerShell
$envBefore = @{}
Get-ChildItem env: | ForEach-Object { $envBefore[$_.Name] = $_.Value }

$output = cmd /c "`"$vcvars`" >nul 2>&1 && set" 2>&1
foreach ($line in $output) {
    if ($line -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}
Write-Host "  x64 environment initialized." -ForegroundColor Gray

# -----------------------------------------------------------------------
# Step 2: Check CMake
# -----------------------------------------------------------------------
Write-Step 2 6 "Checking CMake..."

$cmake = Get-Command cmake -ErrorAction SilentlyContinue
if (-not $cmake) {
    Write-Fail "CMake not found in PATH."
    exit 1
}

$cmakeVersion = (cmake --version | Select-String "version" | Select-Object -First 1).ToString().Trim()
Write-Host "  $cmakeVersion" -ForegroundColor Gray

# -----------------------------------------------------------------------
# Step 3: Clone d2r-stuff
# -----------------------------------------------------------------------
Write-Step 3 6 "Setting up d2r-stuff source..."

if (-not $NoClone) {
    if (Test-Path (Join-Path $D2RStuffDir ".git")) {
        Write-Host "  Repository exists, pulling latest..." -ForegroundColor Gray
        Push-Location $D2RStuffDir
        git pull origin master 2>$null
        if ($LASTEXITCODE -ne 0) { git pull origin main 2>$null }
        Pop-Location
    } else {
        Write-Host "  Cloning ejt1/d2r-stuff..." -ForegroundColor Gray
        git clone "https://github.com/ejt1/d2r-stuff.git" $D2RStuffDir
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Failed to clone d2r-stuff"
            exit 1
        }
    }
} else {
    Write-Host "  Skipping clone (--NoClone)" -ForegroundColor Gray
}

$d2rHeader = Join-Path $D2RStuffDir "blz\src\blz\d2r.h"
if (-not (Test-Path $d2rHeader)) {
    Write-Fail "d2r-stuff not found at: $D2RStuffDir"
    exit 1
}

$ccFiles = (Get-ChildItem -Path "$D2RStuffDir\src" -Filter "*.cc" -Recurse).Count
$cppFiles = (Get-ChildItem -Path "$D2RStuffDir\blz" -Filter "*.cpp" -Recurse).Count
$hdrFiles = (Get-ChildItem -Path "$D2RStuffDir\blz" -Filter "*.h" -Recurse).Count
Write-Host "  Source: $ccFiles .cc + $cppFiles .cpp + $hdrFiles headers" -ForegroundColor Gray

# -----------------------------------------------------------------------
# Step 4: Configure CMake
# -----------------------------------------------------------------------
Write-Step 4 6 "Configuring CMake..."

if ($Clean -and (Test-Path $BuildDir)) {
    Write-Host "  Cleaning build directory..." -ForegroundColor Gray
    Remove-Item -Recurse -Force $BuildDir
}

if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

$cmakeArgs = @(
    "-S", $ScriptDir,
    "-B", $BuildDir,
    "-G", "Visual Studio 17 2022",
    "-A", "x64",
    "-DD2R_STUFF_DIR=$D2RStuffDir",
    "-DUSE_STUB_MOZJS=ON",
    "-DUSE_STUB_IMGUI=ON"
)

& cmake @cmakeArgs 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }

if ($LASTEXITCODE -ne 0) {
    Write-Fail "CMake configuration failed"
    exit 1
}

Write-Host "  Configuration successful." -ForegroundColor Gray

# -----------------------------------------------------------------------
# Step 5: Build verification targets
# -----------------------------------------------------------------------
Write-Step 5 6 "Building verification targets..."

$results = @{}

# Header check
Write-Host "`n  --- Header Parse Verification ---" -ForegroundColor White
$headerOutput = cmake --build $BuildDir --target d2r_header_check --config Release 2>&1
$headerOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
$results["Headers"] = ($LASTEXITCODE -eq 0)

# Struct check
Write-Host "`n  --- Struct Size Verification ---" -ForegroundColor White
$structOutput = cmake --build $BuildDir --target d2r_struct_check --config Release 2>&1
$structOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
$results["Structs"] = ($LASTEXITCODE -eq 0)

# Full source
Write-Host "`n  --- Full Source Compilation ---" -ForegroundColor White
$sourceOutput = cmake --build $BuildDir --target d2r_verify --config Release 2>&1
$sourceOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
$results["Sources"] = ($LASTEXITCODE -eq 0)

# -----------------------------------------------------------------------
# Step 6: Report
# -----------------------------------------------------------------------
Write-Header "BUILD VERIFICATION REPORT"

if ($results["Headers"]) {
    Write-Pass "Header parsing      - All $hdrFiles headers parse without errors"
} else {
    Write-Fail "Header parsing      - One or more headers failed to parse"
}

if ($results["Structs"]) {
    Write-Pass "Struct sizes        - All static_assert size checks pass"
} else {
    Write-Fail "Struct sizes        - Struct layout mismatches detected"
}

if ($results["Sources"]) {
    Write-Pass "Source compilation   - All $ccFiles .cc + $cppFiles .cpp files compile"
} else {
    Write-Fail "Source compilation   - Compilation errors in source files"
}

$passCount = ($results.Values | Where-Object { $_ }).Count
$totalCount = $results.Count

Write-Host ""
if ($passCount -eq $totalCount) {
    Write-Host "  OVERALL: ALL CHECKS PASSED ($passCount/$totalCount)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  The d2r-stuff codebase compiles correctly against stub dependencies." -ForegroundColor Gray
    Write-Host "  For a functional build, replace stubs with real dependencies:" -ForegroundColor Gray
    Write-Host "    - SpiderMonkey (mozilla-central build)" -ForegroundColor Gray
    Write-Host "    - Parent framework (Hook.h, GameLoop, Engine)" -ForegroundColor Gray
    Write-Host "    - ImGui library" -ForegroundColor Gray
} else {
    Write-Host "  OVERALL: $passCount/$totalCount CHECKS PASSED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Review build output above for failure details." -ForegroundColor Gray
}

Write-Host "`n$('=' * 64)`n" -ForegroundColor Cyan
exit $(if ($passCount -eq $totalCount) { 0 } else { 1 })
