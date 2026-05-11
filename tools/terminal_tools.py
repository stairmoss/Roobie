"""
Roobie Terminal Tools
Execute shell commands with timeout, streaming output, and safety checks.
"""

import subprocess
import os
import signal
import threading
from pathlib import Path
from typing import Dict, Optional, Callable


# Commands that are dangerous and need extra caution
DANGEROUS_PATTERNS = [
    "rm -rf /", "rm -rf ~", "mkfs", "dd if=", ":(){", "chmod -R 777 /",
    "wget.*|.*sh", "curl.*|.*sh", "> /dev/sda",
]


class TerminalTools:
    """Shell command execution scoped to a workspace directory."""

    def __init__(self, workspace_dir: str):
        self.workspace = Path(workspace_dir).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self._processes: Dict[str, subprocess.Popen] = {}
        self._process_counter = 0

    def _is_dangerous(self, command: str) -> bool:
        """Check if a command is potentially dangerous."""
        cmd_lower = command.lower().strip()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in cmd_lower:
                return True
        return False

    def run_command(self, command: str, cwd: str = None, timeout: int = 60,
                    on_output: Optional[Callable] = None) -> Dict:
        """Run a shell command and return the result."""
        if self._is_dangerous(command):
            return {
                "success": False,
                "error": f"Potentially dangerous command blocked: {command}",
                "exit_code": -1
            }

        work_dir = self.workspace
        if cwd:
            work_dir = (self.workspace / cwd).resolve()
            if not str(work_dir).startswith(str(self.workspace)):
                return {"success": False, "error": "Path traversal detected", "exit_code": -1}

        if not work_dir.exists():
            work_dir.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["PAGER"] = "cat"  # Prevent paging

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=str(work_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                preexec_fn=os.setsid if os.name != 'nt' else None,
            )

            stdout_data = []
            stderr_data = []

            def read_stream(stream, collector):
                for line in iter(stream.readline, b''):
                    text = line.decode('utf-8', errors='replace')
                    collector.append(text)
                    if on_output:
                        on_output(text)

            stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, stdout_data))
            stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, stderr_data))
            stdout_thread.start()
            stderr_thread.start()

            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
                return {
                    "success": False,
                    "stdout": "".join(stdout_data),
                    "stderr": "".join(stderr_data),
                    "error": f"Command timed out after {timeout}s",
                    "exit_code": -1
                }

            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)

            stdout = "".join(stdout_data)
            stderr = "".join(stderr_data)

            # Truncate very long outputs
            max_output = 50000
            if len(stdout) > max_output:
                stdout = stdout[:max_output] + f"\n... (truncated, {len(stdout)} total chars)"
            if len(stderr) > max_output:
                stderr = stderr[:max_output] + f"\n... (truncated, {len(stderr)} total chars)"

            return {
                "success": process.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode,
                "command": command,
                "cwd": str(work_dir)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exit_code": -1,
                "command": command
            }

    def start_background(self, command: str, cwd: str = None) -> Dict:
        """Start a long-running background process (like a dev server)."""
        work_dir = self.workspace
        if cwd:
            work_dir = (self.workspace / cwd).resolve()

        env = os.environ.copy()

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=str(work_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                preexec_fn=os.setsid if os.name != 'nt' else None,
            )

            self._process_counter += 1
            pid = str(self._process_counter)
            self._processes[pid] = process

            return {
                "success": True,
                "pid": pid,
                "system_pid": process.pid,
                "command": command,
                "message": f"Background process started (ID: {pid})"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_background(self, pid: str) -> Dict:
        """Stop a background process."""
        process = self._processes.get(pid)
        if not process:
            return {"success": False, "error": f"Process {pid} not found"}

        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=5)
            del self._processes[pid]
            return {"success": True, "message": f"Process {pid} stopped"}
        except Exception as e:
            try:
                process.kill()
                del self._processes[pid]
            except Exception:
                pass
            return {"success": True, "message": f"Process {pid} force-killed"}

    def list_background(self) -> Dict:
        """List running background processes."""
        procs = []
        for pid, proc in list(self._processes.items()):
            status = "running" if proc.poll() is None else f"exited ({proc.returncode})"
            procs.append({"pid": pid, "system_pid": proc.pid, "status": status})
        return {"success": True, "processes": procs}
