#!/bin/bash
# Launch script for continuous RowHammer-inspired search
# This script runs the search and properly handles output redirection

echo "==== Starting RowHammer-Inspired Search for Term 68 ===="
echo "Target Address: 1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ"
echo "Search will run continuously until a match is found or interrupted"
echo "Output is being logged to rowhammer_search.log"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Check if required libraries are installed
echo "Checking required Python libraries..."
python3 -c "import hashlib, base58, ecdsa" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Required Python libraries are missing."
    echo "Please install them with: pip install base58 ecdsa"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Get current timestamp for log files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Run the search script with output redirection
echo "Starting search at $(date)"
echo "Press Ctrl+C to stop the search"

# Run the main search script 
python3 ./rowhammer_search.py 2>&1 | tee -a "logs/rowhammer_search_${TIMESTAMP}.log"

# Check if the script found a solution
if [ -f "term68_solution.txt" ]; then
    echo ""
    echo "========== SOLUTION FOUND =========="
    cat term68_solution.txt
    echo "==================================="
    echo ""
    echo "Details saved to term68_solution.txt and term68_rowhammer_result.json"
fi

echo "Search completed or interrupted at $(date)"
echo "Log saved to logs/rowhammer_search_${TIMESTAMP}.log" 