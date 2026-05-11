"""
Roobie Settings Module
Centralized configuration with environment variable support.
Optimized for 4GB RAM systems.
"""

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for AI models."""
    coding_model: str = "qwen2.5-coder:3b"
    coding_model_fallback: str = "qwen2.5-coder:3b"  # Changed to available model
    chat_model: str = "qwen2.5-coder:3b"  # Model used for interactive chat
    reasoning_model: str = "qwen2.5-coder:3b"  # Changed to available model
    vision_model: str = "qwen2.5-coder:3b"  # Changed to available model for now
    embedding_model: str = "qwen2.5-coder:3b"  # Changed to available model for now
    
    # Runtime settings
    ollama_host: str = "http://localhost:11434"
    context_length: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    stream: bool = True
    request_timeout: int = 30
    enable_ai: bool = True
    use_airllm: bool = True  # Use AirLLM for disk-offloaded inference on low-RAM systems
    airllm_model_path: Optional[str] = "garage-bAInd/Platypus2-7B"
    
    # Performance settings for 4GB RAM
    num_gpu_layers: int = 0  # CPU only by default
    num_threads: int = 4
    batch_size: int = 512
    
    # GGUF fallback paths (for llama-cpp-python)
    gguf_models_dir: str = "~/.roobie/models"
    preferred_quantization: str = "Q4_K_M"


@dataclass
class BrowserConfig:
    """Browser automation configuration."""
    browser: str = "chromium"
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    mobile_viewport_width: int = 375
    mobile_viewport_height: int = 812
    tablet_viewport_width: int = 768
    tablet_viewport_height: int = 1024
    screenshot_dir: str = "screenshots"
    timeout: int = 30000  # ms
    slow_mo: int = 0


@dataclass
class ResearchConfig:
    """Research engine configuration."""
    searxng_url: str = "http://localhost:8080"
    crawl4ai_enabled: bool = True
    max_search_results: int = 10
    max_crawl_depth: int = 2
    max_pages_per_site: int = 5
    research_timeout: int = 60  # seconds


@dataclass
class SEOConfig:
    """SEO optimization configuration."""
    target_performance: int = 95
    target_accessibility: int = 95
    target_seo: int = 95
    target_best_practices: int = 95
    generate_sitemap: bool = True
    generate_robots: bool = True
    generate_schema: bool = True
    generate_opengraph: bool = True
    generate_twitter_cards: bool = True


@dataclass 
class MemoryConfig:
    """Memory system configuration."""
    sqlite_db: str = "~/.roobie/memory.db"
    chroma_persist_dir: str = "~/.roobie/chroma"
    max_context_items: int = 20
    embedding_dim: int = 768


@dataclass
class SandboxConfig:
    """Sandbox / project generation configuration."""
    projects_dir: str = "~/.roobie/projects"
    default_port: int = 3000
    dev_server_timeout: int = 60  # seconds
    auto_open_browser: bool = True


@dataclass
class Settings:
    """Master settings for Roobie."""
    # Sub-configurations
    models: ModelConfig = field(default_factory=ModelConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)
    seo: SEOConfig = field(default_factory=SEOConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    
    # Global settings
    debug: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    log_dir: str = "~/.roobie/logs"
    max_improvement_loops: int = 5
    auto_research: bool = True
    auto_improve: bool = True
    
    @classmethod
    def from_file(cls, path: str) -> "Settings":
        """Load settings from a JSON file."""
        config_path = Path(path).expanduser()
        if config_path.exists():
            with open(config_path, "r") as f:
                data = json.load(f)
            return cls._from_dict(data)
        return cls()
    
    @classmethod
    def _from_dict(cls, data: dict) -> "Settings":
        """Create Settings from a dictionary."""
        settings = cls()
        if "models" in data:
            for k, v in data["models"].items():
                if hasattr(settings.models, k):
                    setattr(settings.models, k, v)
        if "browser" in data:
            for k, v in data["browser"].items():
                if hasattr(settings.browser, k):
                    setattr(settings.browser, k, v)
        if "research" in data:
            for k, v in data["research"].items():
                if hasattr(settings.research, k):
                    setattr(settings.research, k, v)
        if "seo" in data:
            for k, v in data["seo"].items():
                if hasattr(settings.seo, k):
                    setattr(settings.seo, k, v)
        if "memory" in data:
            for k, v in data["memory"].items():
                if hasattr(settings.memory, k):
                    setattr(settings.memory, k, v)
        if "sandbox" in data:
            for k, v in data["sandbox"].items():
                if hasattr(settings.sandbox, k):
                    setattr(settings.sandbox, k, v)
        # Global settings
        for key in ["debug", "verbose", "log_level", "log_dir",
                     "max_improvement_loops", "auto_research", "auto_improve"]:
            if key in data:
                setattr(settings, key, data[key])
        return settings
    
    def to_dict(self) -> dict:
        """Serialize settings to dictionary."""
        import dataclasses
        return dataclasses.asdict(self)
    
    def save(self, path: str):
        """Save settings to JSON file."""
        config_path = Path(path).expanduser()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def apply_env_overrides(self):
        """Apply environment variable overrides."""
        env_map = {
            "ROOBIE_OLLAMA_HOST": ("models", "ollama_host"),
            "ROOBIE_CODING_MODEL": ("models", "coding_model"),
            "ROOBIE_REASONING_MODEL": ("models", "reasoning_model"),
            "ROOBIE_VISION_MODEL": ("models", "vision_model"),
            "ROOBIE_SEARXNG_URL": ("research", "searxng_url"),
            "ROOBIE_ENABLE_AI": ("models", "enable_ai"),
            "ROOBIE_USE_AIRLLM": ("models", "use_airllm"),
            "ROOBIE_AIRLLM_MODEL_PATH": ("models", "airllm_model_path"),
            "ROOBIE_DEBUG": ("", "debug"),
            "ROOBIE_VERBOSE": ("", "verbose"),
            "ROOBIE_LOG_LEVEL": ("", "log_level"),
        }
        for env_key, (section, attr) in env_map.items():
            value = os.environ.get(env_key)
            if value is not None:
                if section:
                    target = getattr(self, section)
                    current = getattr(target, attr)
                    if isinstance(current, bool):
                        setattr(target, attr, value.lower() in ("true", "1", "yes"))
                    elif isinstance(current, int):
                        setattr(target, attr, int(value))
                    else:
                        setattr(target, attr, value)
                else:
                    current = getattr(self, attr)
                    if isinstance(current, bool):
                        setattr(self, attr, value.lower() in ("true", "1", "yes"))
                    elif isinstance(current, int):
                        setattr(self, attr, int(value))
                    else:
                        setattr(self, attr, value)


# Singleton
_settings: Optional[Settings] = None


def get_settings(config_path: str = "~/.roobie/config.json") -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.from_file(config_path)
        _settings.apply_env_overrides()
    return _settings


def reset_settings():
    """Reset settings singleton (useful for testing)."""
    global _settings
    _settings = None
