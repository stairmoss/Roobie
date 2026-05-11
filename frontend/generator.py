"""
Roobie Frontend Generator
Generates production-ready Next.js / React / TypeScript frontend code
with TailwindCSS, shadcn/ui, Framer Motion, and optional 3D support.
"""

import json
from typing import Dict, List, Optional
from rich.console import Console

console = Console()


class FrontendGenerator:
    """Generates complete frontend projects from specifications."""

    def __init__(self, settings, model_manager):
        self.settings = settings
        self.model = model_manager
        self.use_ai = getattr(self.model, "ai_enabled", False) and self.model.check_ollama()

    def generate(self, project_type: str, features: list, design_style: str,
                 architecture: dict, skill_context: str = "",
                 with_3d: bool = False) -> Dict[str, str]:
        """Generate all frontend files for a project."""
        files = {}

        # 1. Generate project config files
        files.update(self._generate_config_files(project_type))

        # 2. Generate layout and root files
        files.update(self._generate_layout(project_type, design_style))

        # 3. Generate page files based on architecture
        pages = architecture.get("pages", self._default_pages(project_type))
        files.update(self._generate_pages(pages, project_type, design_style, skill_context))

        # 4. Generate component files
        components = architecture.get("components", self._default_components(project_type))
        files.update(self._generate_components(components, project_type, design_style, skill_context))

        # 5. Generate styles
        files.update(self._generate_styles(design_style))

        # 6. Generate 3D components if needed
        if with_3d:
            files.update(self._generate_3d_components())

        console.print(f"[green]Generated {len(files)} frontend files[/green]")
        return files

    def _generate_config_files(self, project_type: str) -> Dict[str, str]:
        """Generate package.json, tsconfig, tailwind.config, etc."""
        files = {}

        files["package.json"] = json.dumps({
            "name": f"roobie-{project_type}",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.2.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "framer-motion": "^11.0.0",
                "lucide-react": "^0.344.0",
                "class-variance-authority": "^0.7.0",
                "clsx": "^2.1.0",
                "tailwind-merge": "^2.2.0"
            },
            "devDependencies": {
                "typescript": "^5.3.0",
                "@types/node": "^20.11.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "tailwindcss": "^3.4.0",
                "postcss": "^8.4.0",
                "autoprefixer": "^10.4.0",
                "eslint": "^8.56.0",
                "eslint-config-next": "14.2.0"
            }
        }, indent=2)

        files["tsconfig.json"] = json.dumps({
            "compilerOptions": {
                "target": "es5", "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True, "skipLibCheck": True, "strict": True,
                "noEmit": True, "esModuleInterop": True, "module": "esnext",
                "moduleResolution": "bundler", "resolveJsonModule": True,
                "isolatedModules": True, "jsx": "preserve", "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./src/*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }, indent=2)

        files["tailwind.config.ts"] = '''import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
        accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      animation: {
        "fade-in": "fadeIn 0.5s ease-out",
        "slide-up": "slideUp 0.5s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp: { "0%": { opacity: "0", transform: "translateY(20px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        slideDown: { "0%": { opacity: "0", transform: "translateY(-10px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
};

export default config;
'''

        files["postcss.config.js"] = '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
'''

        files["next.config.mjs"] = '''/** @type {import("next").NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: { formats: ["image/webp"] },
};

export default nextConfig;
'''

        files["next-env.d.ts"] = '''/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
'''

        files[".gitignore"] = '''node_modules
.next
dist
out
.env
.DS_Store
npm-debug.log*
yarn-debug.log*
yarn-error.log*
coverage
'''

        files["README.md"] = f'''# Roobie Generated {project_type.title()} Project

This project was generated by Roobie.

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.
'''

        return files

    def _generate_layout(self, project_type: str, design_style: str) -> Dict[str, str]:
        """Generate root layout with metadata and global styles."""
        files = {}

        files["src/app/layout.tsx"] = f'''import type {{ Metadata }} from "next";
import {{ Inter }} from "next/font/google";
import "./globals.css";

const inter = Inter({{ subsets: ["latin"] }});

export const metadata: Metadata = {{
  title: "Roobie Generated - {project_type.title()}",
  description: "A modern {project_type} website generated by Roobie AI",
  openGraph: {{
    title: "Roobie Generated - {project_type.title()}",
    description: "A modern {project_type} website generated by Roobie AI",
    type: "website",
  }},
  twitter: {{ card: "summary_large_image" }},
}};

export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{
  return (
    <html lang="en" className="scroll-smooth">
      <body className={{inter.className + " antialiased bg-background text-foreground"}}>
        {{children}}
      </body>
    </html>
  );
}}
'''
        return files

    def _generate_styles(self, design_style: str) -> Dict[str, str]:
        """Generate global CSS with design tokens."""
        palette = {
            "modern": {"bg": "0 0% 100%", "fg": "222 47% 11%", "primary": "221 83% 53%", "accent": "262 83% 58%"},
            "dark": {"bg": "222 47% 5%", "fg": "210 40% 98%", "primary": "217 91% 60%", "accent": "263 70% 50%"},
            "glassmorphism": {"bg": "222 47% 5%", "fg": "210 40% 98%", "primary": "199 89% 48%", "accent": "280 65% 60%"},
            "minimal": {"bg": "0 0% 100%", "fg": "0 0% 10%", "primary": "0 0% 10%", "accent": "0 0% 40%"},
            "gradient": {"bg": "222 47% 5%", "fg": "210 40% 98%", "primary": "330 80% 60%", "accent": "260 80% 60%"},
        }
        p = palette.get(design_style, palette["modern"])

        return {"src/app/globals.css": f'''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {{
  :root {{
    --background: {p["bg"]};
    --foreground: {p["fg"]};
    --primary: {p["primary"]};
    --primary-foreground: 0 0% 100%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 222 47% 11%;
    --accent: {p["accent"]};
    --accent-foreground: 0 0% 100%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --border: 214 32% 91%;
    --radius: 0.5rem;
  }}

  .dark {{
    --background: 222 47% 5%;
    --foreground: 210 40% 98%;
    --primary: {p["primary"]};
    --primary-foreground: 0 0% 100%;
    --secondary: 217 33% 17%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 65%;
    --border: 217 33% 17%;
  }}

  * {{ @apply border-border; }}
  body {{ @apply bg-background text-foreground; }}
}}

@layer utilities {{
  .glass {{
    @apply bg-white/10 backdrop-blur-lg border border-white/20;
  }}
  .gradient-text {{
    @apply bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent;
  }}
}}
'''
        }

    def _default_pages(self, project_type: str) -> list:
        """Default pages for each project type."""
        page_map = {
            "landing": ["home"],
            "saas": ["home", "pricing", "features", "about"],
            "dashboard": ["dashboard", "analytics", "settings"],
            "portfolio": ["home", "projects", "about", "contact"],
            "ecommerce": ["home", "products", "cart", "checkout"],
            "blog": ["home", "blog", "about"],
            "agency": ["home", "services", "work", "about", "contact"],
        }
        return page_map.get(project_type, ["home"])

    def _default_components(self, project_type: str) -> list:
        """Default components for each project type."""
        base = ["Navbar", "Footer", "Button", "Card"]
        extras = {
            "landing": ["Hero", "Features", "Testimonials", "CTA", "FAQ", "Pricing"],
            "saas": ["Hero", "Features", "Pricing", "Testimonials", "CTA", "Stats"],
            "dashboard": ["Sidebar", "StatCard", "DataTable", "Chart"],
            "portfolio": ["Hero", "ProjectCard", "SkillBar", "ContactForm"],
            "ecommerce": ["ProductCard", "CartItem", "SearchBar", "FilterPanel"],
            "blog": ["ArticleCard", "CategoryFilter", "Newsletter"],
            "agency": ["Hero", "ServiceCard", "CaseStudy", "TeamMember"],
        }
        return base + extras.get(project_type, [])

    def _generate_pages(self, pages: list, project_type: str,
                        design_style: str, skill_context: str) -> Dict[str, str]:
        """Generate page files using AI model."""
        files = {}
        from prompts.templates import PromptTemplates

        for page_name in pages:
            page = page_name if isinstance(page_name, str) else page_name.get("name", "home")
            route = "" if page == "home" else page

            prompt = f"""{PromptTemplates.FRONTEND_PROMPT}

{skill_context[:2000]}

Generate a complete Next.js 14 App Router page component for a {project_type} website.
Page: {page}
Design style: {design_style}

Requirements:
- TypeScript
- TailwindCSS classes
- Responsive design
- Semantic HTML
- Framer Motion animations
- Export as default function

Output ONLY the complete TSX code, no explanations."""

            code = ""
            if self.use_ai:
                code = self.model.generate(prompt, temperature=0.5, stream=False)
                code = self._extract_code(code)

            if not code.strip() or "export default" not in code:
                code = self._fallback_page(page, project_type)

            path = f"src/app/{route}/page.tsx" if route else "src/app/page.tsx"
            files[path] = code

        return files

    def _generate_components(self, components: list, project_type: str,
                             design_style: str, skill_context: str) -> Dict[str, str]:
        """Generate component files using AI model."""
        files = {}
        from prompts.templates import PromptTemplates

        for comp_name in components:
            comp = comp_name if isinstance(comp_name, str) else comp_name.get("name", "Component")

            prompt = f"""{PromptTemplates.FRONTEND_PROMPT}

Generate a reusable React component: {comp}
Project type: {project_type}
Design: {design_style}
Use TypeScript, TailwindCSS, and proper props interface.

Output ONLY the complete TSX code."""

            code = ""
            if self.use_ai:
                code = self.model.generate(prompt, temperature=0.5, stream=False)
                code = self._extract_code(code)

            if not code.strip() or "export default" not in code:
                code = self._fallback_component(comp)

            files[f"src/components/{comp}.tsx"] = code

        return files

    def _generate_3d_components(self) -> Dict[str, str]:
        """Generate React Three Fiber 3D components."""
        return {
            "src/components/3d/Scene.tsx": '''"use client";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, Float } from "@react-three/drei";
import { Suspense } from "react";

function FloatingShape() {
  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <mesh>
        <icosahedronGeometry args={[1, 1]} />
        <meshStandardMaterial color="#6366f1" wireframe />
      </mesh>
    </Float>
  );
}

export default function Scene() {
  return (
    <div className="w-full h-[400px]">
      <Canvas camera={{ position: [0, 0, 5] }}>
        <Suspense fallback={null}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <FloatingShape />
          <OrbitControls enableZoom={false} autoRotate />
          <Environment preset="night" />
        </Suspense>
      </Canvas>
    </div>
  );
}
''',
        }

    def _extract_code(self, response: str) -> str:
        """Extract code from AI response."""
        if "```tsx" in response:
            return response.split("```tsx")[1].split("```")[0].strip()
        if "```typescript" in response:
            return response.split("```typescript")[1].split("```")[0].strip()
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                return parts[1].strip()
        return response.strip()

    def _fallback_page(self, page: str, project_type: str) -> str:
        """Fallback page template when AI generation fails."""
        return f'''export default function {page.title().replace(" ", "")}Page() {{
  return (
    <main className="min-h-screen">
      <section className="container mx-auto px-4 py-20">
        <h1 className="text-4xl font-bold mb-6">{page.title()}</h1>
        <p className="text-lg text-muted-foreground">
          Welcome to the {page} page of this {project_type} website.
        </p>
      </section>
    </main>
  );
}}
'''

    def _fallback_component(self, name: str) -> str:
        """Fallback component template."""
        return f'''interface {name}Props {{
  className?: string;
}}

export default function {name}({{ className = "" }}: {name}Props) {{
  return (
    <div className={{`${{className}}`}}>
      <p>{name} Component</p>
    </div>
  );
}}
'''
