#!/usr/bin/env python3
"""
Main entry point for the Guest List & Family Tree application.
Run this file to start the Streamlit application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from guest_list_app.app import main

if __name__ == "__main__":
    main()
