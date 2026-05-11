"""
Roobie Thinking Tools
Structured thinking/reasoning for the agent.
"""

from typing import Dict
from datetime import datetime


class ThinkingTools:
    """Handles structured thinking/reasoning display."""

    def __init__(self):
        self.thoughts = []

    def think(self, thought: str) -> Dict:
        """Record a thinking step."""
        entry = {
            "thought": thought,
            "timestamp": datetime.now().isoformat(),
            "step": len(self.thoughts) + 1
        }
        self.thoughts.append(entry)
        return {
            "success": True,
            "step": entry["step"],
            "thought": thought,
            "message": f"Thinking step {entry['step']} recorded"
        }

    def get_thoughts(self) -> list:
        """Get all thinking steps."""
        return self.thoughts

    def clear(self):
        """Clear thinking history."""
        self.thoughts = []
