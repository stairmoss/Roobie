import os
import pytest
import tempfile
import shutil
import time
from tools.terminal_tools import TerminalTools

@pytest.fixture
def temp_workspace():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_is_dangerous(temp_workspace):
    tt = TerminalTools(temp_workspace)
    
    assert tt._is_dangerous("sudo rm -rf /") is True
    assert tt._is_dangerous("rm -rf /etc") is True
    assert tt._is_dangerous("ls -la") is False
    assert tt._is_dangerous("echo hello") is False

def test_run_command_success(temp_workspace):
    tt = TerminalTools(temp_workspace)
    
    res = tt.run_command("echo 'hello world'")
    assert res["success"] is True
    assert "hello world" in res["stdout"]
    assert res["exit_code"] == 0

def test_run_command_blocked(temp_workspace):
    tt = TerminalTools(temp_workspace)
    
    res = tt.run_command("rm -rf /")
    assert res["success"] is False
    assert "blocked" in res["error"]

def test_run_command_timeout(temp_workspace):
    tt = TerminalTools(temp_workspace)
    
    res = tt.run_command("sleep 5", timeout=1)
    assert res["success"] is False
    assert "timed out" in res["error"]

def test_background_lifecycle(temp_workspace):
    tt = TerminalTools(temp_workspace)
    
    # Start background process
    res = tt.start_background("sleep 10")
    assert res["success"] is True
    pid = res["pid"]
    
    # List background
    list_res = tt.list_background()
    assert list_res["success"] is True
    pids = [p["pid"] for p in list_res["processes"]]
    assert pid in pids
    
    # Stop background
    stop_res = tt.stop_background(pid)
    assert stop_res["success"] is True
    
    # Verify it is no longer listed as running
    list_res2 = tt.list_background()
    active_pids = [p["pid"] for p in list_res2["processes"] if "exited" not in p["status"]]
    assert pid not in active_pids
