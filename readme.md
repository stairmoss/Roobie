# Roobie

Roobie is a lightweight autonomous full-stack AI web developer agent that runs fully locally using open-source tools and lightweight AI models.

Roobie is inspired by:
- Claude Code
- Cline
- Devin
- OpenHands
- Cursor

but optimized for:
- local-first workflows
- low-end laptops
- 4GB RAM systems
- CPU inference
- autonomous website generation
- SEO-first development
- browser automation
- visual website analysis

---

# Vision

Roobie aims to become a fully autonomous AI software engineer capable of:

- researching
- planning
- coding
- testing
- analyzing
- improving
- optimizing
- deploying

modern production-ready websites completely locally.

---

# Features

## Autonomous Web Development

Roobie can:
- generate frontend code
- generate backend code
- build complete websites
- generate reusable components
- create APIs
- build dashboards
- generate landing pages
- create portfolios
- build SaaS websites

---

## Research Before Coding

Roobie always researches before generating code.

Research includes:
- competitor analysis
- UI inspiration
- SEO opportunities
- accessibility standards
- startup trends
- modern frontend patterns

Preferred tools:
- SearXNG
- crawl4ai
- Firecrawl

---

## Browser Automation

Roobie uses browser automation to inspect websites automatically.

Features:
- localhost preview
- Playwright testing
- form testing
- navigation testing
- responsiveness testing
- screenshot capture
- console inspection

Preferred tools:
- Playwright
- Browser Use

---

## Vision-Based Website Analysis

Roobie visually analyzes websites using AI vision models.

The vision system detects:
- broken layouts
- spacing issues
- typography issues
- weak UI hierarchy
- animation problems
- accessibility issues
- responsiveness issues

Roobie then automatically improves the website.

---

## Autonomous Improvement Loop

Roobie continuously improves generated websites.

Workflow:

```txt
Generate Website
    ↓
Run Localhost
    ↓
Capture Screenshot
    ↓
Analyze UI
    ↓
Find Problems
    ↓
Generate Fixes
    ↓
Apply Fixes
    ↓
Retest


SEO Optimization

Every generated website includes:

meta tags
OpenGraph tags
Twitter cards
semantic HTML
sitemap.xml
robots.txt
schema markup
accessibility improvements

Target Lighthouse scores:

Performance ≥ 95
Accessibility ≥ 95
SEO ≥ 95
Best Practices ≥ 95
3D Website Support

Roobie supports:

Three.js
React Three Fiber
animated backgrounds
shaders
particles
interactive 3D scenes

3D websites are optimized for:

performance
mobile devices
low-end hardware
Tech Stack
Layer	Technology
CLI	Python + Typer
Agent Framework	LangGraph
Runtime	Ollama
Low RAM Runtime	AirLLM
Coding Model	Qwen2.5 Coder 3B
Reasoning Model	DeepSeek R1 Distill 1.5B
Vision Model	Moondream
Browser Automation	Playwright
Local Search	SearXNG
Scraping	crawl4ai
Memory	SQLite
Vector Database	ChromaDB
Frontend	Next.js
Styling	TailwindCSS
3D	React Three Fiber
SEO	Lighthouse + axe-core
Folder Structure
roobie/
├── agent/
├── browser/
├── cli/
├── config/
├── frontend/
├── backend/
├── memory/
├── models/
├── mcp/
├── prompts/
├── research/
├── sandbox/
├── seo/
├── skills/
├── vision/
├── workflows/
└── logs/
Skill System

Roobie uses Claude-style dynamic skills.

Skills are reusable prompt systems loaded automatically depending on the task.

Example skills:

skills/
 ├── uiux/
 ├── seo/
 ├── nextjs/
 ├── animations/
 ├── backend/
 ├── accessibility/
 ├── startup/
 ├── ecommerce/
 ├── dashboard/
 ├── portfolio/
 └── threejs/
Recommended Models
Coding

Preferred:

Qwen2.5 Coder 3B
DeepSeek Coder 1.3B
Reasoning

Preferred:

DeepSeek R1 Distill 1.5B
Vision

Preferred:

Moondream
Recommended Runtime

Preferred runtimes:

Ollama
AirLLM
llama.cpp

Preferred quantization:

Q4_K_M GGUF
Installation
Clone Repository
git clone https://github.com/yourname/roobie.git
cd roobie
Install Python Dependencies
pip install -r requirements.txt
Install Playwright
playwright install
Install Ollama

Install Ollama locally.

Then pull models:

ollama pull qwen2.5-coder:3b
ollama pull deepseek-r1:1.5b
Start Roobie
python main.py
Example Commands
roobie init
roobie think
roobie research
roobie build
roobie preview
roobie screenshot
roobie improve
roobie seo
roobie deploy
Workflow

Roobie follows this pipeline:

Understand Request
    ↓
Research Competitors
    ↓
Analyze SEO
    ↓
Create Architecture
    ↓
Load Skills
    ↓
Generate Frontend
    ↓
Generate Backend
    ↓
Run Website
    ↓
Analyze Website
    ↓
Improve UI/UX
    ↓
Optimize SEO
    ↓
Finalize Project
Performance Goals

Roobie is optimized for:

4GB RAM systems
CPU-only inference
low-end laptops
lightweight workflows

Optimization strategies:

quantized models
lazy loading
streaming inference
optimized assets
lightweight dependencies
Security

Roobie:

sanitizes inputs
validates requests
requests permission for dangerous actions
avoids unsafe filesystem operations
Roadmap

Planned features:

multi-agent workflows
voice interaction
mobile app generation
AI plugin marketplace
collaborative editing
deployment automation
self-healing projects
AI-generated documentation
License

MIT License

Final Goal

Roobie aims to become:

A lightweight autonomous AI software engineer capable of researching, planning, generating, testing, analyzing, improving, optimizing, and deploying modern production-ready websites completely locally on low-end systems.