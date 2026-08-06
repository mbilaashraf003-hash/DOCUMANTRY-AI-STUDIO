import sys
import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import QApplication
from main import MainWindow
from ui.project_dialogs import NewProjectDialog
from PySide6.QtWidgets import QFileDialog

def test_persistence_workflow():
    app = QApplication(sys.argv)
    
    # 1. Start App 1
    window1 = MainWindow()
    
    # Mock New Project Dialog
    def mock_exec_new(self):
        self.project_name = "PersistenceTest"
        self.project_location = str(Path(__file__).parent / "persistence_output")
        Path(self.project_location).mkdir(exist_ok=True)
        return True
    NewProjectDialog.exec = mock_exec_new
    
    # 2. New Project
    window1.new_project()
    proj_dir = Path(__file__).parent / "persistence_output" / "PersistenceTest"
    
    # Create 5 dummy images
    images = []
    for i in range(5):
        img_path = Path(__file__).parent / f"dummy_{i}.png"
        img_path.write_text(f"fake image {i}")
        images.append(img_path)
    
    # 3. Import 5 images
    for img in images:
        window1.asset_manager.import_asset(str(img))
    
    # Verify they were imported into SQLite
    assets1 = window1.asset_manager.get_all_assets()
    assert len(assets1) == 5, "Images not imported correctly"
    
    # 4. Save Project
    # Mock QMessageBox to prevent blocking
    from PySide6.QtWidgets import QMessageBox
    original_info = QMessageBox.information
    QMessageBox.information = lambda parent, title, msg: None
    
    window1.save_project()
    
    # 5. Close Application (simulate by deleting window1)
    del window1
    
    # 6. Reopen Application
    window2 = MainWindow()
    
    # Mock Open Project Dialog
    def mock_getExistingDirectory(*args, **kwargs):
        return str(proj_dir)
    QFileDialog.getExistingDirectory = mock_getExistingDirectory
    
    # 7. Open Project
    window2.open_project()
    
    # 8. Verify all images restored correctly
    assets2 = window2.asset_manager.get_all_assets()
    assert len(assets2) == 5, "Assets were not restored correctly from DB!"
    
    # Verify project.json contains the registered assets
    import json
    with open(proj_dir / "project.json", "r") as f:
        data = json.load(f)
        assert len(data.get("asset_paths", {}).get("images", [])) == 5, "Assets not registered in project.json!"
    
    print("Persistence workflow tests passed successfully!")
    
    # Cleanup dummies
    for img in images:
        img.unlink()

if __name__ == "__main__":
    test_persistence_workflow()
