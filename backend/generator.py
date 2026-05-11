"""
Roobie Backend Generator
Generates FastAPI backends with SQLite, authentication, and modular architecture.
"""

import json
from typing import Dict, List
from rich.console import Console

console = Console()


class BackendGenerator:
    """Generates complete FastAPI backend projects."""

    def __init__(self, settings, model_manager):
        self.settings = settings
        self.model = model_manager

    def generate(self, project_type: str, features: list,
                 architecture: dict) -> Dict[str, str]:
        """Generate all backend files."""
        files = {}

        # Routes
        api_routes = architecture.get("api_routes", self._default_routes(project_type))
        for route in api_routes:
            name = route if isinstance(route, str) else route.get("name", "items")
            files[f"backend/routes/{name}.py"] = self._gen_route(name, project_type)

        # Core application
        files["backend/main.py"] = self._gen_main(api_routes)
        files["backend/config.py"] = self._gen_config()
        files["backend/database.py"] = self._gen_database()
        files["backend/routes/__init__.py"] = self._gen_routes_init(api_routes)

        # Models
        files["backend/models/base.py"] = self._gen_models_base()

        # Middleware
        files["backend/middleware/cors.py"] = self._gen_cors()

        # Requirements
        files["backend/requirements.txt"] = self._gen_requirements()

        console.print(f"[green]Generated {len(files)} backend files[/green]")
        return files

    def _gen_main(self, api_routes: List[str]) -> str:
        imports = []
        routers = []
        for route in api_routes:
            name = route if isinstance(route, str) else route.get("name", "items")
            imports.append(f"from routes.{name} import router as {name}_router")
            routers.append(f"app.include_router({name}_router)")

        imports_code = "\n".join(imports)
        router_code = "\n".join(routers)

        return f'''"""Roobie Generated FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db

{imports_code}

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Roobie API",
    description="Auto-generated API by Roobie AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

{router_code}

@app.get("/health")
async def health():
    return {{"status": "ok", "version": "1.0.0"}}
'''

    def _gen_config(self) -> str:
        return '''"""Application configuration."""
import os
from dataclasses import dataclass

@dataclass
class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

config = Config()
'''

    def _gen_database(self) -> str:
        return '''"""SQLite database setup."""
import sqlite3
from pathlib import Path

DB_PATH = Path("app.db")

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.close()
'''

    def _gen_route(self, name: str, project_type: str) -> str:
        return f'''"""Routes for {name}."""
from fastapi import APIRouter, Depends, HTTPException
from database import get_db

router = APIRouter(prefix="/{name}", tags=["{name}"])

@router.get("/")
async def list_{name}(db=Depends(get_db)):
    cursor = db.execute("SELECT * FROM {name} LIMIT 100")
    return [{"{"}dict(row){"}"} for row in cursor.fetchall()]

@router.get("/{{{name}_id}}")
async def get_{name}({name}_id: int, db=Depends(get_db)):
    cursor = db.execute("SELECT * FROM {name} WHERE id = ?", ({name}_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="{name.title()} not found")
    return dict(row)

@router.post("/")
async def create_{name}(data: dict, db=Depends(get_db)):
    # TODO: Add proper Pydantic model validation
    return {{"message": "Created", "data": data}}
'''

    def _gen_models_base(self) -> str:
        return '''"""Base model utilities."""
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class BaseModel:
    id: int = 0
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self):
        return asdict(self)
'''

    def _gen_cors(self) -> str:
        return '''"""CORS middleware configuration."""

CORS_CONFIG = {
    "allow_origins": ["http://localhost:3000", "http://localhost:3001"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
'''

    def _gen_routes_init(self, api_routes: List[str]) -> str:
        imports = []
        for route in api_routes:
            name = route if isinstance(route, str) else route.get("name", "items")
            imports.append(f"from .{name} import router")

        return "\n".join(imports) + "\n" if imports else ""

    def _gen_requirements(self) -> str:
        return '''fastapi>=0.109.0
uvicorn>=0.27.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
'''

    def _default_routes(self, project_type: str) -> list:
        route_map = {
            "saas": ["users", "subscriptions", "features"],
            "dashboard": ["analytics", "users", "settings"],
            "ecommerce": ["products", "cart", "orders", "users"],
            "blog": ["posts", "categories", "comments"],
            "agency": ["projects", "services", "contacts"],
        }
        return route_map.get(project_type, ["items"])
