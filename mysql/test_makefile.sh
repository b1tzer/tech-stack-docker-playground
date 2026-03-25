#!/bin/bash

# Exit on error
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================="
echo "      Running Makefile Tests           "
echo "======================================="

# 1. Test help target
echo -n "1. Testing 'make help'... "
if make help > /dev/null 2>&1; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

# 2. Test init target
echo -n "2. Testing 'make init'... "
make init > /dev/null 2>&1
if [ -d "master/data" ] && [ -d "slave/data" ] && [ -d "master/init" ]; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

# 3. Test argument passing for seed (dry-run)
echo -n "3. Testing argument passing (make seed 123)... "
if make -n seed 123 2>/dev/null | grep -q "123"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

# 4. Test argument passing for test-perf (dry-run)
echo -n "4. Testing argument passing (make test-perf 456)... "
if make -n test-perf 456 2>/dev/null | grep -q "456"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

# 5. Test dry-run of docker commands
echo -n "5. Testing docker commands generation... "
if make -n start 2>/dev/null | grep -q "docker-compose up -d"; then
    echo -e "${GREEN}PASSED${NC}"
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

echo "======================================="
echo -e "${GREEN}All basic Makefile tests passed!${NC}"
echo "======================================="
echo ""
echo "If you want to run a full End-to-End (E2E) test that actually starts the containers,"
echo "you can manually run the following sequence:"
echo "  make clean && make start && make test && make seed 100 && make clean"
