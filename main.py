#!/usr/bin/env python3
"""
Roobie — Autonomous Local-First AI Coding Assistant
Like Claude Code, but runs locally with Ollama.

Usage:
    python main.py              → Interactive chat (default)
    python main.py chat         → Interactive chat
    python main.py run "..."    → One-shot task
    python main.py search "..." → Web search
    python main.py status       → System status
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Launch Roobie CLI."""
    # Ensure ~/.roobie directory exists
    roobie_dir = os.path.expanduser("~/.roobie")
    os.makedirs(roobie_dir, exist_ok=True)

    from cli.app import app
    app()


if __name__ == "__main__":
    main()
