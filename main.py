import sys
import os
import traceback
import shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QMenu
from PySide6.QtGui import QAction

from managers.project_manager import ProjectManager
from managers.asset_manager import AssetManager
from ui.asset_browser import AssetBrowser
from ui.project_dialogs import NewProjectDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Documentary AI Studio")
        self.resize(1024, 768)
        
        self.project_manager = ProjectManager()
        self.asset_manager = None
        self.asset_browser = None
        
        self.init_menu()
        
    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        self.save_action = QAction("Save Project", self)
        self.save_action.triggered.connect(self.save_project)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)
        
        self.save_as_action = QAction("Save As", self)
        self.save_as_action.triggered.connect(self.save_as_project)
        self.save_as_action.setEnabled(False)
        file_menu.addAction(self.save_as_action)
        
        self.recent_menu = file_menu.addMenu("Recent Projects")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def update_recent_menu(self):
        self.recent_menu.clear()
        try:
            recent_projects = self.project_manager.get_recent_projects()
            if not recent_projects:
                empty_action = QAction("No recent projects", self)
                empty_action.setEnabled(False)
                self.recent_menu.addAction(empty_action)
            else:
                for proj in recent_projects:
                    # Using default arguments in lambda to avoid late-binding loop issues
                    action = QAction(f"{proj['name']} ({proj['path']})", self)
                    action.triggered.connect(lambda checked=False, p=proj['path']: self.load_project(Path(p)))
                    self.recent_menu.addAction(action)
        except Exception as e:
            print(f"Failed to update recent menu: {e}")

    def new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec():
            name = dialog.project_name
            location = Path(dialog.project_location)
            try:
                self.project_manager.create_project(name, location)
                # Create the extra "Video" directory that ProjectManager misses
                (location / name / "Video").mkdir(exist_ok=True)
                
                self.load_project(location / name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project:\n{e}")

    def open_project(self):
        directory = QFileDialog.getExistingDirectory(self, "Open Project")
        if directory:
            self.load_project(Path(directory))

    def load_project(self, path: Path):
        try:
            self.project_manager.open_project(path)
            # Reinitialize asset manager for this project
            self.asset_manager = AssetManager(path)
            
            # Setup AssetBrowser to restore/show assets
            self.asset_browser = AssetBrowser(self.asset_manager)
            self.setCentralWidget(self.asset_browser)
            
            self.setWindowTitle(f"Documentary AI Studio - {self.project_manager.metadata.name}")
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.update_recent_menu()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open project:\n{e}")
            traceback.print_exc()

    def save_project(self):
        if self.project_manager.current_project_path:
            try:
                self.project_manager.save_project()
                QMessageBox.information(self, "Success", "Project saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project:\n{e}")

    def save_as_project(self):
        if not self.project_manager.current_project_path:
            return
            
        new_location = QFileDialog.getExistingDirectory(self, "Select New Location")
        if not new_location:
            return
            
        new_path = Path(new_location) / self.project_manager.metadata.name
        
        if new_path.exists():
            QMessageBox.warning(self, "Error", "Target directory already exists!")
            return
            
        try:
            # Copy everything to new path
            shutil.copytree(self.project_manager.current_project_path, new_path)
            # Open the newly copied project
            self.load_project(new_path)
            QMessageBox.information(self, "Success", "Project saved as new copy.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save as:\n{e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
