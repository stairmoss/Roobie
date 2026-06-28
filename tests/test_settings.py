import os
import pytest
from pathlib import Path
from config.settings import Settings, get_settings, reset_settings

def test_settings_default():
    settings = Settings()
    assert settings.debug is False
    assert settings.models.use_airllm is True
    assert settings.models.ollama_host == "http://localhost:11434"

def test_settings_save_and_load(tmp_path):
    settings_file = tmp_path / "config.json"
    settings = Settings()
    settings.debug = True
    settings.models.ollama_host = "http://custom-ollama:11434"
    settings.save(str(settings_file))
    
    assert settings_file.exists()
    
    loaded = Settings.from_file(str(settings_file))
    assert loaded.debug is True
    assert loaded.models.ollama_host == "http://custom-ollama:11434"

def test_settings_env_override():
    settings = Settings()
    os.environ["ROOBIE_DEBUG"] = "true"
    os.environ["ROOBIE_OLLAMA_HOST"] = "http://env-ollama:11434"
    os.environ["ROOBIE_USE_AIRLLM"] = "false"
    
    try:
        settings.apply_env_overrides()
        assert settings.debug is True
        assert settings.models.ollama_host == "http://env-ollama:11434"
        assert settings.models.use_airllm is False
    finally:
        # Clean up env
        os.environ.pop("ROOBIE_DEBUG", None)
        os.environ.pop("ROOBIE_OLLAMA_HOST", None)
        os.environ.pop("ROOBIE_USE_AIRLLM", None)

def test_get_settings(tmp_path):
    settings_file = tmp_path / "config.json"
    reset_settings()
    
    s = get_settings(str(settings_file))
    assert s.debug is False
    
    # Modify singleton and fetch again
    s.debug = True
    s2 = get_settings(str(settings_file))
    assert s2.debug is True
    
    reset_settings()
