#!/bin/bash

# Style Testing Suite Runner
# Executes all style tests against Vale configuration

set -e

# Configuration
VALE_CONFIG="../complete-vale-config/.vale.ini"
TEST_PATTERN="test-*.md"
VERBOSE=${VERBOSE:-0}
DRY_RUN=${DRY_RUN:-0}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Check if Vale is installed
if ! command -v vale &> /dev/null; then
    echo -e "${RED}Error: Vale is not installed${NC}"
    echo "Install Vale from https://vale.sh/"
    exit 1
fi

# Check if config exists
if [ ! -f "$VALE_CONFIG" ]; then
    echo -e "${RED}Error: Vale configuration not found at $VALE_CONFIG${NC}"
    exit 1
fi

echo "================================"
echo "Style Testing Suite"
echo "================================"
echo ""
echo "Configuration: $VALE_CONFIG"
echo "Test Pattern: $TEST_PATTERN"
echo ""

# Find all test files
TEST_FILES=$(find . -maxdepth 1 -name "$TEST_PATTERN" -type f | sort)

if [ -z "$TEST_FILES" ]; then
    echo -e "${YELLOW}No test files found matching pattern: $TEST_PATTERN${NC}"
    exit 1
fi

# Run tests
for test_file in $TEST_FILES; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    test_name=$(basename "$test_file" .md)

    echo -n "Testing $test_name... "

    if [ $VERBOSE -eq 1 ]; then
        echo ""
    fi

    # Run Vale on test file
    if vale --config="$VALE_CONFIG" "$test_file" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        if [ $VERBOSE -eq 1 ]; then
            vale --config="$VALE_CONFIG" "$test_file"
        fi
        echo -e "${RED}FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Print summary
echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}Some tests failed${NC}"
    echo ""
    echo "Run with VERBOSE=1 for details:"
    echo "  VERBOSE=1 ./run-all-tests.sh"
    exit 1
fi
