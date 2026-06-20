"""
Roobie Chat Engine
Agentic loop: user message → LLM → tool calls → execute → results → LLM → repeat.
Primary: AirLLM (disk-offloaded, 4GB RAM). Fallback: Ollama.
"""

import json
import re
import requests
from typing import Dict, List, Optional, Callable
from tools import TOOL_DEFINITIONS
from agent.tool_executor import ToolExecutor


SYSTEM_PROMPT = """You are Roobie — an autonomous, local-first AI software engineering agent that runs entirely inside the terminal.

You are NOT a chatbot. You are NOT an assistant that gives instructions. You are a fully autonomous agent that DOES the work — plans, codes, executes, tests, debugs, and ships — without asking for permission or confirmation at each step.

Think of yourself as a senior full





















-stack engineer. When given a task, you think it through, build it, run it, test it, fix issues, and only stop when the job is actually done.

IDENTITY & CORE BEHAVIOR:
- You are autonomous. Do NOT ask "should I proceed?" — just do it.
- ALWAYS use tools to perform actions. NEVER write code blocks for the user to copy-paste.
- You work iteratively: plan → build → test → fix → ship.
- Stop ONLY when the task is fully complete and verified.
- Narrate your progress with [Roobie] prefix log lines.

AVAILABLE TOOLS:

- think          {"thought": "your detailed reasoning"}
                 Use BEFORE complex decisions and DURING debugging.

- create_file    {"path": "file/path.ext", "content": "full content"}
                 Always write COMPLETE content. No truncation. No placeholders.

- edit_file      {"path": "...", "old_content": "exact text", "new_content": "replacement"}

- read_file      {"path": "file/path.ext"}

- delete_file    {"path": "file/path.ext"}

- list_directory {"path": "."}

- create_folder  {"path": "dir/path"}

- run_command    {"command": "shell command"}
                 Always use python3 (never python). Use npx for scaffolding.
                 Add -y/--yes flags. If a command FAILS, try a DIFFERENT approach.

- web_search     {"query": "search query"}

HOW TO CALL TOOLS — MANDATORY FORMAT:

EVERY tool call MUST be wrapped in <tool_call> tags. No exceptions.

<tool_call>
{"name": "tool_name", "params": {"key": "value"}}
</tool_call>

Multiple tool calls per response is fine. Execute in logical order.

AUTONOMOUS AGENT WORKFLOW:

1. UNDERSTAND  → think: analyze request, task type, tech stack, risks
2. PLAN        → think: step-by-step plan, full file structure, command order
3. BUILD       → create_folder + create_file (complete, zero placeholders)
4. EXECUTE     → run_command: install deps, start servers, run builds
5. TEST        → verify outputs, check for errors, confirm functionality
6. DEBUG       → think → read_file → edit_file → re-run (never same failing approach)
7. IMPROVE     → UI/UX, responsiveness, performance polish
8. FINALIZE    → confirm end-to-end working, print summary block

TECHNOLOGY DEFAULTS:
Frontend:  Next.js 14+ App Router, TailwindCSS, TypeScript, Lucide React, Framer Motion
Backend:   FastAPI, Uvicorn, SQLite (local-first)
Shell:     python3, npx, always -y/--yes, non-interactive mode

LOW-RAM RULES (4-8GB RAM, CPU only):
- AirLLM layer-wise loading — never full model into RAM
- SQLite over Postgres, Vite over Webpack, FastAPI over Django
- No Docker on low-end machines

CODE QUALITY:
- COMPLETE files only. No "// add logic here". No TODOs. No stubs.
- Proper error handling: try/catch, HTTP status codes, graceful failures.
- TypeScript for all Next.js. Semantic HTML. ARIA labels.
- Never hardcode secrets — use .env files. Always add .gitignore.

TERMINAL OUTPUT FORMAT:
Narrate every step with [Roobie] prefix:
[Roobie] Understanding request...
[Roobie] Planning architecture...
[Roobie] Installing dependencies...
[Roobie] Starting dev server on http://localhost:3000
[Roobie] Detected issue: nav links not visible on mobile
[Roobie] Fixing responsive layout...
[Roobie] All checks passed. Project ready.

End every completed task with:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ROOBIE — TASK COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project:   <name>
URL:       http://localhost:<port>
Files:     <N> files created
Notes:     <brief notes>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ERROR RECOVERY:
Command fails → think through root cause → try a DIFFERENT approach:
- Missing package: install it, retry
- Port conflict: use different port
- Wrong path: read_file to verify, then fix
- After 3 different approaches fail: log it clearly, continue with rest of task

NEVER DO THESE:
❌ Ask "Should I proceed?" — just do it
❌ Write code blocks for the user to copy-paste
❌ Use placeholders like "// add logic here" or "TODO"
❌ Leave files incomplete or partially written
❌ Retry the exact same failing command
❌ Use python instead of python3
❌ Call cloud APIs (OpenAI, Anthropic, Google) — offline only
❌ Write the final summary before the task is actually done"""

# Valid tool names for detection
VALID_TOOLS = {"think", "create_file", "edit_file", "read_file", "delete_file",
               "list_directory", "create_folder", "run_command", "web_search"}


class ChatEngine:
    """Agentic chat engine with tool-calling loop."""

    def __init__(self, workspace_dir: str, model: str = "deepseek-ai/deepseek-coder-1.3b-instruct"):
        self.workspace_dir = workspace_dir
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
        """Check if AI is available."""
        return True

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
                error_msg = "⚠️ No response from AI model. Ensure AirLLM is installed (`pip install airllm transformers torch`)."
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
        """Generate text using AirLLM disk-offloaded inference."""
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages[-20:]
        return self._airllm_generate(full_messages)

    def _airllm_generate(self, full_messages: List[Dict]) -> str:
        """Generate text using AirLLM disk-offloaded inference."""
        if not hasattr(self, "_airllm_model"):
            self._emit("assistant_message", {"content": f"⏳ Loading AirLLM model {self.model} (first run takes a minute)...\n", "partial": True})
            try:
                from airllm import AutoModel
                from transformers import AutoTokenizer
                self._airllm_model = AutoModel.from_pretrained(
                    self.model,
                    compression="4bit",
                    profiling_mode=False
                )
                self._airllm_tokenizer = AutoTokenizer.from_pretrained(self.model)
                self._emit("assistant_message", {"content": "✅ AirLLM model loaded.\n", "partial": True})
            except ImportError as e:
                msg = (
                    f"⚠️ could not import required packages for local inference: {e}\n"
                    f"to fix this, please run: pip install airllm transformers torch"
                )
                self._emit("error", {"message": msg})
                return ""
            except Exception as e:
                msg = (
                    f"⚠️ failed to load the model: {e}\n"
                    f"please check your internet connection, disk space, and ram capacity."
                )
                self._emit("error", {"message": msg})
                return ""

        # Build prompt using chat template if available
        try:
            prompt = self._airllm_tokenizer.apply_chat_template(
                full_messages,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception:
            # Fallback manual prompt construction
            prompt = ""
            for m in full_messages:
                role, content = m["role"], m["content"]
                if role == "system":
                    prompt += f"{content}\n\n"
                elif role == "user":
                    prompt += f"### Instruction:\n{content}\n\n"
                elif role == "assistant":
                    prompt += f"### Response:\n{content}\n\n"
            prompt += "### Response:\n"

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

        if calls:
            return calls

        # Method 5: Markdown file and command blocks fallback
        # If the model outputs ```bash ... ``` or ```sh ... ```
        bash_pattern = re.compile(r'```(?:bash|sh)\n(.*?)\n```', re.DOTALL | re.IGNORECASE)
        for match in bash_pattern.finditer(response):
            cmd = match.group(1).strip()
            if cmd:
                calls.append({"name": "run_command", "params": {"command": cmd}})

        # If the model outputs a file codeblock (e.g. ```python ... ```) with a filename nearby
        file_block_pattern = re.compile(r'(?:create|edit|write|update|file|path).*?`([^`]+\.[a-z]+)`.*?\n?```[a-z]*\n(.*?)\n```', re.IGNORECASE | re.DOTALL)
        for match in file_block_pattern.finditer(response):
            path = match.group(1).strip()
            content = match.group(2)
            calls.append({"name": "create_file", "params": {"path": path, "content": content}})
            
        if not calls:
            # Fallback looking for `# path: filename.ext` inside a block
            code_block_pattern = re.compile(r'```[a-z]*\n(.*?)\n```', re.DOTALL)
            for match in code_block_pattern.finditer(response):
                content = match.group(1)
                first_line = content.split('\n')[0].strip()
                path_match = re.search(r'(?:#|//|<!--)\s*(?:path|file|filename):\s*([/\w\.-]+)', first_line, re.IGNORECASE)
                if path_match:
                    path = path_match.group(1).strip()
                    calls.append({"name": "create_file", "params": {"path": path, "content": content}})

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
            matches = re.findall(r'"([^"]*)"', response)
            if matches:
                cmd = matches[1] if len(matches) > 1 and matches[0] in ("command", "cmd") else matches[0]
                params["command"] = cmd
        if tool_name == "web_search":
            matches = re.findall(r'"([^"]*)"', response)
            if matches:
                query = matches[1] if len(matches) > 1 and matches[0] == "query" else matches[0]
                params["query"] = query
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
