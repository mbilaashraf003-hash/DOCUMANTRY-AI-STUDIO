import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from main import MainWindow
from ui.project_dialogs import NewProjectDialog

def test_integration():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Mock the New Project Dialog
    def mock_exec(self):
        self.project_name = "IntegrationTestProject"
        self.project_location = str(Path(__file__).parent / "integration_output")
        Path(self.project_location).mkdir(exist_ok=True)
        return True
    NewProjectDialog.exec = mock_exec
    
    # Trigger New Project
    window.new_project()
    
    # Check if folders are created
    proj_dir = Path(__file__).parent / "integration_output" / "IntegrationTestProject"
    folders_to_check = ["Images", "PNG", "Audio", "Video", "Music", "Subtitle", "Cache", "Export"]
    for folder in folders_to_check:
        assert (proj_dir / folder).exists(), f"Missing folder {folder}"
    assert (proj_dir / "project.json").exists(), "Missing project.json"
    
    # Check if imported assets go into the project folder
    dummy_img = Path(__file__).parent / "dummy.png"
    dummy_img.write_text("fake png")
    
    window.asset_manager.import_asset(str(dummy_img))
    
    assert (proj_dir / "Images" / "dummy.png").exists(), "Asset was not imported to active project folder"
    
    print("Integration tests passed successfully!")

if __name__ == "__main__":
    test_integration()
