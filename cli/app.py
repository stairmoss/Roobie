"""
Roobie CLI — Autonomous AI Coding Assistant
Interactive terminal-based agentic coding tool.
Like Claude Code, but runs locally with AirLLM (disk-offloaded, 4GB RAM).
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.rule import Rule
from rich import print as rprint
from typing import Optional
import sys
import os 
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = typer.Typer(
    name="roobie",
    help="🤖 Roobie — Autonomous Local-First AI Coding Assistant",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()

BANNER = """[bold cyan]
 ██████╗  ██████╗  ██████╗ ██████╗ ██╗███████╗
 ██╔══██╗██╔═══██╗██╔═══██╗██╔══██╗██║██╔════╝
 ██████╔╝██║   ██║██║   ██║██████╔╝██║█████╗  
 ██╔══██╗██║   ██║██║   ██║██╔══██╗██║██╔══╝  
 ██║  ██║╚██████╔╝╚██████╔╝██████╔╝██║███████╗
 ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝╚══════╝
[/bold cyan]
[dim]Autonomous AI Coding Agent • Local-first • AirLLM-powered • Works offline[/dim]"""


def show_banner():
    """Display the Roobie ASCII banner."""
    console.print(BANNER)


# ── Tool Display Icons ──────────────────────────────────
TOOL_STYLES = {
    "think":          ("🧠", "yellow",  "Thinking"),
    "create_file":    ("📄", "green",   "Create File"),
    "edit_file":      ("✏️",  "blue",    "Edit File"),
    "read_file":      ("📖", "cyan",    "Read File"),
    "delete_file":    ("🗑️",  "red",     "Delete File"),
    "list_directory": ("📂", "white",   "List Directory"),
    "create_folder":  ("📁", "green",   "Create Folder"),
    "run_command":    ("💻", "magenta", "Run Command"),
    "web_search":     ("🔍", "yellow",  "Web Search"),
}


def display_tool_call(tool_name: str, params: dict):
    """Display a tool call in the terminal with Rich formatting."""
    icon, color, label = TOOL_STYLES.get(tool_name, ("🔧", "white", tool_name))

    # Build a short summary of what the tool is doing
    summary = ""
    if tool_name == "create_file":
        summary = params.get("path", "")
    elif tool_name == "edit_file":
        summary = params.get("path", "")
    elif tool_name == "read_file":
        summary = params.get("path", "")
    elif tool_name == "delete_file":
        summary = params.get("path", "")
    elif tool_name == "run_command":
        summary = params.get("command", "")
    elif tool_name == "web_search":
        summary = params.get("query", "")
    elif tool_name == "think":
        thought = params.get("thought", "")
        summary = thought[:120] + "..." if len(thought) > 120 else thought
    elif tool_name in ("create_folder", "list_directory"):
        summary = params.get("path", "")

    header = f"{icon} {label}"
    if summary:
        header += f" → [dim]{summary}[/dim]"

    console.print(f"  [{color}]{header}[/{color}]")


def display_tool_result(tool_name: str, result: dict):
    """Display a tool result in the terminal."""
    icon, color, label = TOOL_STYLES.get(tool_name, ("🔧", "white", tool_name))
    success = result.get("success", False)
    status = "[green]✓[/green]" if success else "[red]✗[/red]"

    if tool_name == "think":
        # Show thinking in a panel
        thought = result.get("thought", "")
        if thought:
            console.print(Panel(
                thought,
                title=f"🧠 Thinking (step {result.get('step', '?')})",
                border_style="yellow",
                padding=(0, 1),
            ))
        return

    if tool_name == "run_command":
        stdout = result.get("stdout", "").strip()
        stderr = result.get("stderr", "").strip()
        exit_code = result.get("exit_code", -1)
        status_text = f"exit code {exit_code}"

        if stdout:
            # Limit output display
            lines = stdout.split("\n")
            if len(lines) > 30:
                display = "\n".join(lines[:15] + ["  ...", f"  ({len(lines)} total lines)", "  ..."] + lines[-10:])
            else:
                display = stdout
            console.print(Panel(
                display,
                title=f"💻 Output ({status_text})",
                border_style="green" if exit_code == 0 else "red",
                padding=(0, 1),
            ))
        if stderr:
            console.print(f"    [red]{stderr[:500]}[/red]")
        return

    if tool_name == "read_file":
        if success:
            content = result.get("content", "")
            path = result.get("path", "")
            lines_count = result.get("lines", 0)
            size = result.get("size", 0)
            console.print(f"    {status} Read {path} ({lines_count} lines, {size} bytes)")
            # Don't show full content — it's for the LLM, not the user
        else:
            console.print(f"    {status} [red]{result.get('error', '')}[/red]")
        return

    if tool_name == "list_directory":
        if success:
            entries = result.get("entries", [])
            if entries:
                for e in entries[:20]:
                    icon_e = "📁" if e["type"] == "directory" else "📄"
                    console.print(f"    {icon_e} {e['name']}")
                if len(entries) > 20:
                    console.print(f"    [dim]... and {len(entries) - 20} more[/dim]")
            else:
                console.print("    [dim](empty directory)[/dim]")
        else:
            console.print(f"    {status} [red]{result.get('error', '')}[/red]")
        return

    if tool_name == "web_search":
        if success:
            results = result.get("results", [])
            for i, r in enumerate(results[:5], 1):
                console.print(f"    [cyan]{i}.[/cyan] [bold]{r.get('title', '')}[/bold]")
                console.print(f"       [dim]{r.get('url', '')}[/dim]")
                snippet = r.get("snippet", "")
                if snippet:
                    console.print(f"       {snippet[:100]}")
        else:
            console.print(f"    {status} [red]{result.get('error', 'No results')}[/red]")
        return

    # Default display for create_file, edit_file, delete_file, create_folder
    msg = result.get("message", result.get("error", ""))
    console.print(f"    {status} {msg}")


def display_assistant_text(text: str):
    """Display the assistant's text response."""
    if not text.strip():
        return
    # Try to render as markdown
    try:
        console.print(Markdown(text))
    except Exception:
        console.print(text)


# ══════════════════════════════════════════════════════
# Interactive Chat — The Main Experience
# ══════════════════════════════════════════════════════

@app.command()
def chat(
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="AirLLM model to use"),
):
    """💬 Start interactive agentic chat (the main Roobie experience)."""
    show_banner()

    # Resolve workspace
    if workspace:
        if os.path.isfile(workspace):
            console.print(f"[red]⚠️ '{workspace}' is a file, not a directory. please specify a directory path.[/red]")
            raise typer.Exit(code=1)
        elif not os.path.isdir(workspace):
            console.print(f"[red]⚠️ the workspace directory '{workspace}' does not exist. please verify the path.[/red]")
            raise typer.Exit(code=1)
    ws = workspace or os.getcwd()
    ws = os.path.abspath(ws)
    mdl = model or os.environ.get("ROOBIE_MODEL", "deepseek-ai/deepseek-coder-1.3b-instruct")

    console.print(f"\n  📁 Workspace: [cyan]{ws}[/cyan]")
    console.print(f"  🧠 Model:     [cyan]{mdl}[/cyan]")

    # Import chat engine
    from agent.chat_engine import ChatEngine

    engine = ChatEngine(ws, mdl)

    import atexit
    atexit.register(engine.executor.terminal_tools.cleanup)

    console.print(f"  ✅ AirLLM ready (will load on first message)\n")

    console.print(Rule("Chat", style="cyan"))
    console.print("[dim]  Type your message and press Enter. Commands: /help /clear /tree /model /exit[/dim]\n")

    # Set up event callback for tool display
    def event_callback(event_type: str, data: dict):
        if event_type == "tool_start" or event_type == "tool_call":
            display_tool_call(data.get("tool", data.get("name", "")), data.get("params", {}))
        elif event_type == "tool_end" or event_type == "tool_result":
            display_tool_result(data.get("tool", data.get("name", "")), data.get("result", {}))
        elif event_type == "thinking_start":
            pass  # We show a spinner in the main loop
        elif event_type == "error":
            console.print(f"  [red]⚠️ {data.get('message', '')}[/red]")

    engine.set_event_callback(event_callback)

    # Interactive loop
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.styles import Style as PTStyle

        history_dir = os.path.expanduser("~/.roobie")
        os.makedirs(history_dir, exist_ok=True)
        session = PromptSession(
            history=FileHistory(os.path.join(history_dir, "chat_history")),
            auto_suggest=AutoSuggestFromHistory(),
            multiline=False,
        )

        pt_style = PTStyle.from_dict({
            'prompt': 'bold ansigreen',
        })

        bindings = KeyBindings()

        @bindings.add('c-c')
        def _(event):
            console.print("\n[bold yellow]Interrupted. Goodbye! 👋[/bold yellow]")
            event.app.exit()
            raise SystemExit(0)

        while True:
            try:
                user_input = session.prompt(
                    "roobie> ",
                    key_bindings=bindings,
                    style=pt_style,
                ).strip()

                if not user_input:
                    continue

                # Handle slash commands
                if user_input.startswith("/"):
                    handled = handle_slash(user_input, engine)
                    if handled == "exit":
                        break
                    continue

                # Process through agentic loop
                console.print()
                with console.status("[bold cyan]Roobie is thinking...", spinner="dots"):
                    response = engine.chat(user_input)

                # Display the final response
                if response:
                    text = _clean_tool_blocks(response)
                    if text.strip():
                        console.print()
                        console.print(Panel(
                            Markdown(text),
                            title="🤖 Roobie",
                            border_style="cyan",
                            padding=(1, 2),
                        ))
                console.print()

            except KeyboardInterrupt:
                console.print("\n[bold yellow]Interrupted. Goodbye! 👋[/bold yellow]")
                break
            except EOFError:
                break

    except ImportError:
        # Fallback if prompt_toolkit not installed
        console.print("[yellow]  (Install prompt_toolkit for better input: pip install prompt_toolkit)[/yellow]\n")
        while True:
            try:
                user_input = console.input("[bold green]roobie>[/bold green] ").strip()
                if not user_input:
                    continue
                if user_input.startswith("/"):
                    handled = handle_slash(user_input, engine)
                    if handled == "exit":
                        break
                    continue

                console.print()
                with console.status("[bold cyan]Roobie is thinking...", spinner="dots"):
                    response = engine.chat(user_input)

                if response:
                    text = _clean_tool_blocks(response)
                    if text.strip():
                        console.print()
                        console.print(Panel(
                            Markdown(text),
                            title="🤖 Roobie",
                            border_style="cyan",
                            padding=(1, 2),
                        ))
                console.print()

            except KeyboardInterrupt:
                console.print("\n[bold yellow]Interrupted. Goodbye! 👋[/bold yellow]")
                break


def _clean_tool_blocks(text: str) -> str:
    """Remove tool call blocks and patterns from display text to make it user friendly."""
    import re
    # Remove explicit tool calls
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL)
    # Remove json code blocks containing name
    text = re.sub(r'```(?:json)?\s*\{[^`]*?"name"\s*:\s*"[^`]*?\}\s*```', '', text, flags=re.DOTALL)
    # Remove bare json objects matching tool names
    tool_names = "think|create_file|edit_file|read_file|delete_file|list_directory|create_folder|run_command|web_search"
    text = re.sub(r'\{\s*"name"\s*:\s*"(?:' + tool_names + r')".*?\}\s*\}', '', text, flags=re.DOTALL)
    return text.strip()


def handle_slash(cmd: str, engine) -> Optional[str]:
    """Handle slash commands. Returns 'exit' to quit."""
    parts = cmd.strip().split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if command in ("/exit", "/quit", "/q"):
        console.print("[bold yellow]Goodbye! 👋[/bold yellow]")
        return "exit"

    elif command == "/help":
        table = Table(title="Roobie Commands", show_header=True, header_style="bold cyan")
        table.add_column("Command", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Description")
        
        table.add_row("/help", "General", "Show this help menu")
        table.add_row("/version", "General", "Show the current version of Roobie")
        table.add_row("/exit", "General", "Exit Roobie")
        
        table.add_row("/clear", "Chat & Files", "Clear conversation history")
        table.add_row("/tree", "Chat & Files", "Show workspace file tree")
        table.add_row("/read [path]", "Chat & Files", "Read a file from workspace")
        
        table.add_row("/run [command]", "Action", "Run a shell command directly")
        table.add_row("/search [query]", "Action", "Search the web")
        
        table.add_row("/status", "System", "Show system status")
        table.add_row("/env", "System", "Show environment configuration settings")
        table.add_row("/workspace [path]", "System", "Show or change workspace")
        table.add_row("/model [name]", "System", "Show or change current model")
        table.add_row("/models", "System", "List available Ollama models")
        
        console.print(table)

    elif command == "/version":
        console.print("[bold cyan]Roobie Version:[/bold cyan] [green]1.0.0[/green]")

    elif command == "/env":
        from config.settings import get_settings
        settings = get_settings()
        table = Table(title="Roobie Settings & Configuration", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="green")
        table.add_column("Value", style="cyan")
        
        table.add_row("Ollama Host", str(getattr(settings.models, "ollama_host", "N/A")))
        table.add_row("Coding Model", str(getattr(settings.models, "coding_model", "N/A")))
        table.add_row("Reasoning Model", str(getattr(settings.models, "reasoning_model", "N/A")))
        table.add_row("Vision Model", str(getattr(settings.models, "vision_model", "N/A")))
        table.add_row("Context Length", str(getattr(settings.models, "context_length", "N/A")))
        table.add_row("Max Output Tokens", str(getattr(settings.models, "max_tokens", "N/A")))
        table.add_row("Temperature", str(getattr(settings.models, "temperature", "N/A")))
        table.add_row("AirLLM Enabled", str(getattr(settings.models, "use_airllm", "N/A")))
        table.add_row("Projects Directory", str(getattr(settings.sandbox, "projects_dir", "N/A")))
        
        console.print(table)

    elif command == "/clear":
        engine.clear_history()
        console.print("  [green]✓ Conversation history cleared[/green]")

    elif command == "/tree":
        tree = engine.get_file_tree()
        if tree.get("success"):
            _print_tree(tree.get("tree", []), 0)
        else:
            console.print("  [dim](empty workspace)[/dim]")

    elif command == "/model":
        if arg:
            engine.model = arg
            console.print(f"  [green]✓ Model changed to: {arg} (AirLLM)[/green]")
        else:
            console.print(f"  Current model: [cyan]{engine.model}[/cyan] (AirLLM)")

    elif command == "/models":
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan")
        table.add_column("Backend", style="yellow")
        table.add_column("Size", style="dim")
        table.add_column("Best For")
        # AirLLM models (recommended)
        airllm_models = [
            ("deepseek-ai/deepseek-coder-1.3b-instruct", "~800MB", "Fast coding"),
            ("Qwen/Qwen2.5-Coder-3B-Instruct",           "~2GB",   "Balanced coding"),
            ("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "~1GB",  "Reasoning"),
        ]
        for name, size, purpose in airllm_models:
            table.add_row(name, "[green]AirLLM[/green]", size, purpose)
        console.print(table)
        console.print("[dim]Use /model <name> to switch. AirLLM models download on first use.[/dim]")

    elif command == "/run":
        if not arg:
            console.print("  [yellow]Usage: /run <command>[/yellow]")
        else:
            from tools.terminal_tools import TerminalTools
            tt = TerminalTools(engine.workspace_dir)
            result = tt.run_command(arg)
            if result.get("stdout"):
                console.print(Panel(result["stdout"].rstrip(), title=f"$ {arg}", border_style="green"))
            if result.get("stderr"):
                console.print(f"  [red]{result['stderr'].rstrip()}[/red]")
            if result.get("error"):
                console.print(f"  [red]{result['error']}[/red]")

    elif command == "/read":
        if not arg:
            console.print("  [yellow]Usage: /read <filepath>[/yellow]")
        else:
            from tools.file_tools import FileTools
            ft = FileTools(engine.workspace_dir)
            result = ft.read_file(arg)
            if result.get("success"):
                path = result.get("path", arg)
                ext = path.rsplit(".", 1)[-1] if "." in path else "text"
                try:
                    console.print(Syntax(
                        result["content"],
                        ext,
                        theme="monokai",
                        line_numbers=True,
                        word_wrap=True,
                    ))
                except Exception:
                    console.print(result["content"])
            else:
                console.print(f"  [red]{result.get('error', 'File not found')}[/red]")

    elif command == "/search":
        if not arg:
            console.print("  [yellow]Usage: /search <query>[/yellow]")
        else:
            from tools.search_tools import SearchTools
            st = SearchTools()
            with console.status("[bold yellow]Searching...", spinner="dots"):
                result = st.web_search(arg)
            if result.get("success"):
                for i, r in enumerate(result.get("results", []), 1):
                    console.print(f"  [cyan]{i}.[/cyan] [bold]{r.get('title', '')}[/bold]")
                    console.print(f"     [dim]{r.get('url', '')}[/dim]")
                    snippet = r.get("snippet", "")
                    if snippet:
                        console.print(f"     {snippet[:120]}")
                    console.print()
            else:
                console.print(f"  [red]{result.get('error', 'Search failed')}[/red]")

    elif command == "/status":
        _show_status(engine)

    elif command == "/workspace":
        if arg:
            new_ws = os.path.abspath(arg)
            if os.path.isfile(new_ws):
                console.print(f"  [red]⚠️ '{arg}' is a file. Please specify a directory path for the workspace.[/red]")
            else:
                os.makedirs(new_ws, exist_ok=True)
                engine.workspace_dir = new_ws
                engine.executor.file_tools.workspace = __import__("pathlib").Path(new_ws).resolve()
                engine.executor.terminal_tools.workspace = __import__("pathlib").Path(new_ws).resolve()
                console.print(f"  [green]✓ Workspace changed to: {new_ws}[/green]")
        else:
            console.print(f"  Workspace: [cyan]{engine.workspace_dir}[/cyan]")

    else:
        console.print(f"  [yellow]Unknown command: {command}. Type /help for commands.[/yellow]")

    return None


def _print_tree(nodes, depth):
    """Print a file tree recursively."""
    for node in nodes:
        indent = "  " + "  │  " * depth
        icon = "📁" if node["type"] == "directory" else _file_icon(node["name"])
        name = node["name"]
        if node["type"] == "directory":
            console.print(f"{indent}{icon} [bold]{name}/[/bold]")
            children = node.get("children", [])
            if isinstance(children, list):
                _print_tree(children, depth + 1)
        else:
            size = node.get("size", 0)
            size_str = _format_size(size)
            console.print(f"{indent}{icon} {name} [dim]({size_str})[/dim]")


def _file_icon(name):
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    icons = {
        "py": "🐍", "js": "📜", "ts": "📘", "jsx": "⚛️", "tsx": "⚛️",
        "html": "🌐", "css": "🎨", "json": "📋", "md": "📝",
        "txt": "📃", "sh": "🐚", "yml": "⚙️", "yaml": "⚙️",
        "env": "🔐", "gitignore": "🔒", "svg": "🖼️", "png": "🖼️",
    }
    return icons.get(ext, "📄")


def _format_size(size):
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f}KB"
    else:
        return f"{size/(1024*1024):.1f}MB"


def _show_status(engine):
    """Display system status."""
    import shutil
    table = Table(title="System Status", show_header=True, header_style="bold cyan")
    table.add_column("Component", style="white")
    table.add_column("Status")

    table.add_row("Roobie Version", "[green]1.0.0[/green]")
    table.add_row("Workspace", f"[cyan]{engine.workspace_dir}[/cyan]")

    # Check environment variable overrides
    env_model = os.environ.get("ROOBIE_MODEL")
    table.add_row("Env Overridden Model", f"[cyan]{env_model}[/cyan]" if env_model else "[dim]Not Set[/dim]")
    env_ws = os.environ.get("ROOBIE_WORKSPACE")
    table.add_row("Env Overridden Workspace", f"[cyan]{env_ws}[/cyan]" if env_ws else "[dim]Not Set[/dim]")

    # Count files in workspace
    try:
        total_files = 0
        if engine.workspace_dir and os.path.exists(engine.workspace_dir) and os.path.isdir(engine.workspace_dir):
            for root, dirs, files in os.walk(engine.workspace_dir):
                dirs[:] = [d for d in dirs if d not in (".git", ".venv", "venv", "node_modules", "__pycache__", ".next")]
                total_files += len(files)
        table.add_row("Workspace Files", f"[cyan]{total_files}[/cyan]")
    except Exception:
        table.add_row("Workspace Files", "[yellow]Unavailable[/yellow]")

    table.add_row("Model", f"[cyan]{engine.model}[/cyan]")

    # AI backend status
    table.add_row("AI Backend", "[green]AirLLM (disk-offloaded)[/green]")
    loaded = hasattr(engine, "_airllm_model")
    table.add_row("Model State", "[green]✅ Loaded[/green]" if loaded else "[yellow]⏳ Will load on first message[/yellow]")

    # RAM
    try:
        import psutil
        mem = psutil.virtual_memory()
        ram_gb = mem.total / (1024**3)
        table.add_row("RAM", f"{ram_gb:.1f} GB ({mem.percent}% used)")
    except ImportError:
        pass

    # Check Playwright package
    try:
        import playwright
        playwright_status = "[green]✅ Installed[/green]"
    except ImportError:
        playwright_status = "[yellow]⚠️ Missing (run: pip install playwright)[/yellow]"
    table.add_row("Playwright SDK", playwright_status)

    # Check sqlite3
    try:
        import sqlite3
        sqlite_status = "[green]✅ Available[/green]"
    except ImportError:
        sqlite_status = "[red]❌ Missing[/red]"
    table.add_row("SQLite3 Database", sqlite_status)

    # Check git command
    git_status = "[green]✅ Available[/green]" if shutil.which("git") else "[yellow]⚠️ Missing[/yellow]"
    table.add_row("Git CLI", git_status)

    # Check docker command
    docker_status = "[green]✅ Available[/green]" if shutil.which("docker") else "[yellow]⚠️ Not Available (Optional)[/yellow]"
    table.add_row("Docker CLI", docker_status)

    table.add_row("Node.js",  "[green]✅[/green]" if shutil.which("node")    else "[red]❌[/red]")
    table.add_row("Python",   f"[green]✅ {sys.version.split()[0]}[/green]")
    table.add_row("Chat History", f"{len(engine.conversation)} messages")

    console.print(table)


# ══════════════════════════════════════════════════════
# Subcommands — One-Shot Operations
# ══════════════════════════════════════════════════════

@app.command()
def run(
    prompt: str = typer.Argument(..., help="What to do"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="AirLLM model"),
):
    """🚀 Run a one-shot task (non-interactive). E.g.: roobie run 'Create a landing page'"""
    if workspace:
        if os.path.isfile(workspace):
            console.print(f"[red]⚠️ '{workspace}' is a file, not a directory. please specify a directory path.[/red]")
            raise typer.Exit(code=1)
        elif not os.path.isdir(workspace):
            console.print(f"[red]⚠️ the workspace directory '{workspace}' does not exist. please verify the path.[/red]")
            raise typer.Exit(code=1)
    ws = workspace or os.getcwd()
    ws = os.path.abspath(ws)
    mdl = model or os.environ.get("ROOBIE_MODEL", "deepseek-ai/deepseek-coder-6.7b-instruct")

    console.print(f"\n  📁 [cyan]{ws}[/cyan]  🧠 [cyan]{mdl}[/cyan]\n")

    from agent.chat_engine import ChatEngine
    engine = ChatEngine(ws, mdl)

    def event_callback(event_type, data):
        if event_type in ("tool_start", "tool_call"):
            display_tool_call(data.get("tool", data.get("name", "")), data.get("params", {}))
        elif event_type in ("tool_end", "tool_result"):
            display_tool_result(data.get("tool", data.get("name", "")), data.get("result", {}))

    engine.set_event_callback(event_callback)

    with console.status("[bold cyan]Roobie is working...", spinner="dots"):
        response = engine.chat(prompt)

    if response:
        text = _clean_tool_blocks(response)
        if text.strip():
            console.print(Panel(Markdown(text), title="🤖 Roobie", border_style="cyan", padding=(1, 2)))


@app.command()
def status():
    """📊 Show system status."""
    show_banner()
    ws = os.environ.get("ROOBIE_WORKSPACE", os.getcwd())
    mdl = os.environ.get("ROOBIE_MODEL", "deepseek-ai/deepseek-coder-1.3b-instruct")

    from agent.chat_engine import ChatEngine
    engine = ChatEngine(ws, mdl)
    _show_status(engine)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
):
    """🔍 Search the web (no API key needed)."""
    from tools.search_tools import SearchTools
    st = SearchTools()
    with console.status("[bold yellow]Searching...", spinner="dots"):
        result = st.web_search(query)
    if result.get("success"):
        for i, r in enumerate(result.get("results", []), 1):
            console.print(f"  [cyan]{i}.[/cyan] [bold]{r.get('title', '')}[/bold]")
            console.print(f"     [dim]{r.get('url', '')}[/dim]")
            snippet = r.get("snippet", "")
            if snippet:
                console.print(f"     {snippet[:150]}")
            console.print()
    else:
        console.print(f"  [red]{result.get('error', 'Search failed')}[/red]")


@app.command()
def version():
    """🏷️ Show the current version of Roobie."""
    console.print("[bold cyan]Roobie Version:[/bold cyan] [green]1.0.0[/green]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """🤖 Roobie — Autonomous AI Coding Assistant. Run 'roobie chat' to start."""
    if ctx.invoked_subcommand is None:
        # Default to chat mode — pass explicit None so Typer resolves defaults properly
        chat(workspace=None, model=None)


if __name__ == "__main__":
    app()
