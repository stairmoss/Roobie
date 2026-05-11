"""
Roobie Paths Module
Manages all filesystem paths used by Roobie.
"""

from pathlib import Path


class RoobiePaths:
    """Centralized path management for Roobie."""
    
    def __init__(self, base_dir: str = "~/.roobie"):
        self.base = Path(base_dir).expanduser()
    
    @property
    def config_file(self) -> Path:
        return self.base / "config.json"
    
    @property
    def memory_db(self) -> Path:
        return self.base / "memory.db"
    
    @property
    def chroma_dir(self) -> Path:
        return self.base / "chroma"
    
    @property
    def models_dir(self) -> Path:
        return self.base / "models"
    
    @property
    def logs_dir(self) -> Path:
        return self.base / "logs"
    
    @property
    def projects_dir(self) -> Path:
        return self.base / "projects"
    
    @property
    def screenshots_dir(self) -> Path:
        return self.base / "screenshots"
    
    @property
    def skills_cache_dir(self) -> Path:
        return self.base / "skills_cache"
    
    @property
    def research_cache_dir(self) -> Path:
        return self.base / "research_cache"
    
    def ensure_dirs(self):
        """Create all required directories."""
        dirs = [
            self.base,
            self.models_dir,
            self.logs_dir,
            self.projects_dir,
            self.screenshots_dir,
            self.skills_cache_dir,
            self.research_cache_dir,
            self.chroma_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def project_dir(self, name: str) -> Path:
        """Get path for a specific project."""
        return self.projects_dir / name
    
    def screenshot_path(self, project: str, name: str) -> Path:
        """Get path for a screenshot."""
        project_dir = self.screenshots_dir / project
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir / f"{name}.png"
    
    def log_file(self, name: str) -> Path:
        """Get path for a log file."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        return self.logs_dir / f"{name}.log"
