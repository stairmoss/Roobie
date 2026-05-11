"""
Roobie MCP Server Integration
Provides MCP tool interfaces for filesystem, terminal, playwright,
github, docker, and sqlite operations.
"""

import os
import subprocess
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console

console = Console()


class MCPServer:
    """MCP tool server providing external integrations."""

    def __init__(self, settings=None):
        self.settings = settings
        self._tools = self._register_tools()

    def _register_tools(self) -> Dict[str, callable]:
        """Register all MCP tools."""
        return {
            "filesystem_read": self.filesystem_read,
            "filesystem_write": self.filesystem_write,
            "filesystem_list": self.filesystem_list,
            "terminal_run": self.terminal_run,
            "sqlite_query": self.sqlite_query,
        }

    def list_tools(self) -> List[Dict]:
        """List all available MCP tools."""
        return [
            {"name": "filesystem_read", "description": "Read a file from disk"},
            {"name": "filesystem_write", "description": "Write content to a file"},
            {"name": "filesystem_list", "description": "List directory contents"},
            {"name": "terminal_run", "description": "Execute a shell command"},
            {"name": "sqlite_query", "description": "Execute SQLite query"},
        ]

    def execute(self, tool_name: str, params: Dict) -> Any:
        """Execute an MCP tool by name."""
        if tool_name not in self._tools:
            return {"error": f"Unknown tool: {tool_name}"}
        try:
            return self._tools[tool_name](**params)
        except Exception as e:
            return {"error": str(e)}

    # ── Filesystem Tools ──────────────────────────────────────

    def filesystem_read(self, path: str) -> Dict:
        """Read a file."""
        p = Path(path).expanduser()
        if not p.exists():
            return {"error": f"File not found: {path}"}
        if not p.is_file():
            return {"error": f"Not a file: {path}"}
        try:
            content = p.read_text(encoding="utf-8")
            return {"path": str(p), "content": content, "size": p.stat().st_size}
        except Exception as e:
            return {"error": str(e)}

    def filesystem_write(self, path: str, content: str) -> Dict:
        """Write to a file (creates directories as needed)."""
        p = Path(path).expanduser()
        # Safety check: prevent writing outside project directories
        if not self._is_safe_path(p):
            return {"error": "Write denied: path outside project scope"}
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"path": str(p), "written": len(content)}

    def filesystem_list(self, path: str, recursive: bool = False) -> Dict:
        """List directory contents."""
        p = Path(path).expanduser()
        if not p.exists():
            return {"error": f"Path not found: {path}"}
        if not p.is_dir():
            return {"error": f"Not a directory: {path}"}

        entries = []
        iterator = p.rglob("*") if recursive else p.iterdir()
        for entry in iterator:
            if "node_modules" in str(entry) or ".next" in str(entry):
                continue
            entries.append({
                "name": entry.name,
                "path": str(entry),
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else 0,
            })
        return {"path": str(p), "entries": entries[:200]}

    # ── Terminal Tools ────────────────────────────────────────

    def terminal_run(self, command: str, cwd: str = None, timeout: int = 30) -> Dict:
        """Execute a shell command (with safety checks)."""
        # Safety: block dangerous commands
        dangerous = ["rm -rf /", "rm -rf ~", "mkfs", "dd if=", "> /dev/"]
        for d in dangerous:
            if d in command:
                return {"error": f"Dangerous command blocked: {command}"}

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                cwd=cwd, timeout=timeout,
            )
            return {
                "command": command,
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:2000],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"error": str(e)}

    # ── SQLite Tools ──────────────────────────────────────────

    def sqlite_query(self, db_path: str, query: str) -> Dict:
        """Execute a read-only SQLite query."""
        p = Path(db_path).expanduser()
        if not p.exists():
            return {"error": f"Database not found: {db_path}"}

        # Safety: only allow SELECT queries
        q = query.strip().upper()
        if not q.startswith("SELECT") and not q.startswith("PRAGMA"):
            return {"error": "Only SELECT and PRAGMA queries allowed"}

        try:
            conn = sqlite3.connect(str(p))
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            rows = [dict(row) for row in cursor.fetchall()[:100]]
            conn.close()
            return {"query": query, "rows": rows, "count": len(rows)}
        except Exception as e:
            return {"error": str(e)}

    def _is_safe_path(self, path: Path) -> bool:
        """Check if a path is safe to write to."""
        resolved = path.resolve()
        home = Path.home()
        # Allow writes under home directory and project directories
        safe_prefixes = [
            home / ".roobie",
            Path("/tmp/roobie"),
        ]
        if self.settings:
            safe_prefixes.append(Path(self.settings.sandbox.projects_dir).expanduser())

        return any(str(resolved).startswith(str(sp)) for sp in safe_prefixes)
