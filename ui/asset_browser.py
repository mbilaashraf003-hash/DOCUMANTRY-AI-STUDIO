import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QLineEdit, QComboBox, 
    QMessageBox, QInputDialog, QMenu, QStackedWidget,
    QListView, QTableView
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap, QImageReader

from models.asset import Asset
from managers.asset_manager import AssetManager

class AssetBrowser(QWidget):
    """Asset Browser UI Component."""
    
    def __init__(self, asset_manager: AssetManager, parent=None):
        super().__init__(parent)
        self.manager = asset_manager
        
        self.setAcceptDrops(True)
        self.init_ui()
        self.refresh_assets()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Top Toolbar (Search, Filter, View Mode)
        toolbar_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search assets...")
        self.search_bar.textChanged.connect(self.on_search)
        toolbar_layout.addWidget(self.search_bar)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Image", "Video", "Audio", "Document"])
        self.filter_combo.currentTextChanged.connect(self.on_filter)
        toolbar_layout.addWidget(self.filter_combo)
        
        self.view_btn = QPushButton("Toggle View")
        self.view_btn.clicked.connect(self.toggle_view)
        toolbar_layout.addWidget(self.view_btn)
        
        layout.addLayout(toolbar_layout)

        # Asset List
        self.asset_list = QListWidget()
        self.asset_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.asset_list.setIconSize(QSize(100, 100))
        self.asset_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.asset_list.setSpacing(10)
        self.asset_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.asset_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.asset_list)
        
        self.current_view_mode = "grid"

    def toggle_view(self):
        if self.current_view_mode == "grid":
            self.asset_list.setViewMode(QListWidget.ViewMode.ListMode)
            self.asset_list.setIconSize(QSize(32, 32))
            self.current_view_mode = "list"
        else:
            self.asset_list.setViewMode(QListWidget.ViewMode.IconMode)
            self.asset_list.setIconSize(QSize(100, 100))
            self.current_view_mode = "grid"

    def refresh_assets(self):
        self.asset_list.clear()
        assets = self.manager.get_all_assets()
        self._populate_list(assets)

    def on_search(self, text: str):
        if not text:
            self.refresh_assets()
            return
        assets = self.manager.search_assets(text)
        self.asset_list.clear()
        self._populate_list(assets)

    def on_filter(self, text: str):
        if text == "All":
            self.refresh_assets()
            return
        assets = self.manager.filter_assets(text.lower())
        self.asset_list.clear()
        self._populate_list(assets)

    def _populate_list(self, assets: list[Asset]):
        for asset in assets:
            item = QListWidgetItem(asset.name)
            item.setData(Qt.ItemDataRole.UserRole, asset)
            
            # Generate thumbnail if image
            if asset.type == "image":
                full_path = self.manager.project_path / asset.project_path
                if full_path.exists():
                    pixmap = QPixmap(str(full_path))
                    item.setIcon(QIcon(pixmap))
            
            self.asset_list.addItem(item)

    # Drag and drop support
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                try:
                    self.manager.import_asset(file_path)
                except Exception as e:
                    QMessageBox.warning(self, "Import Error", str(e))
        self.refresh_assets()

    def show_context_menu(self, position):
        item = self.asset_list.itemAt(position)
        if not item:
            return
            
        asset = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu()
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(self.asset_list.mapToGlobal(position))
        
        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, "Rename Asset", "New Name:", text=asset.name)
            if ok and new_name:
                self.manager.rename_asset(asset.id, new_name)
                self.refresh_assets()
                
        elif action == delete_action:
            confirm = QMessageBox.question(self, "Confirm Delete", f"Delete {asset.name}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.manager.delete_asset(asset.id)
                self.refresh_assets()
