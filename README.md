# 🤖 Roobie — Autonomous AI Coding Agent

> Local-first autonomous AI coding agent · Like Claude Code, but runs **offline** on **4GB RAM**

---

## What is Roobie?

Roobie is a **terminal-based autonomous AI coding agent** powered by **AirLLM** (disk-offloaded inference).

You type a coding task, and Roobie:
- 🧠 **Plans** the project
- 📄 **Creates & edits files**
- 💻 **Runs terminal commands**
- 🔍 **Searches the web**
- 🚀 **Starts localhost servers**
- 🔄 **Debugs and improves** autonomously

Similar to **Claude Code** and **Gemini CLI**, but:
- ✅ Fully **offline** (no API keys)
- ✅ Runs on **4GB RAM** (CPU only)
- ✅ Uses **AirLLM** (disk-offloaded quantized models)
- ✅ No Ollama required

---

## Installation

```bash
# 1. Clone and enter the project
cd roobie

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Install AirLLM + PyTorch (CPU)
pip install airllm transformers accelerate
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Quick Start

```bash
# Start interactive chat (default model: deepseek-coder-1.3b)
python main.py

# Use a specific model
python main.py chat --model Qwen/Qwen2.5-Coder-3B-Instruct

# Set a workspace directory
python main.py chat --workspace ~/my-project

# One-shot task (non-interactive)
python main.py run "Build me a FastAPI REST API with CRUD operations"

# Web search
python main.py search "Next.js 15 new features"

# System status
python main.py status
```

---

## Recommended Models (AirLLM)

| Model | Size | Best For |
|-------|------|----------|
| `deepseek-ai/deepseek-coder-1.3b-instruct` | ~800MB | Fast, lightweight coding |
| `Qwen/Qwen2.5-Coder-3B-Instruct` | ~2GB | Best quality, recommended |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` | ~1GB | Reasoning & planning |

Models are **auto-downloaded** from HuggingFace on first use.
AirLLM splits them into chunks and streams from disk — **no full RAM loading**.

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/models` | List available models |
| `/model <name>` | Switch model |
| `/clear` | Clear conversation history |
| `/tree` | Show workspace file tree |
| `/run <cmd>` | Run a shell command directly |
| `/read <path>` | Read a file |
| `/search <query>` | Web search |
| `/status` | System status |
| `/env` | Show active environment settings |
| `/workspace <path>` | Change workspace |
| `/exit` | Quit |

---

## Example Session

```
roobie> Build me a modern SaaS landing page with HTML, CSS, and JavaScript

🧠 Thinking...

📄 Create File → index.html
✓ Created index.html (4.2 KB)

📄 Create File → style.css
✓ Created style.css (2.8 KB)

📄 Create File → app.js
✓ Created app.js (1.1 KB)

💻 Run Command → python3 -m http.server 8080
✓ Server started at http://localhost:8080

🤖 Roobie: Done! I created a modern SaaS landing page with:
- Responsive hero section with gradient
- Features section with cards
- Pricing table
- CTA section
- Smooth scroll animations

Open http://localhost:8080 to see it.
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `ROOBIE_MODEL` | `deepseek-ai/deepseek-coder-1.3b-instruct` | HuggingFace model ID |
| `ROOBIE_WORKSPACE` | `~/.roobie/workspace` | Working directory |
| `ROOBIE_OLLAMA_HOST` | `http://localhost:11434` | Ollama fallback |
| `ROOBIE_MAX_TOOL_LOOPS` | `10` | Max tool calls per turn |

---

## Architecture

```
roobie/
├── main.py               ← Entry point
├── cli/
│   └── app.py            ← Typer CLI (chat loop, slash commands)
├── agent/
│   ├── chat_engine.py    ← Agentic loop (AirLLM + tool calling)
│   └── tool_executor.py  ← Dispatches tool calls
├── tools/
│   ├── file_tools.py     ← Create, edit, read, delete files
│   ├── terminal_tools.py ← Run shell commands safely
│   ├── search_tools.py   ← Web search (no API key)
│   └── thinking_tools.py ← Chain-of-thought reasoning
├── models/
│   └── manager.py        ← AirLLM + Ollama model management
├── browser/
│   └── automation.py     ← Playwright browser automation
├── vision/
│   └── analyzer.py       ← Screenshot analysis (Moondream)
├── memory/
│   └── store.py          ← SQLite conversation memory
└── prompts/
    └── templates.py      ← System prompts
```

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB |
| CPU | Any x86_64 | Modern multi-core |
| Storage | 2GB free | 5GB free |
| GPU | Not required | Optional (CUDA) |

## Testing

To run the unit test suite, make sure dev dependencies are installed, then run `pytest`:

```bash
# Run all tests
PYTHONPATH=. pytest

# Run settings tests specifically
PYTHONPATH=. pytest tests/test_settings.py
```

---

## License

MIT License — see `LICENSE`
