#!/bin/bash

# Build script for pybind11 C++ modules
# Compiles all .cpp files in cpp/ folder and outputs .so files to lib/ folder

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
CPP_DIR="cpp"
LIB_DIR="lib"

# Create lib directory if it doesn't exist
mkdir -p "$LIB_DIR"

echo -e "${YELLOW}Building all C++ modules...${NC}"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Counter for successful builds
SUCCESS_COUNT=0
FAIL_COUNT=0
BUILT_MODULES=()

# Find all .cpp files in cpp/ directory
for cpp_file in "$CPP_DIR"/*.cpp; do
    # Check if any .cpp files exist
    if [ ! -e "$cpp_file" ]; then
        echo -e "${RED}No .cpp files found in $CPP_DIR/${NC}"
        exit 1
    fi

    # Get the base filename without extension
    filename=$(basename "$cpp_file" .cpp)

    # Extract module name from PYBIND11_MODULE macro
    module_name=$(grep -oP 'PYBIND11_MODULE\(\K[^,]+' "$cpp_file" 2>/dev/null || echo "$filename")

    # Output .so file path
    output_file="$LIB_DIR/${module_name}.so"

    echo -e "Building ${YELLOW}$filename.cpp${NC} → ${YELLOW}$output_file${NC}"

    # Compile the C++ code
    g++ -O3 -Wall -shared -std=c++11 -fPIC \
      -I/Library/Frameworks/Python.framework/Versions/3.13/include/python3.13 \
      -I.venv/lib/python3.13/site-packages/pybind11/include \
      "$cpp_file" \
      -o "$output_file" \
      -L/Library/Frameworks/Python.framework/Versions/3.13/lib \
      -lpython3.13

    # Check if compilation was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Build successful!${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        BUILT_MODULES+=("$module_name")
    else
        echo -e "${RED}✗ Build failed for $filename.cpp${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo ""
done

# Summary
echo "================================"
echo -e "${GREEN}Successfully built: $SUCCESS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo "================================"

if [ $SUCCESS_COUNT -gt 0 ]; then
    echo ""
    echo "Built modules in $LIB_DIR/:"
    ls -lh "$LIB_DIR"/*.so 2>/dev/null
    echo ""
    echo "To use in Python, add lib/ to your path:"
    echo "  import sys"
    echo "  sys.path.insert(0, 'lib')"
    for module in "${BUILT_MODULES[@]}"; do
        echo "  import $module"
    done
fi

# Exit with error if any builds failed
if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi

