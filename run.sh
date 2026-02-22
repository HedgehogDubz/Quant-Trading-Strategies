#!/bin/bash

# Run script for Python files in the python/ directory
# Usage: ./run.sh <script_name.py>

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if a script name was provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No script name provided${NC}"
    echo "Usage: ./run.sh <script_name.py>"
    echo ""
    echo "Available scripts in python/:"
    ls -1 python/*.py 2>/dev/null | xargs -n 1 basename
    exit 1
fi

SCRIPT_NAME=$1

# Check if the script exists in python/ directory
if [ ! -f "python/$SCRIPT_NAME" ]; then
    echo -e "${RED}Error: Script 'python/$SCRIPT_NAME' not found${NC}"
    echo ""
    echo "Available scripts in python/:"
    ls -1 python/*.py 2>/dev/null | xargs -n 1 basename
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Run the Python script
echo -e "${GREEN}Running python/$SCRIPT_NAME...${NC}"
echo ""
python3 "python/$SCRIPT_NAME"

