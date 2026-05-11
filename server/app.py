"""
Roobie Web Server — Main Application
FastAPI app serving web UI + REST API + WebSocket for real-time events.
"""

import os
import sys
import json
import asyncio
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.chat_engine import ChatEngine
from tools.file_tools import FileTools
from tools.terminal_tools import TerminalTools
from tools.search_tools import SearchTools

# ── Config ──────────────────────────────────────────────
WORKSPACE_DIR = os.environ.get("ROOBIE_WORKSPACE", os.path.expanduser("~/.roobie/workspace"))
OLLAMA_HOST = os.environ.get("ROOBIE_OLLAMA_HOST", "http://localhost:11434")
MODEL = os.environ.get("ROOBIE_MODEL", "qwen2.5-coder:3b")
PORT = int(os.environ.get("ROOBIE_PORT", "8484"))

# Ensure workspace exists
Path(WORKSPACE_DIR).mkdir(parents=True, exist_ok=True)

# ── App ─────────────────────────────────────────────────
app = FastAPI(title="Roobie", description="Autonomous AI Coding Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── State ───────────────────────────────────────────────
chat_engine = ChatEngine(WORKSPACE_DIR, OLLAMA_HOST, MODEL)
file_tools = FileTools(WORKSPACE_DIR)
terminal_tools = TerminalTools(WORKSPACE_DIR)
search_tools = SearchTools()

# Connected WebSocket clients
ws_clients: List[WebSocket] = []


async def broadcast_event(event_type: str, data: dict):
    """Broadcast an event to all connected WebSocket clients."""
    message = json.dumps({"type": event_type, "data": data})
    disconnected = []
    for ws in ws_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in ws_clients:
            ws_clients.remove(ws)


def sync_broadcast(event_type: str, data: dict):
    """Thread-safe broadcast for use from sync code."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_event(event_type, data))
        else:
            loop.run_until_complete(broadcast_event(event_type, data))
    except RuntimeError:
        pass  # No event loop available


# ── Request Models ──────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None

class FileCreateRequest(BaseModel):
    path: str
    content: str

class FileEditRequest(BaseModel):
    path: str
    old_content: str
    new_content: str

class CommandRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    timeout: Optional[int] = 60

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 8


# ── Static Files (Web UI) ──────────────────────────────
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main web UI."""
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse("<h1>Roobie</h1><p>Web UI not found. Run from project root.</p>")


# Mount static files
if os.path.exists(WEB_DIR):
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


# ── WebSocket ───────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket for real-time event streaming."""
    await ws.accept()
    ws_clients.append(ws)

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "chat":
                # Process chat in a background thread to not block
                user_msg = msg.get("message", "")
                model = msg.get("model")

                if model and model != chat_engine.model:
                    chat_engine.model = model

                def process_chat():
                    def event_callback(event_type, event_data):
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            # Use thread-safe approach
                            pass
                        except Exception:
                            pass
                        # Store events to send
                        events_queue.append({"type": event_type, "data": event_data})

                    events_queue = []
                    chat_engine.set_event_callback(event_callback)
                    response = chat_engine.chat(user_msg)
                    events_queue.append({
                        "type": "chat_complete",
                        "data": {"response": response}
                    })
                    return events_queue

                # Run in thread pool
                loop = asyncio.get_event_loop()
                events = await loop.run_in_executor(None, process_chat)

                # Send all events
                for event in events:
                    await ws.send_text(json.dumps(event))

            elif msg.get("type") == "get_tree":
                tree = file_tools.get_tree(".", max_depth=4)
                await ws.send_text(json.dumps({"type": "file_tree", "data": tree}))

            elif msg.get("type") == "read_file":
                result = file_tools.read_file(msg.get("path", ""))
                await ws.send_text(json.dumps({"type": "file_content", "data": result}))

    except WebSocketDisconnect:
        if ws in ws_clients:
            ws_clients.remove(ws)
    except Exception as e:
        if ws in ws_clients:
            ws_clients.remove(ws)


# ── REST API: Chat ──────────────────────────────────────

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """Send a chat message and get a response (non-streaming)."""
    if req.model:
        chat_engine.model = req.model

    events = []
    def collect_events(event_type, data):
        events.append({"type": event_type, "data": data})

    chat_engine.set_event_callback(collect_events)

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, chat_engine.chat, req.message)

    return {"response": response, "events": events}


@app.delete("/api/chat/history")
async def clear_chat():
    """Clear chat history."""
    chat_engine.clear_history()
    return {"success": True}


# ── REST API: Files ─────────────────────────────────────

@app.get("/api/files/tree")
async def get_file_tree():
    """Get workspace file tree."""
    return file_tools.get_tree(".", max_depth=4)


@app.get("/api/files/read")
async def read_file(path: str):
    """Read a file."""
    return file_tools.read_file(path)


@app.post("/api/files/create")
async def create_file(req: FileCreateRequest):
    """Create a file."""
    result = file_tools.create_file(req.path, req.content)
    return result


@app.put("/api/files/edit")
async def edit_file(req: FileEditRequest):
    """Edit a file."""
    return file_tools.edit_file(req.path, req.old_content, req.new_content)


@app.delete("/api/files/delete")
async def delete_file(path: str):
    """Delete a file."""
    return file_tools.delete_file(path)


@app.get("/api/files/list")
async def list_directory(path: str = "."):
    """List directory contents."""
    return file_tools.list_directory(path)


# ── REST API: Terminal ──────────────────────────────────

@app.post("/api/terminal/run")
async def run_command(req: CommandRequest):
    """Run a shell command."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: terminal_tools.run_command(req.command, req.cwd, req.timeout)
    )
    return result


# ── REST API: Search ────────────────────────────────────

@app.post("/api/search")
async def web_search(req: SearchRequest):
    """Search the web."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: search_tools.web_search(req.query, req.max_results)
    )
    return result


# ── REST API: Status ────────────────────────────────────

@app.get("/api/status")
async def get_status():
    """Get system status."""
    import shutil

    ollama_ok = False
    models = []
    try:
        import requests as req
        r = req.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if r.status_code == 200:
            ollama_ok = True
            models = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass

    return {
        "status": "running",
        "workspace": WORKSPACE_DIR,
        "ollama": {
            "host": OLLAMA_HOST,
            "connected": ollama_ok,
            "models": models,
        },
        "current_model": chat_engine.model,
        "node_available": shutil.which("node") is not None,
        "python_available": shutil.which("python3") is not None or shutil.which("python") is not None,
    }


@app.post("/api/model")
async def set_model(model: str):
    """Change the active model."""
    chat_engine.model = model
    return {"success": True, "model": model}


# ── Run ─────────────────────────────────────────────────

def start_server(host: str = "0.0.0.0", port: int = None):
    """Start the Roobie web server."""
    import uvicorn
    port = port or PORT
    print(f"\n🤖 Roobie is running at http://localhost:{port}")
    print(f"📁 Workspace: {WORKSPACE_DIR}")
    print(f"🧠 Model: {MODEL}")
    print(f"🔗 Ollama: {OLLAMA_HOST}\n")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_server()
