import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from main import MainWindow

def capture_screenshot():
    app = QApplication(sys.argv)
    
    # Load Theme
    theme_path = Path(__file__).parent / "ui" / "theme.qss"
    if theme_path.exists():
        app.setStyleSheet(theme_path.read_text())
        
    window = MainWindow()
    window.show()
    
    def do_grab():
        pixmap = window.grab()
        artifacts_dir = Path(r"C:\Users\pc\.gemini\antigravity\brain\0ca9b6b4-ef41-4a81-b643-5fa3f64f4082")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        save_path = artifacts_dir / "workspace_screenshot.png"
        pixmap.save(str(save_path))
        print(f"Saved screenshot to {save_path}")
        app.quit()
        
    QTimer.singleShot(2000, do_grab)
    sys.exit(app.exec())

if __name__ == "__main__":
    capture_screenshot()
