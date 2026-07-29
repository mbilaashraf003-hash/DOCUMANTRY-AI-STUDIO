import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

@dataclass
class ProjectMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Project"
    creation_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"
    asset_paths: Dict[str, List[str]] = field(default_factory=lambda: {
        "images": [],
        "png": [],
        "audio": [],
        "music": [],
        "subtitle": []
    })
    export_settings: Dict[str, Any] = field(default_factory=lambda: {
        "resolution": "1920x1080",
        "fps": 30,
        "format": "mp4"
    })
    timeline_settings: Dict[str, Any] = field(default_factory=lambda: {
        "duration": 0
    })

    def update_modified(self) -> None:
        self.last_modified = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'ProjectMetadata':
        return cls(**data)
