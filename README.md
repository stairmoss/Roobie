# Roobie 🤖

**Autonomous Local-First AI Web Developer**

Roobie is a lightweight CLI tool that autonomously researches, plans, generates, tests, analyzes, improves, and optimizes modern production-ready websites — running entirely locally on open-source models.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 Autonomous Planning | Understands requests, decomposes tasks, creates architecture |
| 🔍 Research Engine | SearXNG + crawl4ai for competitor analysis and SEO research |
| 🎨 Frontend Generation | Next.js 14, TypeScript, TailwindCSS, shadcn/ui, Framer Motion |
| ⚙️ Backend Generation | FastAPI + SQLite with modular architecture |
| 📸 Screenshot Capture | Multi-viewport Playwright screenshots |
| 👁️ Vision Analysis | Moondream AI analyzes UI quality, spacing, typography |
| 🔄 Improvement Loop | Autonomous fix → retest → improve cycle |
| 🔎 SEO Optimization | Metadata, schema, sitemap, robots.txt, Lighthouse 95+ |
| 📚 Dynamic Skills | 30+ Claude-style skill modules loaded per project |
| 🎮 3D Support | React Three Fiber for interactive 3D scenes |
| 💾 Memory System | SQLite + ChromaDB for persistent project memory |
| 🔌 MCP Integration | Filesystem, terminal, SQLite tool interfaces |

---

## 🏗️ Architecture

```
roobie/
├── agent/          # Agent orchestrator (16-stage pipeline)
├── browser/        # Playwright browser automation
├── cli/            # Typer + Rich CLI interface
├── config/         # Settings, paths, environment
├── frontend/       # Next.js code generation
├── backend/        # FastAPI code generation
├── memory/         # SQLite + ChromaDB storage
├── models/         # Ollama model management
├── mcp/            # MCP tool server
├── prompts/        # System prompt templates
├── research/       # SearXNG + crawl4ai research
├── sandbox/        # Project scaffolding + localhost
├── seo/            # SEO optimization engine
├── skills/         # 30+ dynamic skill modules
├── vision/         # Moondream screenshot analysis
├── workflows/      # Improvement loop orchestration
├── logs/           # Structured logging
├── main.py         # Entry point
├── requirements.txt
└── setup.py
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourname/roobie.git
cd roobie
pip install -r requirements.txt
```

### 2. Install Playwright

```bash
playwright install chromium
```

### 3. Install Ollama & Models

```bash
# Install Ollama (https://ollama.ai)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull qwen2.5-coder:3b
ollama pull deepseek-r1:1.5b
ollama pull moondream:latest
```

### 4. Run Roobie

```bash
python main.py build "Build a modern SaaS landing page with pricing"
```

---

## 📋 CLI Commands

| Command | Description |
|---------|-------------|
| `roobie build <prompt>` | Build a website from natural language |
| `roobie init <name>` | Initialize a new project |
| `roobie think <prompt>` | Analyze without building |
| `roobie research <query>` | Research a topic |
| `roobie preview <project>` | Preview in browser |
| `roobie screenshot <project>` | Capture screenshots |
| `roobie improve <project>` | Run improvement loop |
| `roobie seo <project>` | Optimize SEO |
| `roobie analyze <project>` | Vision-based UI analysis |
| `roobie skills` | List available skills |
| `roobie models` | List AI models |
| `roobie status` | System health check |
| `roobie chat` | Interactive chat mode |

---

## 🤖 AI Models

| Model | Purpose | Size |
|-------|---------|------|
| Qwen2.5 Coder 3B | Code generation | ~2GB |
| DeepSeek Coder 1.3B | Lightweight coding | ~1GB |
| DeepSeek R1 1.5B | Reasoning & planning | ~1GB |
| Moondream | Vision / screenshots | ~1GB |

All models run locally via Ollama with Q4_K_M quantization.

---

## 📚 Skill System

30+ dynamic skills automatically loaded based on project type:

**Core:** uiux, seo, accessibility, performance, debugging, testing, architecture, deployment

**Web:** nextjs, react, tailwind, shadcn, framer-motion, gsap, threejs, animations

**Product:** saas, startup, dashboard, landingpage, ecommerce, portfolio, blog, agency

**AI Agent:** planning, reasoning, self-improvement

---

## 🔄 Autonomous Workflow

```
User Request → Understand → Research → Plan Architecture → Load Skills
    → Generate Frontend → Generate Backend → Run Localhost
    → Browser Test → Screenshot → Vision Analysis
    → Improve UI → Optimize SEO → Finalize
```

---

## ⚡ Performance

Optimized for **4GB RAM** systems:
- CPU-only inference
- Quantized models (Q4_K_M GGUF)
- Lazy-loaded subsystems
- Streaming inference
- Minimal dependencies

---

## 📄 License

MIT License
