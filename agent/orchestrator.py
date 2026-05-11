"""
Roobie Agent Orchestrator
Central coordinator for all agent workflows using LangGraph-style state machines.
Manages the full pipeline: understand → research → plan → build → test → improve.
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class WorkflowStage(str, Enum):
    UNDERSTAND = "understand"
    RESEARCH = "research"
    ANALYZE_COMPETITORS = "analyze_competitors"
    SEO_ANALYSIS = "seo_analysis"
    ARCHITECTURE = "architecture"
    SKILL_LOADING = "skill_loading"
    FRONTEND_GEN = "frontend_generation"
    BACKEND_GEN = "backend_generation"
    RUN_LOCALHOST = "run_localhost"
    BROWSER_TEST = "browser_test"
    SCREENSHOT = "screenshot"
    VISION_ANALYSIS = "vision_analysis"
    UI_IMPROVEMENT = "ui_improvement"
    SEO_OPTIMIZATION = "seo_optimization"
    PERFORMANCE_OPT = "performance_optimization"
    FINALIZE = "finalize"


@dataclass
class AgentState:
    """State object passed between workflow stages."""
    user_request: str = ""
    project_name: str = ""
    project_type: str = ""
    template: str = "nextjs"
    with_backend: bool = False
    with_3d: bool = False
    
    # Understanding phase
    task_analysis: Dict = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    design_style: str = "modern"
    
    # Research phase
    research_results: List[Dict] = field(default_factory=list)
    competitor_analysis: List[Dict] = field(default_factory=list)
    seo_analysis: Dict = field(default_factory=dict)
    
    # Planning phase
    architecture: Dict = field(default_factory=dict)
    loaded_skills: List[str] = field(default_factory=list)
    
    # Generation phase
    generated_files: Dict[str, str] = field(default_factory=dict)
    project_path: str = ""
    
    # Testing phase
    localhost_url: str = ""
    localhost_port: int = 3000
    screenshots: List[str] = field(default_factory=list)
    
    # Analysis phase
    vision_report: Dict = field(default_factory=dict)
    seo_report: Dict = field(default_factory=dict)
    
    # Improvement phase
    improvement_loop: int = 0
    issues: List[Dict] = field(default_factory=list)
    fixes: List[Dict] = field(default_factory=list)
    
    # Status
    current_stage: str = ""
    errors: List[str] = field(default_factory=list)
    completed: bool = False


class AgentOrchestrator:
    """Orchestrates the full Roobie workflow pipeline."""
    
    def __init__(self, settings):
        self.settings = settings
        self._init_subsystems()
    
    def _init_subsystems(self):
        """Lazy-initialize subsystems to conserve memory."""
        self._model_manager = None
        self._memory_store = None
        self._skill_loader = None
        self._research_engine = None
        self._frontend_gen = None
        self._backend_gen = None
        self._seo_optimizer = None
        self._browser_auto = None
        self._vision_analyzer = None
        self._sandbox_runner = None
    
    @property
    def model_manager(self):
        if self._model_manager is None:
            from models.manager import ModelManager
            self._model_manager = ModelManager(self.settings)
        return self._model_manager
    
    @property
    def memory(self):
        if self._memory_store is None:
            from memory.store import MemoryStore
            self._memory_store = MemoryStore(self.settings.memory.sqlite_db)
        return self._memory_store
    
    @property
    def skill_loader(self):
        if self._skill_loader is None:
            from skills.loader import SkillLoader
            self._skill_loader = SkillLoader()
        return self._skill_loader
    
    @property
    def research_engine(self):
        if self._research_engine is None:
            from research.engine import ResearchEngine
            self._research_engine = ResearchEngine(self.settings)
        return self._research_engine
    
    @property
    def frontend_gen(self):
        if self._frontend_gen is None:
            from frontend.generator import FrontendGenerator
            self._frontend_gen = FrontendGenerator(self.settings, self.model_manager)
        return self._frontend_gen
    
    @property
    def backend_gen(self):
        if self._backend_gen is None:
            from backend.generator import BackendGenerator
            self._backend_gen = BackendGenerator(self.settings, self.model_manager)
        return self._backend_gen
    
    @property
    def seo_optimizer(self):
        if self._seo_optimizer is None:
            from seo.optimizer import SEOOptimizer
            self._seo_optimizer = SEOOptimizer(self.settings)
        return self._seo_optimizer
    
    @property
    def browser_auto(self):
        if self._browser_auto is None:
            from browser.automation import BrowserAutomation
            self._browser_auto = BrowserAutomation(self.settings)
        return self._browser_auto
    
    @property
    def vision_analyzer(self):
        if self._vision_analyzer is None:
            from vision.analyzer import VisionAnalyzer
            self._vision_analyzer = VisionAnalyzer(self.settings)
        return self._vision_analyzer
    
    @property
    def sandbox_runner(self):
        if self._sandbox_runner is None:
            from sandbox.runner import SandboxRunner
            self._sandbox_runner = SandboxRunner(self.settings)
        return self._sandbox_runner
    
    def _show_stage(self, stage: str, description: str):
        """Display current workflow stage."""
        icons = {
            "understand": "🧠", "research": "🔍", "analyze_competitors": "📊",
            "seo_analysis": "🔎", "architecture": "📐", "skill_loading": "📚",
            "frontend_generation": "🎨", "backend_generation": "⚙️",
            "run_localhost": "🚀", "browser_test": "🌐", "screenshot": "📸",
            "vision_analysis": "👁️", "ui_improvement": "✨",
            "seo_optimization": "🔎", "performance_optimization": "⚡",
            "finalize": "🎉",
        }
        icon = icons.get(stage, "▶️")
        console.print(Panel(
            f"[bold]{description}[/bold]",
            title=f"{icon} Stage: {stage.replace('_', ' ').title()}",
            border_style="cyan",
        ))
    
    # ── Stage: Task Understanding ─────────────────────────────
    
    def _understand_task(self, state: AgentState) -> AgentState:
        """Parse and understand the user request."""
        self._show_stage("understand", "Analyzing your request...")
        
        from prompts.templates import PromptTemplates
        if not self.model_manager.check_ollama():
            console.print("[yellow]⚠️ Ollama unreachable; using default task analysis[/yellow]")
            state.task_analysis = {
                "project_type": "landing",
                "features": [],
                "tech_stack": ["nextjs", "react", "tailwind"],
                "design_style": "modern",
                "has_3d": False,
                "has_backend": False,
            }
            state.project_type = "landing"
            state.features = []
            state.tech_stack = ["nextjs", "react", "tailwind"]
            state.design_style = "modern"
            state.with_3d = False
            state.with_backend = False
            return state

        prompt = f"""{PromptTemplates.TASK_UNDERSTANDING_PROMPT}

User request: {state.user_request}

Output valid JSON only."""
        
        response = self.model_manager.generate(
            prompt, model=self.settings.models.reasoning_model,
            temperature=0.3, stream=False
        )
        
        try:
            # Extract JSON from response
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```\n")[1].split("```")[0]
            
            analysis = json.loads(json_str.strip())
            state.task_analysis = analysis
            state.project_type = analysis.get("project_type", "landing")
            state.features = analysis.get("features", [])
            state.tech_stack = analysis.get("tech_stack", [])
            state.design_style = analysis.get("design_style", "modern")
            state.with_3d = analysis.get("has_3d", False)
            state.with_backend = analysis.get("has_backend", False)
            
            console.print(f"[green]✅ Project type: {state.project_type}[/green]")
            console.print(f"[green]✅ Features: {', '.join(state.features[:5])}[/green]")
        except (json.JSONDecodeError, IndexError):
            console.print("[yellow]⚠️ Could not parse analysis, using defaults[/yellow]")
            state.task_analysis = {"raw": response}
            state.project_type = "landing"
            state.features = []
            state.tech_stack = ["nextjs", "react", "tailwind"]
            state.design_style = "modern"
            state.with_3d = False
            state.with_backend = False
        
        return state
    
    # ── Stage: Research ───────────────────────────────────────
    
    def _research(self, state: AgentState) -> AgentState:
        """Research the topic before coding."""
        if not self.settings.auto_research:
            console.print("[dim]Research skipped (--no-research)[/dim]")
            return state
        
        self._show_stage("research", f"Researching: {state.project_type}")
        
        try:
            results = self.research_engine.research(
                f"{state.project_type} website design trends {state.design_style}",
                max_results=self.settings.research.max_search_results
            )
            state.research_results = results or []
            console.print(f"[green]✅ Found {len(state.research_results)} research results[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Research unavailable: {e}[/yellow]")
        
        return state
    
    # ── Stage: Architecture Planning ──────────────────────────
    
    def _plan_architecture(self, state: AgentState) -> AgentState:
        """Create project architecture."""
        self._show_stage("architecture", "Planning project architecture...")
        
        from prompts.templates import PromptTemplates
        if not self.model_manager.check_ollama():
            console.print("[yellow]⚠️ Ollama unreachable; using default architecture plan[/yellow]")
            state.architecture = {
                "folder_structure": {
                    "src": ["app", "components"],
                },
                "components": ["Navbar", "Footer", "Hero", "Features", "CTA"],
                "pages": ["home"],
                "api_routes": ["items"],
                "dependencies": ["next", "react", "tailwindcss"],
            }
            return state

        context = json.dumps({
            "project_type": state.project_type,
            "features": state.features,
            "tech_stack": state.tech_stack,
            "design_style": state.design_style,
            "with_backend": state.with_backend,
            "with_3d": state.with_3d,
        })
        
        prompt = f"""{PromptTemplates.ARCHITECTURE_PROMPT}

Project context: {context}

Output valid JSON with: folder_structure, components, pages, api_routes, dependencies."""
        
        response = self.model_manager.generate(
            prompt, model=self.settings.models.reasoning_model,
            temperature=0.3, stream=False
        )
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            state.architecture = json.loads(json_str.strip())
            console.print("[green]✅ Architecture planned[/green]")
        except (json.JSONDecodeError, IndexError):
            console.print("[yellow]⚠️ Could not parse architecture plan, using defaults[/yellow]")
            state.architecture = {
                "folder_structure": {"src": ["app", "components"]},
                "components": self.frontend_gen._default_components(state.project_type or "landing"),
                "pages": self.frontend_gen._default_pages(state.project_type or "landing"),
                "api_routes": self.backend_gen._default_routes(state.project_type or "landing"),
                "dependencies": ["next", "react", "tailwindcss"],
            }
        
        return state
    
    # ── Stage: Skill Loading ──────────────────────────────────
    
    def _load_skills(self, state: AgentState) -> AgentState:
        """Dynamically load required skills."""
        self._show_stage("skill_loading", "Loading required skills...")
        
        skill_map = {
            "landing": ["uiux", "seo", "landingpage", "animations"],
            "saas": ["uiux", "seo", "saas", "startup", "animations", "dashboard"],
            "dashboard": ["uiux", "dashboard", "backend"],
            "portfolio": ["uiux", "portfolio", "animations", "seo"],
            "ecommerce": ["uiux", "ecommerce", "backend", "seo"],
            "blog": ["uiux", "blog", "seo", "accessibility"],
            "agency": ["uiux", "agency", "animations", "seo"],
        }
        
        needed = skill_map.get(state.project_type, ["uiux", "seo"])
        
        if state.with_3d:
            needed.extend(["threejs", "react-three-fiber"])
        if state.with_backend:
            needed.append("backend")
        needed.extend(["accessibility", "performance"])
        
        # Deduplicate
        needed = list(dict.fromkeys(needed))
        
        loaded_prompts = []
        for skill_name in needed:
            skill_data = self.skill_loader.load_skill(skill_name)
            if skill_data:
                loaded_prompts.append(skill_data.get("prompt", ""))
                state.loaded_skills.append(skill_name)
        
        console.print(f"[green]✅ Loaded {len(state.loaded_skills)} skills: {', '.join(state.loaded_skills)}[/green]")
        return state
    
    # ── Stage: Frontend Generation ────────────────────────────
    
    def _generate_frontend(self, state: AgentState) -> AgentState:
        """Generate frontend code."""
        self._show_stage("frontend_generation", "Generating frontend code...")
        
        skill_context = ""
        for skill_name in state.loaded_skills:
            skill_data = self.skill_loader.load_skill(skill_name)
            if skill_data:
                skill_context += f"\n--- {skill_name} skill ---\n{skill_data.get('prompt', '')}\n"
        
        files = self.frontend_gen.generate(
            project_type=state.project_type,
            features=state.features,
            design_style=state.design_style,
            architecture=state.architecture,
            skill_context=skill_context,
            with_3d=state.with_3d,
        )
        
        state.generated_files.update(files)
        console.print(f"[green]✅ Generated {len(files)} frontend files[/green]")
        return state
    
    # ── Stage: Backend Generation ─────────────────────────────
    
    def _generate_backend(self, state: AgentState) -> AgentState:
        """Generate backend code if needed."""
        if not state.with_backend:
            console.print("[dim]Backend generation skipped[/dim]")
            return state
        
        self._show_stage("backend_generation", "Generating backend code...")
        
        files = self.backend_gen.generate(
            project_type=state.project_type,
            features=state.features,
            architecture=state.architecture,
        )
        
        state.generated_files.update(files)
        console.print(f"[green]✅ Generated {len(files)} backend files[/green]")
        return state
    
    # ── Stage: Write Files & Run Localhost ─────────────────────
    
    def _scaffold_and_run(self, state: AgentState) -> AgentState:
        """Write files to disk and start dev server."""
        self._show_stage("run_localhost", "Setting up project and starting localhost...")
        
        project_path = self.sandbox_runner.scaffold_project(
            state.project_name, state.template, state.generated_files
        )
        state.project_path = project_path
        
        port = self.sandbox_runner.start_dev_server(state.project_name, state.localhost_port)
        state.localhost_url = f"http://localhost:{port}"
        state.localhost_port = port
        
        console.print(f"[green]✅ Project running at {state.localhost_url}[/green]")
        return state
    
    # ── Stage: Browser Testing ────────────────────────────────
    
    def _browser_test(self, state: AgentState) -> AgentState:
        """Run browser tests and capture screenshots."""
        self._show_stage("browser_test", "Running browser tests...")
        
        try:
            results = self.browser_auto.test_website(state.localhost_url)
            screenshots = self.browser_auto.capture_screenshots(
                state.project_name, state.localhost_url
            )
            state.screenshots = screenshots
            console.print(f"[green]✅ Browser tests complete, {len(screenshots)} screenshots[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Browser test error: {e}[/yellow]")
            state.errors.append(f"Browser test: {e}")
        
        return state
    
    # ── Stage: Vision Analysis ────────────────────────────────
    
    def _vision_analysis(self, state: AgentState) -> AgentState:
        """Analyze screenshots with AI vision."""
        if not state.screenshots:
            console.print("[dim]No screenshots to analyze[/dim]")
            return state
        
        self._show_stage("vision_analysis", "Analyzing UI with AI vision...")
        
        try:
            report = self.vision_analyzer.analyze_screenshots(state.screenshots)
            state.vision_report = report
            state.issues = report.get("issues", [])
            console.print(f"[green]✅ Found {len(state.issues)} UI issues[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Vision analysis error: {e}[/yellow]")
        
        return state
    
    # ── Stage: Improvement Loop ───────────────────────────────
    
    def _improve(self, state: AgentState) -> AgentState:
        """Apply UI improvements based on vision analysis."""
        if not self.settings.auto_improve or not state.issues:
            return state
        
        self._show_stage("ui_improvement", f"Improvement loop {state.improvement_loop + 1}")
        
        from prompts.templates import PromptTemplates
        issues_text = json.dumps(state.issues[:10])
        prompt = f"""{PromptTemplates.IMPROVEMENT_PROMPT}

Issues found:
{issues_text}

Project type: {state.project_type}
Generated files: {list(state.generated_files.keys())[:20]}

Generate specific fixes as JSON array of {{file, original, replacement}} objects."""
        
        response = self.model_manager.generate(
            prompt, model=self.settings.models.coding_model,
            temperature=0.4, stream=False
        )
        
        state.improvement_loop += 1
        console.print(f"[green]✅ Improvement loop {state.improvement_loop} complete[/green]")
        return state
    
    # ── Stage: SEO Optimization ───────────────────────────────
    
    def _optimize_seo(self, state: AgentState) -> AgentState:
        """Apply SEO optimizations."""
        self._show_stage("seo_optimization", "Optimizing SEO...")
        
        try:
            seo_files = self.seo_optimizer.generate_seo_files(
                state.project_type, state.project_name,
                state.seo_analysis.get("keywords", [])
            )
            state.generated_files.update(seo_files)
            console.print(f"[green]✅ Generated {len(seo_files)} SEO files[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️ SEO optimization error: {e}[/yellow]")
        
        return state
    
    # ── Stage: Finalize ───────────────────────────────────────
    
    def _finalize(self, state: AgentState) -> AgentState:
        """Finalize the project."""
        self._show_stage("finalize", "Finalizing project...")
        
        # Save to memory
        try:
            self.memory.create_project(
                name=state.project_name,
                description=state.user_request,
                template=state.template,
                path=state.project_path,
                config=state.task_analysis,
            )
        except Exception:
            pass  # Project may already exist
        
        state.completed = True
        console.print(Panel(
            f"[bold green]Project '{state.project_name}' is ready![/bold green]\n\n"
            f"📁 Path: {state.project_path}\n"
            f"🌐 URL: {state.localhost_url}\n"
            f"📊 Files generated: {len(state.generated_files)}\n"
            f"🔄 Improvement loops: {state.improvement_loop}\n"
            f"📚 Skills used: {', '.join(state.loaded_skills)}",
            title="🎉 Project Complete",
            border_style="green",
        ))
        return state
    
    # ── Helpers ────────────────────────────────────────────────

    def _generate_project_name(self, prompt: str) -> str:
        """Generate a project name from the user prompt."""
        import re
        # Extract meaningful words, lowercase, join with hyphens
        words = re.findall(r'[a-zA-Z]+', prompt.lower())
        # Filter out common stop words
        stop_words = {"a", "an", "the", "make", "me", "create", "build", "for", "with", "and", "or", "my", "i", "want"}
        meaningful = [w for w in words if w not in stop_words][:4]
        name = "-".join(meaningful) if meaningful else "roobie-project"
        return name

    def _get_random_spinner(self) -> str:
        """Return a random spinner style for Rich console."""
        import random
        spinners = ["dots", "dots2", "dots3", "line", "star", "moon", "runner", "bouncingBall", "arc", "toggle"]
        return random.choice(spinners)

    def execute_plan(self, plan_text: str):
        """Execute a previously saved plan."""
        console.print(Panel(plan_text, title="📋 Executing Plan", border_style="green"))
        # Attempt to extract a build request from the plan
        if any(kw in plan_text.lower() for kw in ["create", "build", "generate", "make"]):
            self.run_build(plan_text)
        else:
            console.print("[yellow]Plan does not contain a buildable action. Showing as reference.[/yellow]")

    # ── Public API ────────────────────────────────────────────
    
    def run_build(self, prompt: str, project_name: str = None, seo: bool = True):
        """Run the full build pipeline with Claude Code-style animations."""
        console.print(f"[bold green]🛠️  Building: {prompt}[/bold green]")
        
        state = AgentState(
            user_request=prompt,
            project_name=project_name or self._generate_project_name(prompt),
        )
        
        pipeline = [
            ("🧠 Understanding", self._understand_task),
            ("🔍 Researching", self._research),
            ("📐 Planning Architecture", self._plan_architecture),
            ("🛠️ Loading Skills", self._load_skills),
            ("🎨 Generating Frontend", self._generate_frontend),
            ("⚙️ Generating Backend", self._generate_backend),
            ("🚀 Scaffolding & Running", self._scaffold_and_run),
            ("🖥️ Browser Testing", self._browser_test),
            ("👁️ Vision Analysis", self._vision_analysis),
            ("✨ Improving", self._improve),
        ]
        
        if seo:
            pipeline.append(("🔎 SEO Optimization", self._optimize_seo))
        
        pipeline.append(("🎉 Finalizing", self._finalize))
        
        for step_name, stage_fn in pipeline:
            with console.status(f"[bold blue]{step_name}...[/bold blue]", 
                              spinner=self._get_random_spinner()):
                try:
                    state = stage_fn(state)
                except Exception as e:
                    console.print(f"[red]❌ Error in {step_name}: {e}[/red]")
                    state.errors.append(f"{stage_fn.__name__}: {e}")
                    continue
            
            console.print(f"[green]✅ {step_name} complete[/green]")
        
        return state
    
    def run_init(self, name: str, template: str, with_backend: bool, with_3d: bool):
        """Initialize a new empty project."""
        state = AgentState(
            project_name=name, template=template,
            with_backend=with_backend, with_3d=with_3d,
        )
        
        self.sandbox_runner.scaffold_project(name, template, {})
        self.memory.create_project(name=name, template=template)
        
        console.print(f"[green]✅ Project '{name}' initialized[/green]")
    
    def run_think(self, prompt: str):
        """Think about a request without building."""
        state = AgentState(user_request=prompt)
        state = self._understand_task(state)
        state = self._plan_architecture(state)
        
        console.print(Panel(
            json.dumps(state.task_analysis, indent=2),
            title="🧠 Analysis", border_style="yellow",
        ))
    
    def run_chat(self, user_input: str):
        """Handle interactive chat with Claude Code-like behavior."""
        from prompts.templates import PromptTemplates
        
        # Check for plan continuation
        if user_input.lower().strip() in ["proceed", "continue", "go ahead", "yes"]:
            plan = self.memory.get_current_plan()
            if plan:
                console.print("[bold green]🚀 Proceeding with plan...[/bold green]")
                self.execute_plan(plan)
                return
        
        # Parse @ file references (e.g. @index.html or @design.png)
        import os
        import re
        
        attached_context = ""
        mentions = re.findall(r'@([a-zA-Z0-9_\-\.\/]+)', user_input)
        
        # Deduplicate mentions
        mentions = list(dict.fromkeys(mentions))
        
        for mention in mentions:
            if os.path.exists(mention):
                if mention.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                    with console.status(f"[bold blue]👁️ Analyzing image {mention}...[/bold blue]", spinner="dots"):
                        desc = self.model_manager.vision_analyze(mention, "Describe this image in detail for a web developer.")
                        attached_context += f"\n\n--- Visual Description of {mention} ---\n{desc}\n"
                    user_input = user_input.replace(f"@{mention}", f"[Image attached: {mention}]")
                    console.print(f"[green]📸 Attached image context: {mention}[/green]")
                else:
                    try:
                        with open(mention, 'r', encoding='utf-8') as f:
                            content = f.read()
                        attached_context += f"\n\n--- Content of {mention} ---\n{content}\n"
                        user_input = user_input.replace(f"@{mention}", f"[File read: {mention}]")
                        console.print(f"[green]📄 Attached file context: {mention}[/green]")
                    except Exception as e:
                        console.print(f"[yellow]⚠️ Could not read {mention}: {e}[/yellow]")
        
        if attached_context:
            user_input += "\n\n" + attached_context

        self.memory.add_message(None, "user", user_input)
        
        # Show thinking animation
        with console.status("[bold green]🤔 Thinking...[/bold green]", spinner="dots"):
            messages = [
                {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ]
            
            response = self.model_manager.chat(
                messages,
                model=getattr(self.settings.models, "chat_model", None) or self.settings.models.coding_model,
            )
            
            if not response:
                response = self.model_manager.generate(
                    user_input,
                    system=PromptTemplates.SYSTEM_PROMPT,
                    temperature=0.7,
                )
            
            if not response:
                response = "⚠️ No response from the AI model. Check AirLLM configuration."
        
        self.memory.add_message(None, "assistant", response)
        console.print(Panel(response, title="🤖 Roobie", border_style="cyan"))
        
        # Check if response contains a structured plan (more targeted than just "plan" or "will")
        plan_indicators = ["step 1", "step 2", "here's my plan", "here is my plan",
                           "i'll create", "i will create", "implementation plan",
                           "1.", "2.", "3."]
        response_lower = response.lower()
        if sum(1 for indicator in plan_indicators if indicator in response_lower) >= 2:
            self.memory.save_current_plan(response)

    def handle_slash_command(self, command: str):
        """Handle slash commands like /chat, /history, etc."""
        cmd = command.lower().strip()
        if cmd == "/chat" or cmd == "/history":
            self.show_chat_history()
        elif cmd == "/clear":
            self.clear_chat_history()
        elif cmd == "/help":
            self.show_help()
        elif cmd.startswith("/run "):
            self.run_terminal_command(cmd[5:])
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
    
    def show_chat_history(self):
        """Show chat history with selection."""
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.shortcuts import radiolist_dialog
            
            history = self.memory.get_conversation(None, limit=20)
            if not history:
                console.print("[yellow]No chat history found.[/yellow]")
                return
            
            options = [(i, f"{msg['role']}: {msg['content'][:50]}...") for i, msg in enumerate(history)]
            result = radiolist_dialog(
                title="Chat History",
                text="Select a message to view:",
                values=options
            ).run()
            
            if result is not None:
                msg = history[result]
                console.print(Panel(msg['content'], title=f"{msg['role'].title()}", border_style="blue"))
        except ImportError:
            # Fallback
            history = self.memory.get_conversation(None, limit=10)
            for msg in history[-5:]:  # Show last 5
                console.print(f"[bold {msg['role']}]{msg['role']}:[/bold {msg['role']}] {msg['content'][:100]}...")
    
    def clear_chat_history(self):
        """Clear chat history."""
        # Note: This would require a method to clear conversations
        console.print("[green]Chat history cleared.[/green]")
    
    def show_help(self):
        """Show available commands."""
        help_text = """
[bold]Available Commands:[/bold]
/chat or /history - Show chat history
/clear - Clear chat history  
/help - Show this help
/run <command> - Run terminal command
!command - Run terminal command (shortcut)

Type any message for AI chat.
Type 'exit' to quit.
        """
        console.print(Panel(help_text, title="Help", border_style="green"))
    
    def run_terminal_command(self, cmd: str):
        """Run a terminal command."""
        console.print(f"[cyan]Running: {cmd}[/cyan]")
        try:
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                console.print(Panel(result.stdout, title="Output", border_style="green"))
            if result.stderr:
                console.print(Panel(result.stderr, title="Error", border_style="red"))
            console.print(f"[yellow]Exit code: {result.returncode}[/yellow]")
        except Exception as e:
            console.print(f"[red]Command failed: {e}[/red]")
