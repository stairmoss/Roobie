"""
Roobie Tools Package
Real tool execution for the agentic coding assistant.
"""

from tools.file_tools import FileTools
from tools.terminal_tools import TerminalTools
from tools.search_tools import SearchTools
from tools.thinking_tools import ThinkingTools

TOOL_DEFINITIONS = [
    {
        "name": "think",
        "description": "Think step-by-step about the problem, plan your approach, reason about architecture, debug issues. Use this before taking complex actions.",
        "parameters": {
            "thought": {"type": "string", "description": "Your detailed thinking/reasoning", "required": True}
        }
    },
    {
        "name": "create_file",
        "description": "Create a new file with the given content. Creates parent directories automatically.",
        "parameters": {
            "path": {"type": "string", "description": "Relative file path to create", "required": True},
            "content": {"type": "string", "description": "File content to write", "required": True}
        }
    },
    {
        "name": "edit_file",
        "description": "Edit an existing file by replacing old content with new content.",
        "parameters": {
            "path": {"type": "string", "description": "Relative file path to edit", "required": True},
            "old_content": {"type": "string", "description": "Exact content to find and replace", "required": True},
            "new_content": {"type": "string", "description": "New content to replace with", "required": True}
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "parameters": {
            "path": {"type": "string", "description": "Relative file path to read", "required": True}
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file or empty directory.",
        "parameters": {
            "path": {"type": "string", "description": "Relative file path to delete", "required": True}
        }
    },
    {
        "name": "list_directory",
        "description": "List all files and directories at the given path.",
        "parameters": {
            "path": {"type": "string", "description": "Relative directory path to list (use '.' for current)", "required": True}
        }
    },
    {
        "name": "create_folder",
        "description": "Create a new directory (and parent directories).",
        "parameters": {
            "path": {"type": "string", "description": "Relative directory path to create", "required": True}
        }
    },
    {
        "name": "run_command",
        "description": "Run a shell command in the project directory. Use for installing packages, running scripts, starting servers, etc.",
        "parameters": {
            "command": {"type": "string", "description": "Shell command to execute", "required": True},
            "cwd": {"type": "string", "description": "Working directory (relative, default: project root)", "required": False}
        }
    },
    {
        "name": "web_search",
        "description": "Search the web for information. No API key required.",
        "parameters": {
            "query": {"type": "string", "description": "Search query", "required": True}
        }
    },
]

__all__ = ["FileTools", "TerminalTools", "SearchTools", "ThinkingTools", "TOOL_DEFINITIONS"]
