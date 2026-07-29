import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from core.logger import get_logger
from models.asset import Asset

logger = get_logger(__name__)

class AssetDatabase:
    """Manages the SQLite database for project assets."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS assets (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        width INTEGER,
                        height INTEGER,
                        resolution TEXT,
                        duration REAL,
                        file_size INTEGER,
                        date_imported TEXT,
                        original_path TEXT,
                        project_path TEXT,
                        hash TEXT NOT NULL
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Asset database initialization failed: {e}")
            raise

    def add_asset(self, asset: Asset) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO assets (
                        id, name, type, width, height, resolution,
                        duration, file_size, date_imported,
                        original_path, project_path, hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    asset.id, asset.name, asset.type, asset.width, asset.height,
                    asset.resolution, asset.duration, asset.file_size,
                    asset.date_imported, asset.original_path, asset.project_path, asset.hash
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to add asset {asset.name}: {e}")
            raise

    def get_all_assets(self) -> List[Asset]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM assets ORDER BY date_imported DESC")
                return [Asset.from_dict(dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve assets: {e}")
            return []

    def get_asset_by_hash(self, file_hash: str) -> Optional[Asset]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM assets WHERE hash = ?", (file_hash,))
                row = cursor.fetchone()
                if row:
                    return Asset.from_dict(dict(row))
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve asset by hash: {e}")
            return None

    def update_asset_name(self, asset_id: str, new_name: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE assets SET name = ? WHERE id = ?", (new_name, asset_id))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update asset name: {e}")
            raise

    def delete_asset(self, asset_id: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to delete asset: {e}")
            raise

    def search_assets(self, query: str) -> List[Asset]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                search_term = f"%{query}%"
                cursor.execute("SELECT * FROM assets WHERE name LIKE ? ORDER BY date_imported DESC", (search_term,))
                return [Asset.from_dict(dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to search assets: {e}")
            return []

    def filter_assets(self, asset_type: str) -> List[Asset]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM assets WHERE type = ? ORDER BY date_imported DESC", (asset_type,))
                return [Asset.from_dict(dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to filter assets: {e}")
            return []
