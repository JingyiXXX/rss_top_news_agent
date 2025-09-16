#!/usr/bin/env python3
"""
RSS News Agent - Main entry point
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rss_agent.agent import main

if __name__ == "__main__":
    main()