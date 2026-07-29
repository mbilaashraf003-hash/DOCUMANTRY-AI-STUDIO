import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional
from core.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Manages the application's global SQLite database for things like recent projects."""
    def __init__(self):
        self.db_path = Path.home() / ".documentary_ai_studio" / "app.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recent_projects (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        path TEXT NOT NULL,
                        last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")

    def add_recent_project(self, project_id: str, name: str, path: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Upsert project
                cursor.execute("""
                    INSERT INTO recent_projects (id, name, path, last_opened)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(id) DO UPDATE SET 
                        name=excluded.name,
                        path=excluded.path,
                        last_opened=CURRENT_TIMESTAMP
                """, (project_id, name, str(path)))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to add recent project: {e}")

    def get_recent_projects(self, limit: int = 10) -> List[Dict[str, str]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, path, last_opened 
                    FROM recent_projects 
                    ORDER BY last_opened DESC 
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve recent projects: {e}")
            return []
