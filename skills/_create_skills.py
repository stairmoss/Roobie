import json, os

BASE = "/mnt/18A660FBA660DB30/roobie/skills"

skills = {
    "uiux": {"name": "UI/UX Design", "description": "Modern UI/UX design patterns, layout systems, typography, spacing, color theory, and visual hierarchy", "tags": ["design", "ui", "ux", "layout"]},
    "seo": {"name": "SEO Optimization", "description": "Search engine optimization: metadata, schema markup, semantic HTML, OpenGraph, sitemap, robots.txt", "tags": ["seo", "metadata", "search"]},
    "nextjs": {"name": "Next.js", "description": "Next.js 14+ App Router patterns, SSR/SSG, layouts, loading states, error boundaries, API routes", "tags": ["nextjs", "react", "ssr"]},
    "react": {"name": "React", "description": "React component patterns, hooks, state management, performance optimization", "tags": ["react", "components", "hooks"]},
    "tailwind": {"name": "TailwindCSS", "description": "TailwindCSS utility patterns, custom configurations, responsive design, dark mode", "tags": ["tailwind", "css", "styling"]},
    "shadcn": {"name": "shadcn/ui", "description": "shadcn/ui component usage, customization, theming, and composition patterns", "tags": ["shadcn", "components", "ui"]},
    "framer-motion": {"name": "Framer Motion", "description": "Framer Motion animations: enter/exit, scroll, gesture, layout, shared layout animations", "tags": ["animation", "framer", "motion"]},
    "gsap": {"name": "GSAP", "description": "GSAP animation timelines, ScrollTrigger, morphing, text effects, stagger animations", "tags": ["animation", "gsap", "scroll"]},
    "threejs": {"name": "Three.js", "description": "Three.js 3D scenes, materials, lighting, post-processing, optimized for low-end devices", "tags": ["3d", "threejs", "webgl"]},
    "react-three-fiber": {"name": "React Three Fiber", "description": "R3F declarative 3D, Drei helpers, physics, performance optimization for 4GB RAM", "tags": ["3d", "r3f", "react"]},
    "animations": {"name": "Web Animations", "description": "CSS and JS animation best practices, micro-interactions, loading states, transitions", "tags": ["animation", "css", "motion"]},
    "backend": {"name": "Backend Development", "description": "FastAPI backend patterns, SQLite/PostgreSQL, authentication, API design, validation", "tags": ["backend", "api", "database"]},
    "accessibility": {"name": "Accessibility", "description": "WCAG 2.1 compliance, ARIA labels, keyboard navigation, screen readers, color contrast", "tags": ["a11y", "accessibility", "wcag"]},
    "performance": {"name": "Performance", "description": "Web performance optimization: bundle size, lazy loading, image optimization, Core Web Vitals", "tags": ["performance", "speed", "optimization"]},
    "debugging": {"name": "Debugging", "description": "Debugging strategies, error handling, logging, dev tools, common pitfalls", "tags": ["debug", "errors", "logging"]},
    "testing": {"name": "Testing", "description": "Testing patterns: unit, integration, e2e with Playwright, component testing", "tags": ["testing", "playwright", "jest"]},
    "architecture": {"name": "Architecture", "description": "Software architecture patterns: modular design, clean architecture, folder structures", "tags": ["architecture", "patterns", "structure"]},
    "deployment": {"name": "Deployment", "description": "Deployment strategies: Vercel, Docker, CI/CD, environment configuration", "tags": ["deploy", "docker", "ci"]},
    "saas": {"name": "SaaS", "description": "SaaS website patterns: pricing tables, feature grids, testimonials, CTAs, onboarding flows", "tags": ["saas", "startup", "product"]},
    "startup": {"name": "Startup", "description": "Startup landing page patterns: hero sections, social proof, value propositions, conversion optimization", "tags": ["startup", "landing", "conversion"]},
    "dashboard": {"name": "Dashboard", "description": "Dashboard UI patterns: data tables, charts, sidebar navigation, analytics widgets", "tags": ["dashboard", "admin", "analytics"]},
    "landingpage": {"name": "Landing Page", "description": "Landing page design: hero sections, features, testimonials, pricing, FAQ, CTA optimization", "tags": ["landing", "conversion", "marketing"]},
    "ecommerce": {"name": "E-Commerce", "description": "E-commerce patterns: product grids, cart, checkout, filters, search, payment integration", "tags": ["ecommerce", "shop", "products"]},
    "ai-tools": {"name": "AI Tools", "description": "AI tool interfaces: chat UIs, prompt builders, model selectors, streaming responses", "tags": ["ai", "chat", "tools"]},
    "portfolio": {"name": "Portfolio", "description": "Portfolio website patterns: project showcases, about sections, contact forms, image galleries", "tags": ["portfolio", "personal", "showcase"]},
    "blog": {"name": "Blog", "description": "Blog patterns: article layouts, MDX, syntax highlighting, table of contents, RSS feeds", "tags": ["blog", "content", "articles"]},
    "agency": {"name": "Agency", "description": "Agency website patterns: service showcases, team sections, case studies, client logos", "tags": ["agency", "services", "business"]},
    "planning": {"name": "Planning", "description": "AI planning strategies: task decomposition, dependency analysis, prioritization, milestone tracking", "tags": ["planning", "strategy", "tasks"]},
    "reasoning": {"name": "Reasoning", "description": "AI reasoning patterns: chain-of-thought, structured analysis, decision trees", "tags": ["reasoning", "thinking", "analysis"]},
    "self-improvement": {"name": "Self Improvement", "description": "Autonomous improvement loops: detect issues, generate fixes, apply, retest, iterate", "tags": ["improvement", "autonomous", "iteration"]},
}

skill_prompts = {
    "uiux": """# UI/UX Design Skill

## Design Principles
- Visual hierarchy guides user attention
- Consistent spacing system (4px/8px grid)
- Typography scale: use 3-4 font sizes max
- Color palette: primary, secondary, neutral, accent
- Whitespace is a design element, not empty space

## Layout Patterns
- Hero sections: full-width, clear headline, CTA above fold
- Card grids: consistent padding, subtle shadows, hover states
- Navigation: sticky header, clear active states, mobile hamburger
- Footer: organized links, social icons, newsletter signup

## Rules
- Mobile-first responsive design
- Minimum 16px body font size
- Touch targets minimum 44x44px
- Color contrast ratio >= 4.5:1
- Max content width 1280px
- Section padding: 80px+ vertical on desktop""",

    "seo": """# SEO Optimization Skill

## Required Elements
- Unique <title> per page (50-60 chars)
- Meta description per page (150-160 chars)
- Single <h1> per page with primary keyword
- Semantic heading hierarchy (h1 > h2 > h3)
- Alt text on all images
- Canonical URLs
- Structured data (JSON-LD)

## Generated Files
- sitemap.xml with all pages
- robots.txt with crawl rules
- OpenGraph meta tags
- Twitter Card meta tags
- Schema.org markup (Organization, WebSite, WebPage)

## Performance SEO
- Lighthouse Performance >= 95
- Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
- Image optimization (WebP, lazy loading)
- Font optimization (preload, display swap)""",

    "accessibility": """# Accessibility Skill

## WCAG 2.1 Requirements
- All images have descriptive alt text
- Form inputs have associated labels
- Color is not the only means of conveying information
- Sufficient color contrast (4.5:1 for normal text, 3:1 for large)
- Keyboard navigable (Tab, Enter, Escape, Arrow keys)
- Focus indicators visible
- Skip navigation links
- ARIA landmarks (main, nav, aside, footer)
- Screen reader announcements for dynamic content
- Reduced motion support (@media prefers-reduced-motion)""",

    "performance": """# Performance Skill

## Optimization Rules
- Code splitting per route
- Dynamic imports for heavy components
- Image optimization: next/image, WebP, responsive srcset
- Font subsetting and preloading
- CSS purging unused styles
- Minimize third-party scripts
- Debounce scroll/resize handlers
- Virtualize long lists
- Memoize expensive computations

## Targets (4GB RAM Systems)
- Bundle size < 200KB gzipped
- First Contentful Paint < 1.5s
- Time to Interactive < 3.5s
- Memory usage < 50MB runtime""",

    "landingpage": """# Landing Page Skill

## Section Order
1. Navigation (sticky, transparent on hero)
2. Hero (headline, subheadline, CTA, visual)
3. Social proof (logos, stats, trust badges)
4. Features/Benefits (3-6 items, icons, descriptions)
5. How it works (3 steps, numbered)
6. Testimonials (cards, avatars, quotes)
7. Pricing (3 tiers, highlighted recommended)
8. FAQ (accordion, 5-8 questions)
9. CTA section (final conversion push)
10. Footer (links, social, legal)

## Conversion Rules
- Primary CTA above the fold
- One primary action per section
- Social proof near CTAs
- Clear value proposition in headline
- Use benefit-driven copy, not feature-driven""",

    "dashboard": """# Dashboard Skill

## Layout Structure
- Sidebar navigation (collapsible, icons + labels)
- Top bar (search, notifications, user menu)
- Main content area (grid-based widgets)
- Breadcrumbs for deep navigation

## Widget Types
- Stat cards (number, label, trend indicator)
- Charts (line, bar, pie using Recharts)
- Data tables (sortable, filterable, paginated)
- Activity feeds (timeline, avatars)
- Quick action buttons

## Rules
- Use consistent card components
- Loading skeletons for async data
- Empty states with helpful messages
- Responsive: sidebar collapses on mobile""",

    "saas": """# SaaS Website Skill

## Required Sections
- Hero with product screenshot/demo
- Feature showcase (grid or alternating rows)
- Integration logos
- Pricing table (monthly/annual toggle)
- Testimonials with company names
- Security/compliance badges
- CTA with free trial offer

## Design Patterns
- Glassmorphism for cards
- Gradient backgrounds on hero
- Animated feature demonstrations
- Dark mode by default for dev tools
- Clean, minimal aesthetic""",

    "portfolio": """# Portfolio Skill

## Sections
- Hero with name, title, and brief intro
- About section with photo and bio
- Project showcase (filterable grid, hover previews)
- Skills/technologies section
- Experience timeline
- Contact form or email CTA
- Social links

## Design
- Minimal, content-focused layout
- Large project thumbnails
- Smooth page transitions
- Subtle scroll animations
- Dark/light mode toggle""",

    "threejs": """# Three.js / React Three Fiber Skill

## Performance Rules (4GB RAM)
- Max 50K triangles per scene
- Use instanced meshes for repeated geometry
- LOD (Level of Detail) for complex models
- Compress textures (max 1024x1024)
- Use draco compression for GLTF models
- Dispose geometries/materials on unmount
- RequestAnimationFrame-based rendering only
- Fallback to 2D for devices without WebGL

## Common Patterns
- Floating particles background
- 3D product viewers
- Interactive globe/map
- Animated geometric shapes
- Scroll-driven 3D transitions

## Required: <Canvas> with Suspense fallback""",
}

for skill_name, meta in skills.items():
    skill_dir = os.path.join(BASE, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "examples"), exist_ok=True)
    
    with open(os.path.join(skill_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    
    prompt = skill_prompts.get(skill_name, f"# {meta['name']} Skill\n\n{meta['description']}\n\nApply best practices for {meta['name'].lower()} when generating code.")
    with open(os.path.join(skill_dir, "skill.md"), "w") as f:
        f.write(prompt)

print(f"Created {len(skills)} skill modules")
