import pytest
from agent.chat_engine import ChatEngine

def test_extract_tool_calls_explicit():
    engine = ChatEngine("/tmp/roobie_test", model="mock-model")
    
    response = """<tool_call>
{"name": "think", "params": {"thought": "analyzing workspace"}}
</tool_call>"""
    calls = engine._extract_tool_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "think"
    assert calls[0]["params"]["thought"] == "analyzing workspace"

def test_extract_tool_calls_json_block():
    engine = ChatEngine("/tmp/roobie_test", model="mock-model")
    
    response = """```json
{
  "name": "run_command",
  "params": {
    "command": "npm run dev"
  }
}
```"""
    calls = engine._extract_tool_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "run_command"
    assert calls[0]["params"]["command"] == "npm run dev"

def test_extract_tool_calls_bash_fallback():
    engine = ChatEngine("/tmp/roobie_test", model="mock-model")
    
    response = "I will start the server now.\n```bash\npython3 main.py run\n```"
    calls = engine._extract_tool_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "run_command"
    assert calls[0]["params"]["command"] == "python3 main.py run"

def test_extract_tool_calls_file_fallback():
    engine = ChatEngine("/tmp/roobie_test", model="mock-model")
    
    response = "Let's write a file named `hello.py` with this content:\n```python\nprint(\"hello world\")\n```"
    calls = engine._extract_tool_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "create_file"
    assert calls[0]["params"]["path"] == "hello.py"
    assert "print(\"hello world\")" in calls[0]["params"]["content"]

def test_extract_text_parts():
    engine = ChatEngine("/tmp/roobie_test", model="mock-model")
    
    response = """Step 1: Planning
<tool_call>
{"name": "think", "params": {"thought": "planning"}}
</tool_call>
And step 2: execute it."""
    text = engine._extract_text_parts(response)
    assert "Step 1: Planning" in text
    assert "And step 2: execute it." in text
    assert "tool_call" not in text

def test_clean_tool_blocks():
    from cli.app import _clean_tool_blocks
    response = """some user content
<tool_call>
{"name": "think", "params": {"thought": "testing"}}
</tool_call>
more user content
```json
{
  "name": "run_command",
  "params": {"command": "echo"}
}
```
final content"""
    cleaned = _clean_tool_blocks(response)
    assert "some user content" in cleaned
    assert "more user content" in cleaned
    assert "final content" in cleaned
    assert "tool_call" not in cleaned
    assert "run_command" not in cleaned

def test_extract_tool_calls_fuzzy():
    engine = ChatEngine("/tmp/roobie_test", model="mock-model")
    response = '{"name": "run_command", "params": {"command": "echo hello"}}'
    calls = engine._extract_tool_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "run_command"
    assert calls[0]["params"]["command"] == "echo hello"

def test_extract_tool_calls_natural_intent():
    engine = ChatEngine("/tmp/roobie_test", model="mock-model")
    response = 'I will run the command run_command("command"="npm run test") now.'
    calls = engine._extract_tool_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "run_command"
    assert calls[0]["params"]["command"] == "npm run test"
