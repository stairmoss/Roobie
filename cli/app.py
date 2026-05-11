"""
Roobie CLI — Autonomous AI Coding Assistant
Interactive terminal-based agentic coding tool.
Like Claude Code, but runs locally with Ollama.
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
[dim]Autonomous AI Coding Assistant • Local-first • Ollama-powered[/dim]"""


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
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Ollama model to use"),
    ollama_host: Optional[str] = typer.Option(None, "--ollama", help="Ollama host URL"),
):
    """💬 Start interactive agentic chat (the main Roobie experience)."""
    show_banner()

    # Resolve workspace
    ws = workspace or os.getcwd()
    ws = os.path.abspath(ws)
    mdl = model or os.environ.get("ROOBIE_MODEL", "deepseek-ai/deepseek-coder-6.7b-instruct")
    host = ollama_host or os.environ.get("ROOBIE_OLLAMA_HOST", "http://localhost:11434")

    console.print(f"\n  📁 Workspace: [cyan]{ws}[/cyan]")
    console.print(f"  🧠 Model:     [cyan]{mdl}[/cyan]")
    console.print(f"  🔗 Ollama:    [cyan]{host}[/cyan]")

    # Import chat engine
    from agent.chat_engine import ChatEngine

    engine = ChatEngine(ws, host, mdl)

    # Check Ollama connection
    if engine.check_model():
        console.print(f"  ✅ Ollama connected\n")
    else:
        console.print(f"  [red]❌ Ollama not running. Start with: ollama serve[/red]\n")

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
    """Remove <tool_call> blocks from display text."""
    import re
    return re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL).strip()


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
        table.add_column("Description")
        table.add_row("/help", "Show this help")
        table.add_row("/clear", "Clear conversation history")
        table.add_row("/tree", "Show workspace file tree")
        table.add_row("/model [name]", "Show or change current model")
        table.add_row("/models", "List available Ollama models")
        table.add_row("/run [command]", "Run a shell command directly")
        table.add_row("/read [path]", "Read a file")
        table.add_row("/search [query]", "Search the web")
        table.add_row("/status", "Show system status")
        table.add_row("/workspace [path]", "Show or change workspace")
        table.add_row("/exit", "Exit Roobie")
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
            console.print(f"  [green]✓ Model changed to: {arg}[/green]")
        else:
            console.print(f"  Current model: [cyan]{engine.model}[/cyan]")

    elif command == "/models":
        try:
            import requests
            r = requests.get(f"{engine.ollama_host}/api/tags", timeout=5)
            if r.status_code == 200:
                models = r.json().get("models", [])
                table = Table(title="Available Models")
                table.add_column("Name", style="cyan")
                table.add_column("Size", style="yellow")
                for m in models:
                    size_gb = m.get("size", 0) / (1024**3)
                    table.add_row(m["name"], f"{size_gb:.1f} GB")
                console.print(table)
            else:
                console.print("  [red]Failed to list models[/red]")
        except Exception as e:
            console.print(f"  [red]Ollama not reachable: {e}[/red]")

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

    # Workspace
    table.add_row("Workspace", f"[cyan]{engine.workspace_dir}[/cyan]")
    table.add_row("Model", f"[cyan]{engine.model}[/cyan]")
    table.add_row("Ollama", f"[cyan]{engine.ollama_host}[/cyan]")

    # Check Ollama
    if engine.check_model():
        table.add_row("Ollama Status", "[green]✅ Connected[/green]")
        try:
            import requests
            r = requests.get(f"{engine.ollama_host}/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])]
            table.add_row("Models", ", ".join(models))
        except Exception:
            pass
    else:
        table.add_row("Ollama Status", "[red]❌ Not running[/red]")

    # RAM
    try:
        import psutil
        mem = psutil.virtual_memory()
        ram_gb = mem.total / (1024**3)
        table.add_row("RAM", f"{ram_gb:.1f} GB ({mem.percent}% used)")
    except ImportError:
        pass

    # Node
    table.add_row("Node.js", "[green]✅[/green]" if shutil.which("node") else "[red]❌[/red]")
    table.add_row("Python", f"[green]✅ {sys.version.split()[0]}[/green]")

    # Conversation
    table.add_row("Chat History", f"{len(engine.conversation)} messages")

    console.print(table)


# ══════════════════════════════════════════════════════
# Subcommands — One-Shot Operations
# ══════════════════════════════════════════════════════

@app.command()
def run(
    prompt: str = typer.Argument(..., help="What to do"),
    workspace: Optional[str] = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Ollama model"),
):
    """🚀 Run a one-shot task (non-interactive). E.g.: roobie run 'Create a landing page'"""
    ws = workspace or os.getcwd()
    ws = os.path.abspath(ws)
    mdl = model or os.environ.get("ROOBIE_MODEL", "deepseek-ai/deepseek-coder-6.7b-instruct")
    host = os.environ.get("ROOBIE_OLLAMA_HOST", "http://localhost:11434")

    console.print(f"\n  📁 [cyan]{ws}[/cyan]  🧠 [cyan]{mdl}[/cyan]\n")

    from agent.chat_engine import ChatEngine
    engine = ChatEngine(ws, host, mdl)

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
    host = os.environ.get("ROOBIE_OLLAMA_HOST", "http://localhost:11434")
    mdl = os.environ.get("ROOBIE_MODEL", "qwen2.5-coder:3b")

    from agent.chat_engine import ChatEngine
    engine = ChatEngine(ws, host, mdl)
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


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """🤖 Roobie — Autonomous AI Coding Assistant. Run 'roobie chat' to start."""
    if ctx.invoked_subcommand is None:
        # Default to chat mode
        chat()


if __name__ == "__main__":
    app()
