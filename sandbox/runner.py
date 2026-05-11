"""
Roobie Sandbox Runner
Scaffolds projects, writes generated files to disk, installs deps,
and starts development servers for localhost preview.
"""

import os
import subprocess
import time
import signal
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console

console = Console()


class SandboxRunner:
    """Manages project scaffolding and localhost dev servers."""

    def __init__(self, settings):
        self.settings = settings
        self.projects_dir = Path(settings.sandbox.projects_dir).expanduser()
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self._server_process = None

    def scaffold_project(self, name: str, template: str = "nextjs",
                         files: Dict[str, str] = None) -> str:
        """Create project directory and write all generated files."""
        project_path = self.projects_dir / name
        project_path.mkdir(parents=True, exist_ok=True)

        if files:
            for rel_path, content in files.items():
                file_path = project_path / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(content)
                console.print(f"  📄 {rel_path}")

        console.print(f"[green]✅ Project scaffolded at: {project_path}[/green]")
        return str(project_path)

    def install_dependencies(self, project_name: str) -> bool:
        """Install npm dependencies for a project."""
        project_path = self.projects_dir / project_name
        package_json = project_path / "package.json"

        if not package_json.exists():
            console.print("[yellow]⚠️ No package.json found[/yellow]")
            return False

        console.print("[cyan]Installing dependencies...[/cyan]")
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(project_path),
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                console.print("[green]✅ Dependencies installed[/green]")
                return True
            else:
                console.print(f"[red]❌ npm install failed: {result.stderr[:200]}[/red]")
                return False
        except subprocess.TimeoutExpired:
            console.print("[red]❌ npm install timed out[/red]")
            return False
        except FileNotFoundError:
            console.print("[red]❌ npm not found. Install Node.js first.[/red]")
            return False

    def start_dev_server(self, project_name: str, port: int = None) -> int:
        """Start the development server."""
        port = port or self.settings.sandbox.default_port
        project_path = self.projects_dir / project_name

        if not (project_path / "node_modules").exists():
            self.install_dependencies(project_name)

        console.print(f"[cyan]Starting dev server on port {port}...[/cyan]")

        env = os.environ.copy()
        env["PORT"] = str(port)

        try:
            self._server_process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", str(port)],
                cwd=str(project_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )

            # Wait for server to start
            time.sleep(3)

            if self._server_process.poll() is None:
                console.print(f"[green]✅ Dev server running on port {port}[/green]")

                if self.settings.sandbox.auto_open_browser:
                    self._open_browser(f"http://localhost:{port}")

                return port
            else:
                stderr = self._server_process.stderr.read().decode()[:300]
                console.print(f"[red]❌ Server failed to start: {stderr}[/red]")
                return port

        except FileNotFoundError:
            console.print("[red]❌ npm not found[/red]")
            return port

    def stop_dev_server(self):
        """Stop the running development server."""
        if self._server_process and self._server_process.poll() is None:
            try:
                os.killpg(os.getpgid(self._server_process.pid), signal.SIGTERM)
                self._server_process.wait(timeout=5)
                console.print("[green]✅ Dev server stopped[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️ Error stopping server: {e}[/yellow]")
                try:
                    self._server_process.kill()
                except Exception:
                    pass

    def check_server_health(self, port: int = 3000) -> bool:
        """Check if the dev server is responding."""
        import requests
        try:
            r = requests.get(f"http://localhost:{port}", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def get_server_logs(self) -> str:
        """Get stdout/stderr from the dev server."""
        if self._server_process:
            try:
                stdout = self._server_process.stdout.read1(4096).decode()
                return stdout
            except Exception:
                pass
        return ""

    def _open_browser(self, url: str):
        """Open URL in default browser."""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            console.print(f"[dim]Open manually: {url}[/dim]")

    def write_file(self, project_name: str, rel_path: str, content: str):
        """Write a single file to a project."""
        file_path = self.projects_dir / project_name / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)

    def read_file(self, project_name: str, rel_path: str) -> Optional[str]:
        """Read a file from a project."""
        file_path = self.projects_dir / project_name / rel_path
        if file_path.exists():
            with open(file_path) as f:
                return f.read()
        return None

    def list_files(self, project_name: str) -> list:
        """List all files in a project."""
        project_path = self.projects_dir / project_name
        if not project_path.exists():
            return []
        files = []
        for f in project_path.rglob("*"):
            if f.is_file() and "node_modules" not in str(f) and ".next" not in str(f):
                files.append(str(f.relative_to(project_path)))
        return sorted(files)
