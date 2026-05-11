"""
Roobie Memory Store
SQLite-based persistent memory for projects, tasks, and conversation history.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class MemoryStore:
    """SQLite-backed persistent memory for Roobie."""
    
    def __init__(self, db_path: str = "~/.roobie/memory.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL, description TEXT,
                template TEXT, status TEXT DEFAULT 'created',
                path TEXT, config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER, type TEXT NOT NULL,
                description TEXT, status TEXT DEFAULT 'pending',
                result TEXT, metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER, role TEXT NOT NULL,
                content TEXT NOT NULL, metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS research_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL, results TEXT, source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER, path TEXT NOT NULL,
                viewport TEXT, analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER, loop_number INTEGER,
                issues_found TEXT, fixes_applied TEXT,
                score_before TEXT, score_after TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY,
                plan_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()
    
    def create_project(self, name, description="", template="nextjs", path="", config=None):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, description, template, path, config) VALUES (?, ?, ?, ?, ?)",
            (name, description, template, path, json.dumps(config or {})))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_project(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_project_status(self, name, status):
        self.conn.execute(
            "UPDATE projects SET status=?, updated_at=? WHERE name=?",
            (status, datetime.now().isoformat(), name))
        self.conn.commit()
    
    def list_projects(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def create_task(self, project_id, task_type, description="", metadata=None):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (project_id, type, description, metadata) VALUES (?, ?, ?, ?)",
            (project_id, task_type, description, json.dumps(metadata or {})))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_task(self, task_id, status, result=""):
        completed = datetime.now().isoformat() if status in ("done", "failed") else None
        self.conn.execute(
            "UPDATE tasks SET status=?, result=?, completed_at=? WHERE id=?",
            (status, result, completed, task_id))
        self.conn.commit()
    
    def add_message(self, project_id, role, content, metadata=None):
        self.conn.execute(
            "INSERT INTO conversations (project_id, role, content, metadata) VALUES (?, ?, ?, ?)",
            (project_id, role, content, json.dumps(metadata or {})))
        self.conn.commit()
    
    def get_conversation(self, project_id, limit=50):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM conversations WHERE project_id=? ORDER BY created_at DESC LIMIT ?",
            (project_id, limit))
        return list(reversed([dict(r) for r in cursor.fetchall()]))
    
    def cache_research(self, query, results, source=""):
        self.conn.execute(
            "INSERT INTO research_cache (query, results, source) VALUES (?, ?, ?)",
            (query, json.dumps(results), source))
        self.conn.commit()
    
    def get_cached_research(self, query):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT results FROM research_cache WHERE query=? ORDER BY created_at DESC LIMIT 1",
            (query,))
        row = cursor.fetchone()
        return json.loads(row["results"]) if row else None
    
    def log_screenshot(self, project_id, path, viewport="desktop", analysis=""):
        self.conn.execute(
            "INSERT INTO screenshots (project_id, path, viewport, analysis) VALUES (?, ?, ?, ?)",
            (project_id, path, viewport, analysis))
        self.conn.commit()
    
    def save_current_plan(self, plan_text: str):
        """Save the current plan for later execution."""
        self.conn.execute(
            "INSERT OR REPLACE INTO plans (id, plan_text, created_at) VALUES (?, ?, ?)",
            (1, plan_text, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_current_plan(self) -> Optional[str]:
        """Get the current saved plan."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT plan_text FROM plans WHERE id = 1")
        row = cursor.fetchone()
        return row["plan_text"] if row else None
    
    def close(self):
        self.conn.close()
