"""
Roobie Chat Engine
Agentic loop: user message → LLM → tool calls → execute → results → LLM → repeat.
Works with small local models (3B-7B params) via Ollama.
"""

import json
import re
import requests
from typing import Dict, List, Optional, Callable
from tools import TOOL_DEFINITIONS
from agent.tool_executor import ToolExecutor


# Keep the system prompt simple and explicit for small models
SYSTEM_PROMPT = """You are Roobie, an autonomous AI coding assistant. You can use tools to create files, edit files, run commands, and search the web.

AVAILABLE TOOLS:
- think: Think about the problem. Params: {"thought": "your reasoning"}
- create_file: Create a file. Params: {"path": "file/path.ext", "content": "file content"}
- edit_file: Edit a file. Params: {"path": "file/path.ext", "old_content": "text to find", "new_content": "replacement"}
- read_file: Read a file. Params: {"path": "file/path.ext"}
- delete_file: Delete a file. Params: {"path": "file/path.ext"}
- list_directory: List files. Params: {"path": "."}
- create_folder: Create directory. Params: {"path": "dir/path"}
- run_command: Run shell command. Params: {"command": "npm install"}
- web_search: Search web. Params: {"query": "search terms"}

HOW TO CALL TOOLS:
Wrap each tool call in <tool_call> tags exactly like this:

<tool_call>
{"name": "create_file", "params": {"path": "index.html", "content": "<!DOCTYPE html>\\n<html>\\n<body>Hello</body>\\n</html>"}}
</tool_call>

RULES:
1. ALWAYS wrap tool calls in <tool_call> tags. This is mandatory.
2. You can make multiple tool calls in one response.
3. Write complete file contents, never use placeholders.
4. Be autonomous - just do the work without asking permission. YOU MUST USE TOOLS to create files. DO NOT just write markdown code blocks for the user to copy-paste.
5. Use python3 (not python) for Python commands. Use npx for Node.js scaffolding.
6. If a command fails, try a different approach - do NOT retry the same command.
7. YOU MUST execute commands using `run_command` yourself. Do not tell the user to run them.
8. When done, give a final summary without any tool calls.

EXAMPLE:
User: Create a hello world page

I'll create a hello world HTML page.

<tool_call>
{"name": "create_file", "params": {"path": "index.html", "content": "<!DOCTYPE html>\\n<html lang=\\"en\\">\\n<head>\\n<meta charset=\\"UTF-8\\">\\n<title>Hello World</title>\\n</head>\\n<body>\\n<h1>Hello, World!</h1>\\n</body>\\n</html>"}}
</tool_call>

Done! I created index.html with a Hello World page."""

# Valid tool names for detection
VALID_TOOLS = {"think", "create_file", "edit_file", "read_file", "delete_file",
               "list_directory", "create_folder", "run_command", "web_search"}


class ChatEngine:
    """Agentic chat engine with tool-calling loop."""

    def __init__(self, workspace_dir: str, ollama_host: str = "http://localhost:11434",
                 model: str = "qwen2.5-coder:3b"):
        self.workspace_dir = workspace_dir
        self.ollama_host = ollama_host
        self.model = model
        self.executor = ToolExecutor(workspace_dir)
        self.conversation: List[Dict] = []
        self._event_callback: Optional[Callable] = None
        self.max_tool_loops = 8  # Max tool call rounds per message

    def set_event_callback(self, callback: Callable):
        """Set callback for streaming events to UI."""
        self._event_callback = callback
        self.executor.set_event_callback(callback)

    def _emit(self, event_type: str, data: dict):
        if self._event_callback:
            self._event_callback(event_type, data)

    def check_model(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            r = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def chat(self, user_message: str) -> str:
        """Process a user message through the agentic loop."""
        self.conversation.append({"role": "user", "content": user_message})
        self._emit("user_message", {"content": user_message})

        full_response = ""
        loop_count = 0

        while loop_count < self.max_tool_loops:
            loop_count += 1

            # Generate LLM response
            self._emit("thinking_start", {})
            response = self._generate(self.conversation)
            self._emit("thinking_end", {})

            if not response:
                error_msg = "⚠️ No response from AI model. Make sure Ollama is running (`ollama serve`) and has a model pulled (`ollama pull qwen2.5-coder:3b`)."
                self._emit("assistant_message", {"content": error_msg})
                return error_msg

            # Parse tool calls from response
            tool_calls = self._extract_tool_calls(response)

            if not tool_calls:
                # No tool calls — this is the final answer
                self.conversation.append({"role": "assistant", "content": response})
                self._emit("assistant_message", {"content": response})
                full_response = response
                break

            # Extract text parts (between tool calls) and emit them
            text_parts = self._extract_text_parts(response)
            if text_parts:
                self._emit("assistant_message", {"content": text_parts, "partial": True})

            # Execute tool calls
            tool_results = []
            for tc in tool_calls:
                self._emit("tool_call", {"name": tc["name"], "params": tc["params"]})
                result = self.executor.execute(tc["name"], tc["params"])
                tool_results.append({
                    "tool": tc["name"],
                    "params": tc["params"],
                    "result": result
                })
                self._emit("tool_result", {
                    "name": tc["name"],
                    "result": result
                })

            # Add assistant message + tool results to conversation
            self.conversation.append({"role": "assistant", "content": response})

            # Format tool results as a user message for the next round
            results_text = "Tool execution results:\n"
            for tr in tool_results:
                result_str = json.dumps(tr["result"], indent=2, default=str)
                # Truncate very long results
                if len(result_str) > 3000:
                    result_str = result_str[:3000] + "\n... (truncated)"
                results_text += f"\n[{tr['tool']}] → {result_str}\n"
            results_text += "\nContinue with the task. Use more tool calls if needed, or give a final response."

            self.conversation.append({"role": "user", "content": results_text})
            full_response += text_parts + "\n"

        return full_response

    def _generate(self, messages: List[Dict]) -> str:
        """Generate a response from AirLLM or Ollama."""
        # Build messages with system prompt
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages[-20:]  # Keep last 20 messages for context window

        if "/" in self.model or "deepseek-ai" in self.model:
            return self._airllm_generate(full_messages)
        else:
            return self._ollama_generate(full_messages)

    def _ollama_generate(self, full_messages: List[Dict]) -> str:
        """Generate via Ollama HTTP API."""
        payload = {
            "model": self.model,
            "messages": full_messages,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 4096,
                "num_ctx": 8192,
            }
        }
        try:
            r = requests.post(
                f"{self.ollama_host}/api/chat",
                json=payload,
                timeout=300
            )
            if r.status_code == 200:
                return r.json().get("message", {}).get("content", "")
            else:
                return ""
        except Exception as e:
            self._emit("error", {"message": f"Model error: {e}"})
            return ""

    def _airllm_generate(self, full_messages: List[Dict]) -> str:
        """Generate text using AirLLM disk-offloaded inference."""
        if not hasattr(self, "_airllm_model"):
            self._emit("assistant_message", {"content": f"Loading AirLLM model {self.model} (may take a minute)...\\n", "partial": True})
            try:
                from airllm import AutoModel
                from transformers import AutoTokenizer
                self._airllm_model = AutoModel.from_pretrained(
                    self.model,
                    compression="4bit",
                    profiling_mode=True
                )
                self._airllm_tokenizer = AutoTokenizer.from_pretrained(self.model)
                self._emit("assistant_message", {"content": "AirLLM model loaded.\\n", "partial": True})
            except ImportError:
                self._emit("error", {"message": "AirLLM not installed. Install with: pip install airllm"})
                return ""
            except Exception as e:
                self._emit("error", {"message": f"AirLLM loading error: {e}"})
                return ""

        # Build prompt from messages using chat template if available
        try:
            prompt = self._airllm_tokenizer.apply_chat_template(
                full_messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
        except Exception:
            # Fallback for tokenizers without chat template
            prompt = ""
            for m in full_messages:
                role = m["role"]
                content = m["content"]
                if role == "system":
                    prompt += f"{content}\\n\\n"
                elif role == "user":
                    prompt += f"### Instruction:\\n{content}\\n\\n"
                elif role == "assistant":
                    prompt += f"### Response:\\n{content}\\n\\n"
            prompt += "### Response:\\n"

        try:
            input_ids = self._airllm_tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=4096
            ).input_ids
            
            generation_output = self._airllm_model.generate(
                input_ids,
                max_new_tokens=1024,
                use_cache=True,
                return_dict_in_generate=True,
            )
            
            output_ids = generation_output.sequences[0][input_ids.shape[1]:]
            response = self._airllm_tokenizer.decode(output_ids, skip_special_tokens=True)
            return response.strip()
        except Exception as e:
            self._emit("error", {"message": f"AirLLM generation error: {e}"})
            return ""

    def _extract_tool_calls(self, response: str) -> List[Dict]:
        """Extract tool calls from the response — handles multiple formats from small models."""
        calls = []

        # Method 1: Explicit <tool_call> blocks
        pattern1 = re.compile(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', re.DOTALL)
        for match in pattern1.finditer(response):
            parsed = self._try_parse_tool_json(match.group(1))
            if parsed:
                calls.append(parsed)

        if calls:
            return calls

        # Method 2: ```json blocks containing tool calls
        pattern2 = re.compile(r'```(?:json)?\s*(\{[^`]*?"name"\s*:\s*"[^`]*?\})\s*```', re.DOTALL)
        for match in pattern2.finditer(response):
            parsed = self._try_parse_tool_json(match.group(1))
            if parsed:
                calls.append(parsed)

        if calls:
            return calls

        # Method 3: Find JSON-like objects with "name" field matching a known tool
        # This is the most forgiving approach for small models
        tool_names_pattern = '|'.join(VALID_TOOLS)
        pattern3 = re.compile(
            r'\{\s*"name"\s*:\s*"(' + tool_names_pattern + r')"\s*,\s*"params"\s*:\s*\{(.*?)\}\s*\}',
            re.DOTALL
        )
        for match in pattern3.finditer(response):
            tool_name = match.group(1)
            params_str = match.group(2)
            params = self._parse_params_fuzzy(tool_name, params_str, response)
            if params is not None:
                calls.append({"name": tool_name, "params": params})

        if calls:
            return calls

        # Method 4: Last resort — detect tool intent from natural language
        # If the model says something like: create_file with path "x" content "y"
        for tool in VALID_TOOLS:
            if tool in response and tool != "think":
                # Try to find it used as a function-like call
                func_pattern = re.compile(
                    rf'{tool}\s*[\(:\{{]\s*.*?(?:"path"|"command"|"query")\s*[=:]\s*"([^"]*)"',
                    re.DOTALL
                )
                fm = func_pattern.search(response)
                if fm:
                    calls.append(self._build_tool_from_context(tool, response))
                    break

        return calls

    def _parse_params_fuzzy(self, tool_name: str, params_str: str, full_response: str) -> Optional[Dict]:
        """Parse params from a possibly malformed JSON string."""
        # Try standard JSON parse first
        try:
            params = json.loads("{" + params_str + "}")
            return params
        except json.JSONDecodeError:
            pass

        # Fuzzy extraction based on known param patterns
        params = {}

        if tool_name == "create_file":
            # Extract path
            path_match = re.search(r'"path"\s*:\s*"([^"]*)"', params_str)
            if path_match:
                params["path"] = path_match.group(1)

            # Extract content — everything between "content": " and the closing
            content_match = re.search(r'"content"\s*:\s*"(.*)', params_str, re.DOTALL)
            if content_match:
                raw = content_match.group(1)
                # Remove trailing "} or similar
                raw = re.sub(r'"\s*$', '', raw)
                # Unescape
                raw = raw.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                params["content"] = raw
            else:
                # Try to find content between the tool call and end of response
                # Look for HTML/code content after "content":
                content_match2 = re.search(
                    r'"content"\s*:\s*["\']?(.*?)(?:["\']?\s*\}\s*\}|$)',
                    full_response[full_response.find(tool_name):],
                    re.DOTALL
                )
                if content_match2:
                    raw = content_match2.group(1).strip().strip('"\'')
                    params["content"] = raw.replace('\\n', '\n')

            if "path" in params:
                if "content" not in params:
                    params["content"] = ""
                return params

        elif tool_name in ("read_file", "delete_file", "list_directory", "create_folder"):
            path_match = re.search(r'"path"\s*:\s*"([^"]*)"', params_str)
            if path_match:
                params["path"] = path_match.group(1)
                return params

        elif tool_name == "edit_file":
            path_match = re.search(r'"path"\s*:\s*"([^"]*)"', params_str)
            old_match = re.search(r'"old_content"\s*:\s*"(.*?)"', params_str, re.DOTALL)
            new_match = re.search(r'"new_content"\s*:\s*"(.*?)"', params_str, re.DOTALL)
            if path_match:
                params["path"] = path_match.group(1)
                params["old_content"] = old_match.group(1) if old_match else ""
                params["new_content"] = new_match.group(1) if new_match else ""
                return params

        elif tool_name == "run_command":
            cmd_match = re.search(r'"command"\s*:\s*"([^"]*)"', params_str)
            if cmd_match:
                params["command"] = cmd_match.group(1)
                return params

        elif tool_name == "web_search":
            query_match = re.search(r'"query"\s*:\s*"([^"]*)"', params_str)
            if query_match:
                params["query"] = query_match.group(1)
                return params

        elif tool_name == "think":
            thought_match = re.search(r'"thought"\s*:\s*"(.*?)"', params_str, re.DOTALL)
            if thought_match:
                params["thought"] = thought_match.group(1)
                return params

        return None if not params else params

    def _build_tool_from_context(self, tool_name: str, response: str) -> Dict:
        """Build a tool call from context when no proper JSON is found."""
        params = {}
        if tool_name in ("create_file", "read_file", "delete_file", "create_folder", "list_directory"):
            path_match = re.search(r'"([^"]*\.[a-z]{2,5})"', response)
            if path_match:
                params["path"] = path_match.group(1)
        if tool_name == "run_command":
            cmd_match = re.search(r'"([^"]*)"', response)
            if cmd_match:
                params["command"] = cmd_match.group(1)
        if tool_name == "web_search":
            q_match = re.search(r'"([^"]*)"', response)
            if q_match:
                params["query"] = q_match.group(1)
        return {"name": tool_name, "params": params}

    def _try_parse_tool_json(self, text: str) -> Optional[Dict]:
        """Try to parse a JSON string as a tool call."""
        try:
            text = text.strip()
            data = json.loads(text)
            if isinstance(data, dict) and "name" in data:
                name = data["name"]
                if name in VALID_TOOLS:
                    return {
                        "name": name,
                        "params": data.get("params", data.get("parameters", {}))
                    }
        except json.JSONDecodeError:
            # Try fixing common issues
            try:
                fixed = re.sub(r'(?<!\\)\n', '\\\\n', text)
                data = json.loads(fixed)
                if isinstance(data, dict) and "name" in data and data["name"] in VALID_TOOLS:
                    return {
                        "name": data["name"],
                        "params": data.get("params", data.get("parameters", {}))
                    }
            except (json.JSONDecodeError, Exception):
                pass
        return None

    def _extract_text_parts(self, response: str) -> str:
        """Extract text parts (non-tool-call content) from response."""
        text = re.sub(r'<tool_call>.*?</tool_call>', '', response, flags=re.DOTALL)
        text = re.sub(r'```(?:json)?\s*\{[^`]*?"name"\s*:\s*"[^`]*?\}\s*```', '', text, flags=re.DOTALL)
        # Remove bare JSON tool objects
        tool_names_pattern = '|'.join(VALID_TOOLS)
        text = re.sub(
            r'\{\s*"name"\s*:\s*"(?:' + tool_names_pattern + r')".*?\}\s*\}',
            '', text, flags=re.DOTALL
        )
        return text.strip()

    def get_file_tree(self) -> Dict:
        """Get workspace file tree."""
        return self.executor.get_file_tree()

    def clear_history(self):
        """Clear conversation history."""
        self.conversation = []
        self.executor.thinking_tools.clear()
