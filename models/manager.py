"""
Roobie Model Manager
Manages AI models via AirLLM (primary), Ollama, or llama-cpp-python fallback.
Optimized for 4GB RAM / CPU-only systems.
"""

import json
import sys
import requests
from typing import List, Dict, Optional, Generator
from rich.console import Console
import os

console = Console()

# ── Patch AirLLM/Optimum compatibility with transformers 5.x ──
# optimum.bettertransformer tries to import is_tf_available which was
# removed from transformers >=5.0. We stub it so the import chain works.
try:
    import transformers.utils as _tu
    if not hasattr(_tu, "is_tf_available"):
        _tu.is_tf_available = lambda: False
except Exception:
    pass

MODEL_REGISTRY = {
    "qwen2.5-coder:3b": {"purpose": "Code generation", "size": "~2GB", "type": "coding"},
    "deepseek-coder:1.3b": {"purpose": "Lightweight code generation", "size": "~1GB", "type": "coding"},
    "deepseek-r1:1.5b": {"purpose": "Reasoning & planning", "size": "~1GB", "type": "reasoning"},
    "moondream:latest": {"purpose": "Vision / screenshot analysis", "size": "~1GB", "type": "vision"},
    "nomic-embed-text:latest": {"purpose": "Text embeddings", "size": "~300MB", "type": "embedding"},
}

AIRLLM_MODELS = {
    "garage-bAInd/Platypus2-7B": {"purpose": "General chat & coding", "size": "~4GB (4bit)", "type": "general"},
}


class ModelManager:
    """Manages AI model lifecycle and inference via AirLLM or Ollama."""
    
    def __init__(self, settings):
        self.settings = settings
        self.ollama_host = settings.models.ollama_host
        self.ai_enabled = getattr(settings.models, "enable_ai", True)
        self.use_airllm = getattr(settings.models, "use_airllm", True)
        self.airllm_model_path = getattr(settings.models, "airllm_model_path", None)
        self.airllm_model = None
        self._airllm_tokenizer = None
        
        if self.use_airllm:
            self._init_airllm()
    
    def _init_airllm(self):
        """Initialize AirLLM model with disk-offloaded inference."""
        try:
            from airllm import AutoModel
            model_path = self.airllm_model_path or "garage-bAInd/Platypus2-7B"
            console.print(f"[cyan]Loading AirLLM model: {model_path}...[/cyan]")
            self.airllm_model = AutoModel.from_pretrained(
                model_path,
                compression="4bit",
                profiling_mode=True
            )
            console.print(f"[green]✅ AirLLM model loaded: {model_path}[/green]")
        except ImportError:
            console.print("[red]AirLLM not installed. Install with: pip install airllm[/red]")
            self.use_airllm = False
        except Exception as e:
            console.print(f"[red]AirLLM loading error: {e}[/red]")
            self.use_airllm = False
    
    def _get_airllm_tokenizer(self):
        """Lazy-load the tokenizer for the AirLLM model."""
        if self._airllm_tokenizer is None:
            try:
                from transformers import AutoTokenizer
                model_path = self.airllm_model_path or "garage-bAInd/Platypus2-7B"
                self._airllm_tokenizer = AutoTokenizer.from_pretrained(model_path)
            except Exception as e:
                console.print(f"[red]Tokenizer error: {e}[/red]")
        return self._airllm_tokenizer
    
    def _airllm_generate(self, prompt: str, system: str = "", max_tokens: int = 512) -> str:
        """Generate text using AirLLM disk-offloaded inference."""
        if self.airllm_model is None:
            console.print("[yellow]⚠️ AirLLM model not loaded, falling back to Ollama[/yellow]")
            return ""
        
        try:
            tokenizer = self._get_airllm_tokenizer()
            if tokenizer is None:
                return ""
            
            # Build prompt with system context
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"
            
            # Tokenize
            input_ids = tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.settings.models.context_length
            ).input_ids
            
            # Generate
            console.print("[dim]Generating with AirLLM (disk-offloaded)...[/dim]")
            generation_output = self.airllm_model.generate(
                input_ids,
                max_new_tokens=max_tokens,
                use_cache=True,
                return_dict_in_generate=True,
            )
            
            # Decode output (skip the input tokens)
            output_ids = generation_output.sequences[0][input_ids.shape[1]:]
            response = tokenizer.decode(output_ids, skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            console.print(f"[red]AirLLM generation error: {e}[/red]")
            return ""
    
    def check_ollama(self) -> bool:
        try:
            r = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return r.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[Dict]:
        result = []
        
        # AirLLM models
        if self.use_airllm:
            airllm_status = "✅ Loaded" if self.airllm_model is not None else "❌ Not loaded"
            model_path = self.airllm_model_path or "garage-bAInd/Platypus2-7B"
            info = AIRLLM_MODELS.get(model_path, {"purpose": "General", "size": "Unknown"})
            result.append({
                "name": f"[AirLLM] {model_path}",
                "size": info["size"],
                "status": airllm_status,
                "purpose": info["purpose"],
            })
        
        # Ollama models
        installed = set()
        if self.check_ollama():
            try:
                r = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
                for m in r.json().get("models", []):
                    installed.add(m["name"])
            except Exception:
                pass
        
        for name, info in MODEL_REGISTRY.items():
            status = "✅ Installed" if name in installed else "❌ Not installed"
            result.append({"name": name, "size": info["size"],
                          "status": status, "purpose": info["purpose"]})
        return result
    
    def pull_model(self, model_name: str) -> bool:
        console.print(f"[cyan]Pulling model: {model_name}...[/cyan]")
        try:
            r = requests.post(f"{self.ollama_host}/api/pull",
                            json={"name": model_name}, stream=True, timeout=600)
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    if "status" in data:
                        console.print(f"  {data['status']}", end="\r")
            console.print(f"\n[green]✅ {model_name} pulled successfully[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to pull {model_name}: {e}[/red]")
            return False
    
    def generate(self, prompt: str, model: str = None, system: str = "",
                 temperature: float = None, max_tokens: int = None,
                 stream: bool = None) -> str:
        if not self.ai_enabled:
            console.print("[yellow]⚠️ AI generation disabled by configuration[/yellow]")
            return ""

        # AirLLM is primary
        if self.use_airllm and self.airllm_model is not None:
            result = self._airllm_generate(prompt, system, max_tokens or 512)
            if result:
                return result
            # Fall through to Ollama if AirLLM returned empty

        # Ollama fallback
        model = model or self.settings.models.coding_model
        temp = temperature if temperature is not None else self.settings.models.temperature
        tokens = max_tokens or self.settings.models.max_tokens
        do_stream = stream if stream is not None else self.settings.models.stream
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": do_stream,
            "options": {
                "temperature": temp,
                "num_predict": tokens,
                "num_ctx": self.settings.models.context_length,
            }
        }
        if system:
            payload["system"] = system
        
        try:
            timeout = getattr(self.settings.models, "request_timeout", 30)
            if do_stream:
                return self._stream_generate(payload, timeout=timeout)
            else:
                r = requests.post(f"{self.ollama_host}/api/generate",
                                json=payload, timeout=timeout)
                return r.json().get("response", "")
        except Exception as e:
            console.print(f"[red]Generation error: {e}[/red]")
            return ""
    
    def _stream_generate(self, payload: dict, timeout: int = 30) -> str:
        full_response = []
        try:
            r = requests.post(f"{self.ollama_host}/api/generate",
                            json=payload, stream=True, timeout=timeout)
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    full_response.append(chunk)
                    if chunk:
                        console.print(chunk, end="")
            console.print()
        except Exception as e:
            console.print(f"\n[red]Stream error: {e}[/red]")
        return "".join(full_response)
    
    def stream_generate(self, prompt: str, model: str = None,
                        system: str = "") -> Generator[str, None, None]:
        # AirLLM doesn't support streaming, generate full then yield
        if self.use_airllm and self.airllm_model is not None:
            result = self._airllm_generate(prompt, system)
            if result:
                # Simulate streaming by yielding word by word
                for word in result.split(" "):
                    yield word + " "
                return
        
        model = model or self.settings.models.coding_model
        payload = {
            "model": model, "prompt": prompt, "stream": True,
            "options": {"temperature": self.settings.models.temperature,
                       "num_predict": self.settings.models.max_tokens,
                       "num_ctx": self.settings.models.context_length}
        }
        if system:
            payload["system"] = system
        try:
            r = requests.post(f"{self.ollama_host}/api/generate",
                            json=payload, stream=True, timeout=300)
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk
        except Exception as e:
            yield f"\n[Error: {e}]"
    
    def chat(self, messages: List[Dict], model: str = None) -> str:
        # AirLLM: concatenate messages into a single prompt
        if self.use_airllm and self.airllm_model is not None:
            system = ""
            user_prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                elif msg["role"] == "user":
                    user_prompt = msg["content"]
            result = self._airllm_generate(user_prompt, system)
            if result:
                return result
        
        # Ollama fallback
        model = model or self.settings.models.coding_model
        payload = {
            "model": model, "messages": messages, "stream": False,
            "options": {"temperature": self.settings.models.temperature,
                       "num_predict": self.settings.models.max_tokens}
        }
        try:
            r = requests.post(f"{self.ollama_host}/api/chat",
                            json=payload, timeout=300)
            return r.json().get("message", {}).get("content", "")
        except Exception as e:
            console.print(f"[red]Chat error: {e}[/red]")
            return ""
    
    def vision_analyze(self, image_path: str, prompt: str = "Analyze this website screenshot") -> str:
        """Vision analysis — requires Ollama + vision model (AirLLM doesn't support vision)."""
        import base64
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        
        payload = {
            "model": self.settings.models.vision_model,
            "prompt": prompt, "stream": False,
            "images": [img_b64],
            "options": {"temperature": 0.3, "num_predict": 1024}
        }
        try:
            r = requests.post(f"{self.ollama_host}/api/generate",
                            json=payload, timeout=120)
            return r.json().get("response", "")
        except Exception as e:
            console.print(f"[red]Vision error: {e}[/red]")
            return ""
    
    def ensure_model(self, model_name: str) -> bool:
        if self.check_ollama():
            try:
                r = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
                installed = {m["name"] for m in r.json().get("models", [])}
                if model_name not in installed:
                    return self.pull_model(model_name)
                return True
            except Exception:
                pass
        return False
