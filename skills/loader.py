"""
Roobie Dynamic Skill Loader
Claude-style dynamic skill system that loads modular prompt+pattern sets
based on project type, UI style, and requirements.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console

console = Console()

# Base directory for skills
SKILLS_DIR = Path(__file__).parent


class SkillLoader:
    """Loads and manages dynamic skills for Roobie."""

    def __init__(self, skills_dir: str = None):
        self.skills_dir = Path(skills_dir) if skills_dir else SKILLS_DIR
        self._cache: Dict[str, Dict] = {}

    def list_skills(self) -> List[Dict]:
        """List all available skills with metadata."""
        skills = []
        for category_dir in sorted(self.skills_dir.iterdir()):
            if category_dir.is_dir() and not category_dir.name.startswith("_"):
                meta_path = category_dir / "meta.json"
                if meta_path.exists():
                    with open(meta_path) as f:
                        meta = json.load(f)
                    skills.append({
                        "category": category_dir.name,
                        "name": meta.get("name", category_dir.name),
                        "description": meta.get("description", ""),
                        "tags": meta.get("tags", []),
                    })
                else:
                    # Auto-discover from skill.md
                    skill_md = category_dir / "skill.md"
                    desc = ""
                    if skill_md.exists():
                        with open(skill_md) as f:
                            first_line = f.readline().strip().lstrip("# ")
                            desc = first_line
                    skills.append({
                        "category": category_dir.name,
                        "name": category_dir.name.replace("-", " ").title(),
                        "description": desc or f"{category_dir.name} skill",
                        "tags": [],
                    })
        return skills

    def load_skill(self, name: str) -> Optional[Dict]:
        """Load a skill by name. Returns dict with prompt, patterns, examples."""
        if name in self._cache:
            return self._cache[name]

        skill_dir = self.skills_dir / name
        if not skill_dir.exists():
            # Try hyphenated version
            skill_dir = self.skills_dir / name.replace("_", "-")
        if not skill_dir.exists():
            return None

        skill_data = {"name": name, "prompt": "", "patterns": [], "examples": [], "rules": []}

        # Load skill.md (main prompt)
        skill_md = skill_dir / "skill.md"
        if skill_md.exists():
            with open(skill_md) as f:
                skill_data["prompt"] = f.read()

        # Load meta.json
        meta_path = skill_dir / "meta.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
                skill_data.update(meta)

        # Load patterns.json
        patterns_path = skill_dir / "patterns.json"
        if patterns_path.exists():
            with open(patterns_path) as f:
                skill_data["patterns"] = json.load(f)

        # Load examples directory
        examples_dir = skill_dir / "examples"
        if examples_dir.exists():
            for ex_file in sorted(examples_dir.iterdir()):
                if ex_file.is_file():
                    with open(ex_file) as f:
                        skill_data["examples"].append({
                            "name": ex_file.stem,
                            "content": f.read(),
                        })

        self._cache[name] = skill_data
        return skill_data

    def load_skills_for_project(self, project_type: str, features: list = None,
                                 design_style: str = None) -> List[Dict]:
        """Automatically select and load skills based on project context."""
        skill_map = {
            "landing": ["uiux", "seo", "landingpage", "animations", "accessibility", "performance"],
            "saas": ["uiux", "seo", "saas", "startup", "animations", "dashboard", "accessibility", "performance"],
            "dashboard": ["uiux", "dashboard", "backend", "accessibility", "performance"],
            "portfolio": ["uiux", "portfolio", "animations", "seo", "accessibility", "performance"],
            "ecommerce": ["uiux", "ecommerce", "backend", "seo", "accessibility", "performance"],
            "blog": ["uiux", "blog", "seo", "accessibility", "performance"],
            "agency": ["uiux", "agency", "animations", "seo", "accessibility", "performance"],
        }

        needed = skill_map.get(project_type, ["uiux", "seo", "accessibility", "performance"])

        if features:
            feature_skills = {
                "3d": ["threejs", "react-three-fiber"],
                "three": ["threejs", "react-three-fiber"],
                "animation": ["animations", "framer-motion", "gsap"],
                "auth": ["backend"],
                "api": ["backend"],
                "dashboard": ["dashboard"],
                "payment": ["ecommerce"],
            }
            for feat in features:
                feat_lower = feat.lower()
                for key, skills_list in feature_skills.items():
                    if key in feat_lower:
                        needed.extend(skills_list)

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for s in needed:
            if s not in seen:
                seen.add(s)
                unique.append(s)

        loaded = []
        for skill_name in unique:
            data = self.load_skill(skill_name)
            if data:
                loaded.append(data)

        return loaded

    def get_combined_prompt(self, skills: List[Dict]) -> str:
        """Combine multiple skill prompts into one context string."""
        parts = []
        for skill in skills:
            if skill.get("prompt"):
                parts.append(f"=== SKILL: {skill['name'].upper()} ===\n{skill['prompt']}")
        return "\n\n".join(parts)
