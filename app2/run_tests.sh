#!/bin/bash
# Test runner script for UTMS application

set -e

echo "======================================"
echo "UTMS Test Suite"
echo "======================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing test dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Parse arguments
VERBOSE=""
COVERAGE=""
FILE=""

for arg in "$@"; do
    case $arg in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=app --cov-report=html"
            shift
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [OPTIONS] [TEST_FILE]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose       Show detailed output"
            echo "  -c, --coverage      Generate coverage report"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                    # Run all tests"
            echo "  ./run_tests.sh -v                 # Run all tests verbosely"
            echo "  ./run_tests.sh -c                 # Run with coverage report"
            echo "  ./run_tests.sh tests/test_auth.py # Run specific file"
            exit 0
            ;;
        *)
            if [[ -z "$FILE" ]]; then
                FILE="$arg"
            fi
            shift
            ;;
    esac
done

# Run tests
echo "Running tests..."
echo ""

if [[ -z "$FILE" ]]; then
    pytest tests/ $VERBOSE $COVERAGE
else
    pytest "$FILE" $VERBOSE $COVERAGE
fi

exit_code=$?

echo ""
echo "======================================"
if [[ $exit_code -eq 0 ]]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed"
fi
echo "======================================"

if [[ -n "$COVERAGE" ]]; then
    echo "Coverage report generated in htmlcov/index.html"
fi

exit $exit_code
