import hashlib
import os
import shutil
from pathlib import Path
from typing import List, Optional
from core.logger import get_logger
from models.asset import Asset
from core.asset_database import AssetDatabase
class AssetImportError(Exception):
    pass

logger = get_logger(__name__)

class AssetManager:
    """Manages business logic for media assets."""
    
    SUPPORTED_IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.psd'}
    SUPPORTED_AUDIO_TYPES = {'.mp3', '.wav', '.aac'}
    SUPPORTED_VIDEO_TYPES = {'.mp4', '.mov', '.mkv', '.avi'}
    SUPPORTED_DOC_TYPES = {'.srt', '.txt'}

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.db = AssetDatabase(project_path / "assets.db")
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure specific asset directories exist within the project."""
        for folder in ["Images", "PNG", "Audio", "Music", "Subtitle", "Video", "Thumbnails"]:
            (self.project_path / folder).mkdir(exist_ok=True)

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _determine_type(self, file_path: Path) -> str:
        ext = file_path.suffix.lower()
        if ext in self.SUPPORTED_IMAGE_TYPES:
            return "image"
        elif ext in self.SUPPORTED_AUDIO_TYPES:
            return "audio"
        elif ext in self.SUPPORTED_VIDEO_TYPES:
            return "video"
        elif ext in self.SUPPORTED_DOC_TYPES:
            return "document"
        return "unknown"

    def _get_target_dir(self, asset_type: str) -> Path:
        if asset_type == "image":
            return self.project_path / "Images"
        elif asset_type == "audio":
            return self.project_path / "Audio"
        elif asset_type == "video":
            return self.project_path / "Video"
        elif asset_type == "document":
            return self.project_path / "Subtitle"
        return self.project_path / "Temp"

    def import_asset(self, source_path: str) -> Asset:
        """Import an asset into the project."""
        src = Path(source_path)
        if not src.exists():
            raise AssetImportError(f"File not found: {source_path}")

        file_hash = self._calculate_hash(src)
        existing_asset = self.db.get_asset_by_hash(file_hash)
        if existing_asset:
            logger.info(f"Asset already exists: {existing_asset.name}")
            return existing_asset

        asset_type = self._determine_type(src)
        if asset_type == "unknown":
            raise AssetImportError(f"Unsupported file type: {src.suffix}")

        target_dir = self._get_target_dir(asset_type)
        target_path = target_dir / src.name

        # Handle filename collisions during copy
        counter = 1
        while target_path.exists():
            target_path = target_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1

        try:
            shutil.copy2(src, target_path)
        except Exception as e:
            raise AssetImportError(f"Failed to copy file: {e}")

        # Basic metadata extraction (width/height/duration left as placeholders unless using specific libraries)
        # In a full implementation, we'd use FFprobe / PySide6 QImageReader here.
        file_size = target_path.stat().st_size
        
        # Determine relative project path
        rel_project_path = str(target_path.relative_to(self.project_path))

        asset = Asset(
            name=target_path.stem,
            type=asset_type,
            original_path=str(src),
            project_path=rel_project_path,
            hash=file_hash,
            file_size=file_size
        )

        self.db.add_asset(asset)
        logger.info(f"Successfully imported asset: {asset.name}")
        return asset

    def get_all_assets(self) -> List[Asset]:
        return self.db.get_all_assets()

    def search_assets(self, query: str) -> List[Asset]:
        return self.db.search_assets(query)

    def filter_assets(self, asset_type: str) -> List[Asset]:
        return self.db.filter_assets(asset_type)

    def rename_asset(self, asset_id: str, new_name: str) -> None:
        """Rename an asset in the database (file rename can be optional based on design)."""
        self.db.update_asset_name(asset_id, new_name)
        logger.info(f"Renamed asset {asset_id} to {new_name}")

    def delete_asset(self, asset_id: str) -> None:
        """Delete an asset from the project."""
        assets = [a for a in self.get_all_assets() if a.id == asset_id]
        if not assets:
            logger.warning(f"Asset {asset_id} not found for deletion.")
            return
            
        asset = assets[0]
        full_path = self.project_path / asset.project_path
        
        if full_path.exists():
            try:
                full_path.unlink()
            except Exception as e:
                logger.error(f"Failed to delete file {full_path}: {e}")
                
        self.db.delete_asset(asset_id)
        logger.info(f"Deleted asset {asset.name}")
