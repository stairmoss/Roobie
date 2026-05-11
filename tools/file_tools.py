"""
Roobie File Tools
Real filesystem operations: create, read, edit, delete files and directories.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class FileTools:
    """File system operations scoped to a project directory."""

    def __init__(self, workspace_dir: str):
        self.workspace = Path(workspace_dir).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _resolve(self, rel_path: str) -> Path:
        """Resolve a relative path within the workspace, preventing path traversal."""
        resolved = (self.workspace / rel_path).resolve()
        if not str(resolved).startswith(str(self.workspace)):
            raise ValueError(f"Path traversal detected: {rel_path}")
        return resolved

    def create_file(self, path: str, content: str) -> Dict:
        """Create a file with content. Creates parent dirs automatically."""
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "path": path,
            "size": len(content),
            "message": f"Created {path} ({len(content)} bytes)"
        }

    def read_file(self, path: str) -> Dict:
        """Read file contents."""
        target = self._resolve(path)
        if not target.exists():
            return {"success": False, "error": f"File not found: {path}"}
        if not target.is_file():
            return {"success": False, "error": f"Not a file: {path}"}
        try:
            content = target.read_text(encoding="utf-8")
            return {
                "success": True,
                "path": path,
                "content": content,
                "size": len(content),
                "lines": content.count("\n") + 1
            }
        except UnicodeDecodeError:
            return {"success": False, "error": f"Binary file, cannot read as text: {path}"}

    def edit_file(self, path: str, old_content: str, new_content: str) -> Dict:
        """Edit a file by replacing old_content with new_content."""
        target = self._resolve(path)
        if not target.exists():
            return {"success": False, "error": f"File not found: {path}"}

        current = target.read_text(encoding="utf-8")
        if old_content not in current:
            return {
                "success": False,
                "error": f"Target content not found in {path}. File has {len(current)} chars."
            }

        new_file = current.replace(old_content, new_content, 1)
        target.write_text(new_file, encoding="utf-8")
        return {
            "success": True,
            "path": path,
            "message": f"Edited {path}: replaced {len(old_content)} chars with {len(new_content)} chars"
        }

    def delete_file(self, path: str) -> Dict:
        """Delete a file or empty directory."""
        target = self._resolve(path)
        if not target.exists():
            return {"success": False, "error": f"Not found: {path}"}

        if target.is_file():
            target.unlink()
            return {"success": True, "path": path, "message": f"Deleted file: {path}"}
        elif target.is_dir():
            if any(target.iterdir()):
                # Delete non-empty dirs too (like rm -rf) but be cautious
                shutil.rmtree(str(target))
                return {"success": True, "path": path, "message": f"Deleted directory: {path}"}
            else:
                target.rmdir()
                return {"success": True, "path": path, "message": f"Deleted empty directory: {path}"}

    def list_directory(self, path: str = ".") -> Dict:
        """List directory contents with file types and sizes."""
        target = self._resolve(path)
        if not target.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
        if not target.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}

        entries = []
        try:
            for item in sorted(target.iterdir()):
                rel = str(item.relative_to(self.workspace))
                if item.name.startswith(".") and item.name not in (".env", ".gitignore"):
                    continue
                if item.name in ("node_modules", "__pycache__", ".next", ".git", "venv", ".venv"):
                    continue
                entry = {
                    "name": item.name,
                    "path": rel,
                    "type": "directory" if item.is_dir() else "file",
                }
                if item.is_file():
                    entry["size"] = item.stat().st_size
                elif item.is_dir():
                    try:
                        entry["children"] = sum(1 for _ in item.iterdir())
                    except PermissionError:
                        entry["children"] = 0
                entries.append(entry)
        except PermissionError:
            return {"success": False, "error": f"Permission denied: {path}"}

        return {
            "success": True,
            "path": path,
            "entries": entries,
            "count": len(entries)
        }

    def create_folder(self, path: str) -> Dict:
        """Create a directory (and parents)."""
        target = self._resolve(path)
        target.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "path": path,
            "message": f"Created directory: {path}"
        }

    def get_tree(self, path: str = ".", max_depth: int = 3) -> Dict:
        """Get a recursive file tree."""
        target = self._resolve(path)
        if not target.exists() or not target.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}

        def _build_tree(dir_path: Path, depth: int = 0) -> List[Dict]:
            if depth >= max_depth:
                return []
            items = []
            try:
                for item in sorted(dir_path.iterdir()):
                    if item.name.startswith(".") and item.name not in (".env", ".gitignore"):
                        continue
                    if item.name in ("node_modules", "__pycache__", ".next", ".git", "venv", ".venv"):
                        continue
                    node = {
                        "name": item.name,
                        "path": str(item.relative_to(self.workspace)),
                        "type": "directory" if item.is_dir() else "file",
                    }
                    if item.is_dir():
                        node["children"] = _build_tree(item, depth + 1)
                    else:
                        node["size"] = item.stat().st_size
                    items.append(node)
            except PermissionError:
                pass
            return items

        return {
            "success": True,
            "tree": _build_tree(target)
        }
