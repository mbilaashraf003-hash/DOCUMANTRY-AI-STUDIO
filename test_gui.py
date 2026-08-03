import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from main import MainWindow
from ui.project_dialogs import NewProjectDialog

def mock_exec(self):
    self.project_name = "AutomatedTestProject"
    self.project_location = str(Path(__file__).parent / "test_output")
    Path(self.project_location).mkdir(exist_ok=True)
    return True

NewProjectDialog.exec = mock_exec

app = QApplication(sys.argv)
window = MainWindow()
window.new_project()
print("Success! Central widget is now:", window.centralWidget())
