#!/usr/bin/env python3
"""
Roobie — Entry Point

Usage:
    python main.py          → Interactive chat (default)
    python main.py chat     → Interactive chat
    python main.py run "..."  → One-shot task
    python main.py status   → System status
    python main.py search "..." → Web search
"""

import sys
import os

if sys.version_info < (3, 9):
    print("⚠️ Warning: Roobie requires Python 3.9 or higher. You are running Python " + 
          sys.version.split()[0] + ". Some features may not work correctly.", file=sys.stderr)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure ~/.roobie directory exists
os.makedirs(os.path.expanduser("~/.roobie"), exist_ok=True)

from cli.app import app

def main():
    app()

if __name__ == "__main__":
    main()

