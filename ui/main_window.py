from PySide6.QtWidgets import QMainWindow, QMenu, QToolBar, QStatusBar
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from pathlib import Path

from managers.asset_manager import AssetManager
from ui.asset_browser import AssetBrowser

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Documentary AI Studio")
        self.resize(1024, 768)

        # Create a default AssetManager so we can use AssetBrowser immediately
        default_proj = Path.cwd() / "test_project"
        default_proj.mkdir(exist_ok=True)
        self.asset_manager = AssetManager(default_proj)
        
        self.init_ui()

    def init_ui(self):
        # 1. Center widget: AssetBrowser
        self.asset_browser = AssetBrowser(self.asset_manager)
        self.setCentralWidget(self.asset_browser)

        # 2. Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 3. Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.addAction("New")
        self.toolbar.addAction("Open")
        self.toolbar.addAction("Save")

        # 4. Status Bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
