"""
Roobie Vision Analyzer
Uses Moondream (via Ollama) for screenshot analysis to detect UI issues,
spacing problems, typography flaws, and accessibility concerns.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console

console = Console()

# Structured vision analysis prompts
ANALYSIS_PROMPTS = {
    "layout": "Analyze the layout of this website screenshot. Look for: alignment issues, unbalanced sections, overflow problems, inconsistent margins. List specific issues found.",
    "typography": "Analyze the typography in this website screenshot. Check: font sizes, readability, line heights, font weights, heading hierarchy. List specific issues.",
    "spacing": "Analyze the spacing in this website screenshot. Check: padding consistency, margins between sections, whitespace balance, element gaps. List specific issues.",
    "hierarchy": "Analyze the visual hierarchy of this website screenshot. Check: clear focal points, information flow, CTA visibility, content grouping. List specific issues.",
    "accessibility": "Analyze this website screenshot for accessibility issues. Check: color contrast, text readability, button sizes, focus indicators. List specific issues.",
    "overall": "Rate this website UI on a scale of 1-10. Analyze: layout quality, typography, spacing, color palette, visual hierarchy, responsiveness. List the top 5 issues and suggest specific improvements.",
}


class VisionAnalyzer:
    """Vision-based website analysis using Moondream."""

    def __init__(self, settings):
        self.settings = settings
        self._model_manager = None

    @property
    def model_manager(self):
        if self._model_manager is None:
            from models.manager import ModelManager
            self._model_manager = ModelManager(self.settings)
        return self._model_manager

    def analyze_url(self, project_name: str, url: str) -> Dict:
        """Analyze a URL by first capturing screenshots then analyzing them."""
        from browser.automation import BrowserAutomation

        browser = BrowserAutomation(self.settings)
        screenshots = browser.capture_screenshots(project_name, url, mobile=True)
        browser.close()

        if screenshots:
            return self.analyze_screenshots(screenshots)
        return {"error": "No screenshots captured"}

    def analyze_screenshots(self, screenshot_paths: List[str]) -> Dict:
        """Analyze multiple screenshots for UI quality."""
        report = {
            "screenshots_analyzed": len(screenshot_paths),
            "issues": [],
            "suggestions": [],
            "scores": {},
            "overall_score": 0,
        }

        for path in screenshot_paths:
            if not Path(path).exists():
                continue

            viewport_name = Path(path).stem  # desktop, mobile, tablet

            # Run overall analysis
            analysis = self._analyze_image(path, "overall")
            if analysis:
                parsed = self._parse_analysis(analysis)
                report["scores"][viewport_name] = parsed.get("score", 5)

                for issue in parsed.get("issues", []):
                    report["issues"].append({
                        "viewport": viewport_name,
                        "issue": issue,
                    })

                for suggestion in parsed.get("suggestions", []):
                    report["suggestions"].append({
                        "viewport": viewport_name,
                        "suggestion": suggestion,
                    })

            # Run specific analyses
            for check_type in ["layout", "spacing", "typography"]:
                detail = self._analyze_image(path, check_type)
                if detail:
                    parsed_detail = self._parse_analysis(detail)
                    for issue in parsed_detail.get("issues", []):
                        report["issues"].append({
                            "viewport": viewport_name,
                            "type": check_type,
                            "issue": issue,
                        })

        # Calculate overall score
        if report["scores"]:
            report["overall_score"] = sum(report["scores"].values()) / len(report["scores"])

        console.print(f"[green]Vision analysis complete: {len(report['issues'])} issues found[/green]")
        return report

    def analyze_single(self, screenshot_path: str, analysis_type: str = "overall") -> str:
        """Analyze a single screenshot with a specific prompt."""
        return self._analyze_image(screenshot_path, analysis_type)

    def _analyze_image(self, image_path: str, analysis_type: str) -> Optional[str]:
        """Run vision model on a screenshot."""
        prompt = ANALYSIS_PROMPTS.get(analysis_type, ANALYSIS_PROMPTS["overall"])

        try:
            result = self.model_manager.vision_analyze(image_path, prompt)
            return result
        except Exception as e:
            console.print(f"[yellow]⚠️ Vision analysis error: {e}[/yellow]")
            return None

    def _parse_analysis(self, raw_text: str) -> Dict:
        """Parse raw vision model output into structured data."""
        result = {"issues": [], "suggestions": [], "score": 5}

        # Try to extract JSON if present
        if "{" in raw_text and "}" in raw_text:
            try:
                json_str = raw_text[raw_text.index("{"):raw_text.rindex("}") + 1]
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    result["issues"] = parsed.get("issues", [])
                    result["suggestions"] = parsed.get("suggestions", [])
                    result["score"] = parsed.get("score", parsed.get("overall_score", 5))
                    return result
            except (json.JSONDecodeError, ValueError):
                pass

        # Fallback: extract issues from text
        lines = raw_text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Look for numbered or bulleted items
            if any(line.startswith(p) for p in ["- ", "* ", "• "]):
                clean = line.lstrip("-*• ").strip()
                if any(kw in clean.lower() for kw in ["issue", "problem", "bad", "poor", "missing", "lack", "no ", "weak"]):
                    result["issues"].append(clean)
                elif any(kw in clean.lower() for kw in ["suggest", "improve", "add", "use", "consider", "should"]):
                    result["suggestions"].append(clean)
                else:
                    result["issues"].append(clean)

            # Look for score
            if "score" in line.lower() or "/10" in line:
                import re
                numbers = re.findall(r'(\d+(?:\.\d+)?)\s*/?\s*10', line)
                if numbers:
                    try:
                        result["score"] = float(numbers[0])
                    except ValueError:
                        pass

        return result

    def generate_fix_prompt(self, issues: List[Dict]) -> str:
        """Generate a prompt for fixing detected issues."""
        issue_text = "\n".join(
            f"- [{i.get('viewport', 'desktop')}] {i.get('type', 'general')}: {i.get('issue', '')}"
            for i in issues[:10]
        )
        return f"""Fix the following UI issues detected by visual analysis:

{issue_text}

Generate specific CSS/TSX code changes to address each issue.
Focus on: spacing, typography, layout, hierarchy, and accessibility.
Output changes as JSON array: [{{"file": "path", "original": "old code", "replacement": "new code"}}]"""
