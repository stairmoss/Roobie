import os
import json
from pathlib import Path
import huggingface_hub
from safetensors import safe_open

def patch_airllm():
    utils_path = "/mnt/18A660FBA660DB30/roobie/.venv/lib/python3.12/site-packages/airllm/utils.py"
    with open(utils_path, "r") as f:
        content = f.read()

    # We need to find the part where it checks for model.safetensors.index.json
    target_str = """    else:
        safetensors_format = True
        assert os.path.exists(checkpoint_path / 'model.safetensors.index.json'), f'model.safetensors.index.json should exist.'
        with open(checkpoint_path / 'model.safetensors.index.json', 'rb') as f:
            index = json.load(f)['weight_map']"""

    replacement_str = """    else:
        safetensors_format = True
        if not os.path.exists(checkpoint_path / 'model.safetensors.index.json'):
            # It might be a single safetensors file
            if repo_id is not None:
                # Force download model.safetensors
                huggingface_hub.snapshot_download(repo_id, allow_patterns=["model.safetensors"], token=hf_token)
            
            if os.path.exists(checkpoint_path / 'model.safetensors'):
                from safetensors import safe_open
                with safe_open(checkpoint_path / 'model.safetensors', framework="pt", device="cpu") as sf:
                    index = {k: 'model.safetensors' for k in sf.keys()}
            else:
                assert False, f'model.safetensors.index.json or model.safetensors should exist.'
        else:
            with open(checkpoint_path / 'model.safetensors.index.json', 'rb') as f:
                index = json.load(f)['weight_map']"""
    
    if target_str in content:
        content = content.replace(target_str, replacement_str)
        with open(utils_path, "w") as f:
            f.write(content)
        print("Patched airllm/utils.py successfully!")
    else:
        print("Target string not found, maybe already patched?")

patch_airllm()
