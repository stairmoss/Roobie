"""
Roobie Browser Automation
Playwright-based browser automation for localhost testing, screenshots,
navigation testing, form testing, responsiveness testing, and console inspection.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()


class BrowserAutomation:
    """Playwright-based browser automation for website testing."""

    def __init__(self, settings):
        self.settings = settings
        self.screenshots_dir = Path(settings.sandbox.projects_dir).expanduser().parent / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self._playwright = None
        self._browser = None

    def _ensure_browser(self):
        """Initialize Playwright browser lazily."""
        if self._browser is None:
            try:
                from playwright.sync_api import sync_playwright
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(
                    headless=self.settings.browser.headless
                )
            except ImportError:
                console.print("[red]❌ Playwright not installed: pip install playwright && playwright install[/red]")
                raise
            except Exception as e:
                console.print(f"[red]❌ Browser launch failed: {e}[/red]")
                raise

    def capture_screenshots(self, project_name: str, url: str,
                            mobile: bool = False) -> List[str]:
        """Capture screenshots at multiple viewports."""
        self._ensure_browser()
        project_dir = self.screenshots_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        viewports = [
            {"name": "desktop", "width": self.settings.browser.viewport_width,
             "height": self.settings.browser.viewport_height},
        ]

        if mobile:
            viewports.append(
                {"name": "mobile", "width": self.settings.browser.mobile_viewport_width,
                 "height": self.settings.browser.mobile_viewport_height}
            )
            viewports.append(
                {"name": "tablet", "width": self.settings.browser.tablet_viewport_width,
                 "height": self.settings.browser.tablet_viewport_height}
            )

        paths = []
        for vp in viewports:
            try:
                page = self._browser.new_page(
                    viewport={"width": vp["width"], "height": vp["height"]}
                )
                page.goto(url, wait_until="networkidle",
                         timeout=self.settings.browser.timeout)
                time.sleep(1)  # Wait for animations

                screenshot_path = project_dir / f"{vp['name']}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                paths.append(str(screenshot_path))
                console.print(f"  📸 {vp['name']}: {screenshot_path}")

                page.close()
            except Exception as e:
                console.print(f"[yellow]⚠️ Screenshot {vp['name']} failed: {e}[/yellow]")

        return paths

    def test_website(self, url: str) -> Dict:
        """Run comprehensive tests on a website."""
        self._ensure_browser()
        results = {
            "url": url,
            "navigation": False,
            "console_errors": [],
            "links_tested": 0,
            "forms_found": 0,
            "accessibility_issues": [],
        }

        try:
            page = self._browser.new_page(
                viewport={"width": self.settings.browser.viewport_width,
                          "height": self.settings.browser.viewport_height}
            )

            # Capture console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text)
                    if msg.type == "error" else None)

            # Navigate
            response = page.goto(url, wait_until="networkidle",
                                timeout=self.settings.browser.timeout)
            results["navigation"] = response is not None and response.ok
            time.sleep(2)

            # Check console errors
            results["console_errors"] = console_errors

            # Test links
            links = page.query_selector_all("a[href]")
            results["links_tested"] = len(links)

            # Test forms
            forms = page.query_selector_all("form")
            results["forms_found"] = len(forms)

            # Basic accessibility checks
            issues = self._check_accessibility(page)
            results["accessibility_issues"] = issues

            page.close()

        except Exception as e:
            console.print(f"[yellow]⚠️ Test error: {e}[/yellow]")
            results["error"] = str(e)

        return results

    def test_responsiveness(self, url: str) -> List[Dict]:
        """Test responsiveness across multiple viewports."""
        self._ensure_browser()
        breakpoints = [
            {"name": "mobile-sm", "width": 320, "height": 568},
            {"name": "mobile", "width": 375, "height": 812},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "laptop", "width": 1280, "height": 720},
            {"name": "desktop", "width": 1920, "height": 1080},
        ]

        results = []
        for bp in breakpoints:
            try:
                page = self._browser.new_page(
                    viewport={"width": bp["width"], "height": bp["height"]}
                )
                page.goto(url, wait_until="networkidle",
                         timeout=self.settings.browser.timeout)
                time.sleep(1)

                # Check for horizontal overflow
                has_overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
                )

                results.append({
                    "viewport": bp["name"],
                    "width": bp["width"],
                    "has_overflow": has_overflow,
                    "status": "pass" if not has_overflow else "fail",
                })

                page.close()
            except Exception as e:
                results.append({"viewport": bp["name"], "error": str(e)})

        return results

    def inspect_console(self, url: str) -> List[str]:
        """Capture all console output from a page."""
        self._ensure_browser()
        messages = []

        try:
            page = self._browser.new_page()
            page.on("console", lambda msg: messages.append(
                f"[{msg.type}] {msg.text}"))
            page.goto(url, wait_until="networkidle",
                     timeout=self.settings.browser.timeout)
            time.sleep(2)
            page.close()
        except Exception as e:
            messages.append(f"[error] {e}")

        return messages

    def _check_accessibility(self, page) -> List[str]:
        """Run basic accessibility checks."""
        issues = []

        # Check for images without alt text
        try:
            imgs_no_alt = page.evaluate("""
                () => Array.from(document.querySelectorAll('img'))
                    .filter(img => !img.alt || img.alt.trim() === '')
                    .length
            """)
            if imgs_no_alt > 0:
                issues.append(f"{imgs_no_alt} images missing alt text")
        except Exception:
            pass

        # Check for form inputs without labels
        try:
            inputs_no_label = page.evaluate("""
                () => Array.from(document.querySelectorAll('input, select, textarea'))
                    .filter(el => {
                        const id = el.id;
                        if (!id) return true;
                        return !document.querySelector(`label[for="${id}"]`);
                    }).length
            """)
            if inputs_no_label > 0:
                issues.append(f"{inputs_no_label} form inputs missing labels")
        except Exception:
            pass

        # Check heading hierarchy
        try:
            h1_count = page.evaluate("() => document.querySelectorAll('h1').length")
            if h1_count == 0:
                issues.append("No h1 element found")
            elif h1_count > 1:
                issues.append(f"Multiple h1 elements found ({h1_count})")
        except Exception:
            pass

        return issues

    def close(self):
        """Clean up browser resources."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
