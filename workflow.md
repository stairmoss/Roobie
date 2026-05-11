# WORKFLOW.md

# Roobie Autonomous Workflow System

# Overview

Roobie uses a fully autonomous multi-stage workflow system designed for local-first AI web development.

The workflow system allows Roobie to:
- understand requests
- research before coding
- generate architecture
- create websites
- analyze websites visually
- improve websites automatically
- optimize SEO
- optimize performance

The workflow is inspired by:
- Claude Code
- Devin
- OpenHands
- Cline

but optimized for:
- local execution
- lightweight models
- low-end hardware
- frontend-first workflows

---

# Main Workflow

Roobie follows this primary execution pipeline:

```txt
User Request
    ↓
Task Understanding
    ↓
Research Phase
    ↓
Competitor Analysis
    ↓
SEO Analysis
    ↓
Architecture Planning
    ↓
Skill Loading
    ↓
Frontend Generation
    ↓
Backend Generation
    ↓
Run Localhost
    ↓
Browser Automation
    ↓
Screenshot Capture
    ↓
Vision Analysis
    ↓
UI/UX Improvements
    ↓
SEO Optimization
    ↓
Performance Optimization
    ↓
Final Output
Workflow Stages
Stage 1 — Task Understanding

Purpose:
Understand exactly what the user wants before taking action.

Responsibilities:

parse user request
detect project type
detect frontend requirements
detect backend requirements
detect SEO requirements
detect animation requirements
detect 3D requirements

Example:

Input:
Build a modern SaaS landing page

Detected:
- Next.js
- TailwindCSS
- SEO optimization
- Framer Motion
- Responsive layout
- Startup UI skill
Stage 2 — Research Phase

Purpose:
Research before coding.

Responsibilities:

analyze competitor websites
collect UI inspiration
analyze SEO keywords
collect layout ideas
identify design trends
identify accessibility patterns

Preferred tools:

SearXNG
crawl4ai
Firecrawl

Research output:

design references
SEO opportunities
animation ideas
component suggestions
content structure
Stage 3 — Competitor Analysis

Purpose:
Understand industry standards.

Roobie should:

inspect modern websites
analyze hero sections
analyze typography
analyze layouts
analyze animations
analyze CTA patterns
analyze navigation systems

Extract:

strengths
weaknesses
reusable ideas
UX patterns
Stage 4 — SEO Analysis

Purpose:
Generate SEO-first architecture.

Responsibilities:

identify keywords
generate metadata strategy
create heading hierarchy
generate semantic structure
optimize accessibility
optimize Lighthouse score

Target scores:

Category	Target
Performance	95+
Accessibility	95+
SEO	95+
Best Practices	95+
Stage 5 — Architecture Planning

Purpose:
Create scalable architecture before coding.

Responsibilities:

choose frameworks
create folder structure
split components
create backend architecture
create API structure
create database structure

Preferred frontend stack:

Next.js
React
TypeScript
TailwindCSS

Preferred backend stack:

FastAPI
SQLite
PostgreSQL

Example structure:

src/
 ├── app/
 ├── components/
 ├── sections/
 ├── hooks/
 ├── styles/
 ├── utils/
 └── lib/
Stage 6 — Skill Loading

Purpose:
Load Claude-style dynamic skills.

Roobie dynamically loads skills based on:

project type
design style
framework
backend needs
animation needs
SEO requirements

Example:

Project:
Modern startup landing page

Loaded skills:
- UI/UX
- Startup
- SEO
- Accessibility
- Animations

Skill categories:

skills/
 ├── uiux/
 ├── seo/
 ├── animations/
 ├── backend/
 ├── accessibility/
 ├── ecommerce/
 ├── startup/
 ├── dashboard/
 ├── landingpage/
 └── threejs/
Stage 7 — Frontend Generation

Purpose:
Generate modern production-ready frontend code.

Responsibilities:

generate layouts
generate components
generate sections
generate animations
generate responsive design
generate navigation
generate forms

Frontend requirements:

reusable architecture
semantic HTML
accessibility
responsive design
optimized assets
lazy loading

Preferred libraries:

shadcn/ui
Framer Motion
GSAP
Stage 8 — Backend Generation

Purpose:
Generate scalable backend systems.

Responsibilities:

API generation
authentication
database integration
route generation
validation
middleware generation

Backend structure:

backend/
 ├── routes/
 ├── controllers/
 ├── services/
 ├── middleware/
 ├── database/
 └── models/
Stage 9 — Run Localhost

Purpose:
Automatically preview generated websites.

Responsibilities:

launch development server
open localhost
monitor build errors
monitor runtime errors
detect crashes

Preferred browser:

Chromium
Stage 10 — Browser Automation

Purpose:
Automatically inspect generated websites.

Preferred tools:

Playwright
Browser Use

Responsibilities:

test navigation
click buttons
test forms
inspect console
inspect responsiveness
capture screenshots

Browser workflow:

Launch Browser
    ↓
Open Localhost
    ↓
Inspect Website
    ↓
Test Navigation
    ↓
Test Forms
    ↓
Inspect Console
    ↓
Capture Screenshots
Stage 11 — Screenshot Capture

Purpose:
Collect visual data for AI analysis.

Responsibilities:

full-page screenshots
mobile screenshots
tablet screenshots
desktop screenshots
interaction screenshots

Captured states:

homepage
navigation
forms
modals
animations
hover states
Stage 12 — Vision Analysis

Purpose:
Analyze website quality visually.

Preferred vision model:

Moondream

Responsibilities:

analyze layout quality
detect spacing issues
detect alignment issues
detect poor typography
detect weak UI hierarchy
detect accessibility issues
detect animation problems

Vision analysis output:

detected issues
UI critique
improvement suggestions
automatic fixes
Stage 13 — UI/UX Improvements

Purpose:
Continuously improve generated websites.

Roobie should:

improve layouts
improve typography
improve spacing
improve animations
improve accessibility
improve responsiveness

Improvement loop:

Analyze Website
    ↓
Find Problems
    ↓
Generate Fixes
    ↓
Apply Fixes
    ↓
Reload Website
    ↓
Retest
Stage 14 — SEO Optimization

Purpose:
Optimize websites for search engines.

Responsibilities:

generate metadata
optimize headings
generate schema markup
optimize accessibility
optimize semantic HTML
optimize page speed

Generated files:

sitemap.xml
robots.txt
metadata
OpenGraph tags
Twitter cards
Stage 15 — Performance Optimization

Purpose:
Ensure websites remain lightweight and fast.

Responsibilities:

reduce bundle size
optimize images
lazy load assets
optimize rendering
minimize dependencies
optimize animations

Target systems:

4GB RAM laptops
CPU-only systems
low-end devices
Stage 16 — Final Output

Purpose:
Deliver polished production-ready projects.

Generated output must include:

production-ready source code
README.md
deployment instructions
environment setup
SEO setup
folder structure
reusable architecture
Autonomous Improvement Workflow

Roobie continuously improves websites until quality targets are achieved.

Loop:

Generate Website
    ↓
Run Localhost
    ↓
Capture Screenshot
    ↓
Analyze UI
    ↓
Detect Problems
    ↓
Generate Improvements
    ↓
Apply Fixes
    ↓
Retest
    ↓
Repeat

Quality targets:

responsive UI
strong typography
good spacing
accessibility compliance
SEO optimization
modern design quality
Multi-Agent Workflow

Roobie can optionally support multiple agents.

Example:

Planner Agent
    ↓
Research Agent
    ↓
Coding Agent
    ↓
Browser Agent
    ↓
Vision Agent
    ↓
SEO Agent
    ↓
Deployment Agent

Each agent has specialized responsibilities.

Local AI Workflow

Roobie runs locally using lightweight models.

Preferred runtime stack:

Ollama
AirLLM
llama.cpp

Preferred models:

Qwen2.5 Coder 3B
DeepSeek Coder 1.3B
DeepSeek R1 Distill 1.5B
Moondream

Preferred quantization:

Q4_K_M GGUF

Optimization goals:

low RAM usage
fast inference
CPU support
local execution
MCP Workflow

Roobie supports MCP integrations.

Required MCP servers:

filesystem
terminal
playwright
github
docker
sqlite

Responsibilities:

file editing
terminal execution
browser control
repository management
local database access

Roobie must request permission before:

deleting files
executing dangerous commands
modifying system configurations
3D Workflow

Roobie supports modern 3D websites.

Preferred stack:

Three.js
React Three Fiber
Drei
GSAP

3D workflow:

Generate 3D Scene
    ↓
Optimize Assets
    ↓
Test FPS
    ↓
Optimize Rendering
    ↓
Test Mobile Support

3D systems must:

remain performant
avoid FPS drops
support mobile devices
use lazy loading
Final Workflow Philosophy

Roobie follows these principles:

research before coding
think before generating
test before finalizing
analyze visually
improve continuously
optimize performance
prioritize accessibility
prioritize SEO
maintain clean architecture
remain lightweight

Roobie should behave like:

a senior frontend engineer
a UI/UX designer
a browser automation engineer
an SEO engineer
a performance engineer
an autonomous AI software engineer

