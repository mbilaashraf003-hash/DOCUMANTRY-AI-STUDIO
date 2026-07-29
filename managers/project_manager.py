import json
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from core.logger import get_logger
from core.exceptions import (
    ProjectNotFoundError, 
    InvalidProjectError, 
    CorruptedProjectFileError,
    ProjectPermissionError
)
from models.project import ProjectMetadata
from core.database import DatabaseManager

logger = get_logger(__name__)

class ProjectManager:
    """Manages the lifecycle of Documentary AI Studio projects."""
    
    REQUIRED_FOLDERS = [
        "Images",
        "PNG",
        "Audio",
        "Music",
        "Subtitle",
        "Cache",
        "Export",
        "Temp"
    ]
    
    PROJECT_FILE_NAME = "project.json"

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_project_path: Optional[Path] = None
        self.metadata: Optional[ProjectMetadata] = None

    def create_project(self, name: str, location: Path) -> None:
        """Creates a new project structure and metadata."""
        logger.info(f"Creating new project '{name}' at {location}")
        
        project_dir = location / name
        
        try:
            # Create root directory
            project_dir.mkdir(parents=True, exist_ok=False)
            
            # Create subfolders
            for folder in self.REQUIRED_FOLDERS:
                (project_dir / folder).mkdir(exist_ok=True)
                
            # Initialize metadata
            self.metadata = ProjectMetadata(name=name)
            self.current_project_path = project_dir
            
            # Save project to disk
            self.save_project()
            
            # Add to recent projects
            self.db_manager.add_recent_project(
                self.metadata.id, 
                self.metadata.name, 
                str(self.current_project_path)
            )
            
            logger.info("Project created successfully.")
            
        except FileExistsError:
            logger.error(f"Project directory already exists: {project_dir}")
            raise ProjectPermissionError(f"Directory {project_dir} already exists.")
        except PermissionError as e:
            logger.error(f"Permission denied creating project at {location}: {e}")
            raise ProjectPermissionError(f"Permission denied: {e}")
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            # Cleanup if partially created
            if project_dir.exists():
                shutil.rmtree(project_dir, ignore_errors=True)
            raise

    def open_project(self, project_path: Path) -> None:
        """Opens an existing project."""
        logger.info(f"Opening project at {project_path}")
        
        if not project_path.exists() or not project_path.is_dir():
            raise ProjectNotFoundError(f"Project directory not found: {project_path}")
            
        project_file = project_path / self.PROJECT_FILE_NAME
        
        if not project_file.exists():
            raise InvalidProjectError(f"Missing {self.PROJECT_FILE_NAME} in {project_path}")
            
        # Verify required folders exist
        missing_folders = []
        for folder in self.REQUIRED_FOLDERS:
            if not (project_path / folder).exists():
                missing_folders.append(folder)
                
        if missing_folders:
            error_msg = f"Corrupted project structure. Missing folders: {', '.join(missing_folders)}"
            logger.error(error_msg)
            raise InvalidProjectError(error_msg)

        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metadata = ProjectMetadata.from_dict(data)
                
            self.current_project_path = project_path
            
            # Update recent projects
            self.db_manager.add_recent_project(
                self.metadata.id, 
                self.metadata.name, 
                str(self.current_project_path)
            )
            
            logger.info(f"Successfully opened project '{self.metadata.name}'")
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON in {project_file}: {e}")
            raise CorruptedProjectFileError(f"Failed to parse project file: {e}")
        except PermissionError as e:
            logger.error(f"Permission error opening project: {e}")
            raise ProjectPermissionError(f"Permission denied: {e}")
        except Exception as e:
            logger.error(f"Unexpected error opening project: {e}")
            raise InvalidProjectError(f"Failed to open project: {e}")

    def save_project(self) -> None:
        """Saves current project metadata to disk."""
        if not self.current_project_path or not self.metadata:
            logger.warning("No active project to save.")
            return
            
        logger.info(f"Saving project '{self.metadata.name}'")
        self.metadata.update_modified()
        
        project_file = self.current_project_path / self.PROJECT_FILE_NAME
        
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata.to_dict(), f, indent=4)
            logger.info("Project saved successfully.")
        except PermissionError as e:
            logger.error(f"Permission error saving project: {e}")
            raise ProjectPermissionError(f"Permission denied saving project: {e}")
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            raise CorruptedProjectFileError(f"Failed to save project file: {e}")

    def get_recent_projects(self) -> List[Dict[str, str]]:
        """Retrieves a list of recent projects."""
        return self.db_manager.get_recent_projects()
