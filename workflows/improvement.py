"""
Roobie Improvement Workflow
Autonomous improvement loop: generate → preview → screenshot → analyze → fix → repeat.
Runs until quality targets are met or max iterations reached.
"""

import time
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class ImprovementWorkflow:
    """Autonomous improvement loop for continuous website refinement."""

    def __init__(self, settings):
        self.settings = settings
        self.max_loops = settings.max_improvement_loops
        self._browser = None
        self._vision = None
        self._model = None
        self._sandbox = None
        self._memory = None

    @property
    def browser(self):
        if self._browser is None:
            from browser.automation import BrowserAutomation
            self._browser = BrowserAutomation(self.settings)
        return self._browser

    @property
    def vision(self):
        if self._vision is None:
            from vision.analyzer import VisionAnalyzer
            self._vision = VisionAnalyzer(self.settings)
        return self._vision

    @property
    def model(self):
        if self._model is None:
            from models.manager import ModelManager
            self._model = ModelManager(self.settings)
        return self._model

    @property
    def sandbox(self):
        if self._sandbox is None:
            from sandbox.runner import SandboxRunner
            self._sandbox = SandboxRunner(self.settings)
        return self._sandbox

    @property
    def memory(self):
        if self._memory is None:
            from memory.store import MemoryStore
            self._memory = MemoryStore(self.settings.memory.sqlite_db)
        return self._memory

    def run(self, project_name: str, url: str = None, max_loops: int = None):
        """Run the autonomous improvement loop."""
        max_loops = max_loops or self.max_loops
        port = self.settings.sandbox.default_port
        url = url or f"http://localhost:{port}"

        console.print(Panel(
            f"[bold]Starting improvement loop for:[/bold] {project_name}\n"
            f"[bold]URL:[/bold] {url}\n"
            f"[bold]Max loops:[/bold] {max_loops}",
            title="🔄 Improvement Loop",
            border_style="cyan",
        ))

        # Ensure dev server is running
        if not self.sandbox.check_server_health(port):
            console.print("[cyan]Starting dev server...[/cyan]")
            self.sandbox.start_dev_server(project_name, port)
            time.sleep(5)

        project = self.memory.get_project(project_name)
        project_id = project["id"] if project else None

        for loop_num in range(1, max_loops + 1):
            console.print(f"\n[bold cyan]━━━ Loop {loop_num}/{max_loops} ━━━[/bold cyan]")

            # Step 1: Capture screenshots
            console.print("[cyan]📸 Capturing screenshots...[/cyan]")
            screenshots = self.browser.capture_screenshots(project_name, url, mobile=True)

            if not screenshots:
                console.print("[yellow]⚠️ No screenshots captured, skipping loop[/yellow]")
                continue

            # Step 2: Analyze with vision
            console.print("[cyan]👁️ Analyzing with AI vision...[/cyan]")
            report = self.vision.analyze_screenshots(screenshots)
            issues = report.get("issues", [])
            score = report.get("overall_score", 0)

            console.print(f"  Score: [{'green' if score >= 7 else 'yellow' if score >= 5 else 'red'}]{score}/10[/]")
            console.print(f"  Issues found: {len(issues)}")

            # Step 3: Check if quality target met
            if score >= 8 and len(issues) <= 2:
                console.print("[bold green]✅ Quality target reached! Stopping improvement loop.[/bold green]")
                if project_id:
                    self.memory.log_improvement(project_id, loop_num, issues, [],
                                               {"score": score}, {"score": score})
                break

            # Step 4: Generate fixes
            if issues:
                console.print("[cyan]🔧 Generating fixes...[/cyan]")
                fixes = self._generate_fixes(issues, project_name)

                # Step 5: Apply fixes
                if fixes:
                    console.print(f"[cyan]📝 Applying {len(fixes)} fixes...[/cyan]")
                    applied = self._apply_fixes(fixes, project_name)
                    console.print(f"  Applied {applied} fixes")

                    # Log improvement
                    if project_id:
                        self.memory.log_improvement(
                            project_id, loop_num, issues, fixes,
                            {"score": score}, {}
                        )

            # Step 6: Wait for dev server to reload
            console.print("[dim]Waiting for server reload...[/dim]")
            time.sleep(3)

        console.print(Panel(
            f"[bold green]Improvement loop complete[/bold green]\n"
            f"Loops executed: {min(loop_num, max_loops)}\n"
            f"Final score: {score}/10",
            title="✅ Done",
            border_style="green",
        ))

        # Cleanup
        try:
            self.browser.close()
        except Exception:
            pass

    def _generate_fixes(self, issues: List[Dict], project_name: str) -> List[Dict]:
        """Generate code fixes for detected issues."""
        from prompts.templates import PromptTemplates

        issue_descriptions = "\n".join(
            f"- [{i.get('viewport', 'desktop')}] {i.get('type', 'general')}: {i.get('issue', '')}"
            for i in issues[:8]
        )

        # Get current project files for context
        files_list = self.sandbox.list_files(project_name)
        relevant_files = [f for f in files_list if f.endswith((".tsx", ".css", ".ts"))][:10]

        file_contents = {}
        for f in relevant_files[:5]:
            content = self.sandbox.read_file(project_name, f)
            if content and len(content) < 3000:
                file_contents[f] = content

        context = "\n".join(f"--- {k} ---\n{v[:1500]}" for k, v in file_contents.items())

        prompt = f"""{PromptTemplates.IMPROVEMENT_PROMPT}

Issues detected:
{issue_descriptions}

Current project files:
{context[:4000]}

Generate fixes as JSON array: [{{"file": "relative/path.tsx", "description": "what to fix", "code": "fixed code"}}]
Output ONLY valid JSON."""

        response = self.model.generate(
            prompt, model=self.settings.models.coding_model,
            temperature=0.4, stream=False
        )

        return self._parse_fixes(response)

    def _parse_fixes(self, response: str) -> List[Dict]:
        """Parse fix suggestions from AI response."""
        import json

        # Try to extract JSON
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            elif "[" in response:
                start = response.index("[")
                end = response.rindex("]") + 1
                json_str = response[start:end]
            else:
                return []

            fixes = json.loads(json_str.strip())
            if isinstance(fixes, list):
                return fixes
        except (json.JSONDecodeError, ValueError, IndexError):
            pass

        return []

    def _apply_fixes(self, fixes: List[Dict], project_name: str) -> int:
        """Apply generated fixes to project files."""
        applied = 0
        for fix in fixes:
            file_path = fix.get("file", "")
            code = fix.get("code", "")
            if file_path and code:
                try:
                    self.sandbox.write_file(project_name, file_path, code)
                    applied += 1
                    console.print(f"  ✅ Fixed: {file_path}")
                except Exception as e:
                    console.print(f"  ❌ Failed: {file_path} ({e})")

        return applied
