#!/bin/bash
# Simple script to run the Guest List & Family Tree application

echo "Starting Guest List & Family Tree application..."
echo "Make sure you have installed the requirements: pip install -r requirements.txt"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: Streamlit is not installed. Please run: pip install -r requirements.txt"
    exit 1
fi

# Run the application
streamlit run main.py
