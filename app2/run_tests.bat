@echo off
REM Test runner script for UTMS application (Windows)

setlocal enabledelayedexpansion

echo.
echo ======================================
echo UTMS Test Suite
echo ======================================
echo.

REM Check if pytest is installed
where pytest >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ pytest not found. Installing test dependencies...
    pip install -r requirements.txt
    echo.
)

REM Parse arguments
set "VERBOSE="
set "COVERAGE="
set "FILE="

for %%A in (%*) do (
    if "%%A"=="-v" set "VERBOSE=-v"
    if "%%A"=="--verbose" set "VERBOSE=-v"
    if "%%A"=="-c" set "COVERAGE=--cov=app --cov-report=html"
    if "%%A"=="--coverage" set "COVERAGE=--cov=app --cov-report=html"
    if "%%A"=="-h" goto help
    if "%%A"=="--help" goto help
    if not "%%A"=="-v" if not "%%A"=="--verbose" if not "%%A"=="-c" if not "%%A"=="--coverage" (
        set "FILE=%%A"
    )
)

echo Running tests...
echo.

if "!FILE!"=="" (
    pytest tests/ %VERBOSE% %COVERAGE%
) else (
    pytest !FILE! %VERBOSE% %COVERAGE%
)

set exit_code=%errorlevel%

echo.
echo ======================================
if %exit_code% equ 0 (
    echo ✅ All tests passed!
) else (
    echo ❌ Some tests failed
)
echo ======================================

if not "!COVERAGE!"=="" (
    echo Coverage report generated in htmlcov\index.html
)

exit /b %exit_code%

:help
echo Usage: run_tests.bat [OPTIONS] [TEST_FILE]
echo.
echo Options:
echo   -v, --verbose       Show detailed output
echo   -c, --coverage      Generate coverage report
echo   -h, --help          Show this help message
echo.
echo Examples:
echo   run_tests.bat                    # Run all tests
echo   run_tests.bat -v                 # Run all tests verbosely
echo   run_tests.bat -c                 # Run with coverage report
echo   run_tests.bat tests/test_auth.py # Run specific file
exit /b 0
