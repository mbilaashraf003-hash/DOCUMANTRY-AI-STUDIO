import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Asset:
    """Domain model representing a media asset."""
    name: str
    type: str  # 'image', 'audio', 'video', 'document'
    original_path: str
    project_path: str
    hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[str] = None
    duration: Optional[float] = None
    file_size: int = 0
    date_imported: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "width": self.width,
            "height": self.height,
            "resolution": self.resolution,
            "duration": self.duration,
            "file_size": self.file_size,
            "date_imported": self.date_imported,
            "original_path": self.original_path,
            "project_path": self.project_path,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
