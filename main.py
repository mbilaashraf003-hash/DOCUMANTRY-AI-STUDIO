import sys
import os
import traceback
from pathlib import Path

print(f"DEBUG: Python version: {sys.version}")
print(f"DEBUG: Current working directory: {os.getcwd()}")

try:
    print("DEBUG: Importing modules...")
    from PySide6.QtWidgets import QApplication, QMainWindow
    from managers.asset_manager import AssetManager
    from ui.asset_browser import AssetBrowser
    print("DEBUG: Imported modules successfully.")

    class MainWindow(QMainWindow):
        def __init__(self, asset_manager):
            super().__init__()
            self.setWindowTitle("Documentary AI Studio - Asset Manager Preview")
            self.resize(800, 600)
            self.asset_browser = AssetBrowser(asset_manager)
            self.setCentralWidget(self.asset_browser)

    def main():
        app = QApplication(sys.argv)
        print("DEBUG: QApplication created.")
        
        test_project_dir = Path(__file__).parent / "test_project"
        test_project_dir.mkdir(exist_ok=True)
        manager = AssetManager(test_project_dir)
        
        window = MainWindow(manager)
        print("DEBUG: Main window created.")
        
        window.show()
        print("DEBUG: Window shown.")
        
        print("DEBUG: Event loop started.")
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
