import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox
)

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.resize(400, 150)
        
        self.project_name = ""
        self.project_location = ""
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Location
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(QLabel("Location:"))
        self.loc_input = QLineEdit()
        self.loc_input.setText(os.path.expanduser("~/Documents"))
        loc_layout.addWidget(self.loc_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_location)
        loc_layout.addWidget(browse_btn)
        layout.addLayout(loc_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.accept_creation)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Location", self.loc_input.text())
        if directory:
            self.loc_input.setText(directory)

    def accept_creation(self):
        name = self.name_input.text().strip()
        location = self.loc_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Project name cannot be empty.")
            return
            
        if not os.path.exists(location):
            QMessageBox.warning(self, "Error", "Location does not exist.")
            return
            
        self.project_name = name
        self.project_location = location
        self.accept()
