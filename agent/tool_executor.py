"""
Roobie Tool Executor
Dispatches tool calls to the appropriate tool handler and formats results.
"""

import json
from typing import Dict, Optional, Callable
from tools.file_tools import FileTools
from tools.terminal_tools import TerminalTools
from tools.search_tools import SearchTools
from tools.thinking_tools import ThinkingTools


class ToolExecutor:
    """Executes tool calls and returns formatted results."""

    def __init__(self, workspace_dir: str):
        self.file_tools = FileTools(workspace_dir)
        self.terminal_tools = TerminalTools(workspace_dir)
        self.search_tools = SearchTools()
        self.thinking_tools = ThinkingTools()
        self.workspace_dir = workspace_dir
        self._event_callback: Optional[Callable] = None

    def set_event_callback(self, callback: Callable):
        """Set callback for streaming events to the UI."""
        self._event_callback = callback

    def _emit(self, event_type: str, data: dict):
        """Emit an event to the UI."""
        if self._event_callback:
            self._event_callback(event_type, data)

    def execute(self, tool_name: str, params: Dict) -> Dict:
        """Execute a tool by name with given parameters."""
        try:
            result = self._dispatch(tool_name, params)
        except Exception as e:
            result = {"success": False, "error": str(e)}
        return result

    def _dispatch(self, tool_name: str, params: Dict) -> Dict:
        """Route tool call to the correct handler."""
        handlers = {
            "think": self._handle_think,
            "create_file": self._handle_create_file,
            "edit_file": self._handle_edit_file,
            "read_file": self._handle_read_file,
            "delete_file": self._handle_delete_file,
            "list_directory": self._handle_list_directory,
            "create_folder": self._handle_create_folder,
            "run_command": self._handle_run_command,
            "web_search": self._handle_web_search,
        }

        handler = handlers.get(tool_name)
        if not handler:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        return handler(params)

    def _handle_think(self, params: Dict) -> Dict:
        return self.thinking_tools.think(params.get("thought", ""))

    def _handle_create_file(self, params: Dict) -> Dict:
        return self.file_tools.create_file(
            params.get("path", ""),
            params.get("content", "")
        )

    def _handle_edit_file(self, params: Dict) -> Dict:
        return self.file_tools.edit_file(
            params.get("path", ""),
            params.get("old_content", ""),
            params.get("new_content", "")
        )

    def _handle_read_file(self, params: Dict) -> Dict:
        return self.file_tools.read_file(params.get("path", ""))

    def _handle_delete_file(self, params: Dict) -> Dict:
        return self.file_tools.delete_file(params.get("path", ""))

    def _handle_list_directory(self, params: Dict) -> Dict:
        return self.file_tools.list_directory(params.get("path", "."))

    def _handle_create_folder(self, params: Dict) -> Dict:
        return self.file_tools.create_folder(params.get("path", ""))

    def _handle_run_command(self, params: Dict) -> Dict:
        def on_output(text):
            self._emit("terminal_output", {"text": text})

        return self.terminal_tools.run_command(
            params.get("command", ""),
            cwd=params.get("cwd"),
            timeout=int(params.get("timeout", 60)),
            on_output=on_output
        )

    def _handle_web_search(self, params: Dict) -> Dict:
        return self.search_tools.web_search(
            params.get("query", ""),
            max_results=int(params.get("max_results", 8))
        )

    def get_file_tree(self) -> Dict:
        """Get the workspace file tree."""
        return self.file_tools.get_tree(".", max_depth=4)
