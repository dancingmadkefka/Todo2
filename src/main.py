import sys
import os
import logging
# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory (project root) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Python path:", sys.path)
print("Current working directory:", os.getcwd())

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager

try:
    import resources_rc
    print("resources_rc imported successfully")
    resources_rc.qInitResources()
except ImportError as e:
    print(f"Failed to import resources_rc: {e}")
    print(f"Looked in these locations: {sys.path}")

def load_stylesheets():
    base_stylesheet = ""
    user_stylesheet = ""
    
    base_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    if os.path.exists(base_path):
        with open(base_path, "r") as f:
            base_stylesheet = f.read()
    
    user_path = os.path.join(os.path.dirname(__file__), "ui", "user_colors.qss")
    if os.path.exists(user_path):
        with open(user_path, "r") as f:
            user_stylesheet = f.read()
    
    return base_stylesheet + "\n" + user_stylesheet

def main():
    logging.info("Starting the application...")
    
    logging.info("Initializing database...")
    db_manager = DatabaseManager()
    db_manager.create_tables()

    app = QApplication(sys.argv)
    logging.info("QApplication created")

    logging.info("Setting application style to Fusion")
    app.setStyle("Fusion")

    logging.info("Setting application icon")
    icon_path = os.path.join(os.path.dirname(__file__), "ui", "icons", "app_icon.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)

    logging.info("Loading stylesheets")
    stylesheet = load_stylesheets()

    logging.info("Creating main window")
    window = MainWindow(db_manager)
    window.setStyleSheet(stylesheet)

    logging.info("Showing main window")
    window.show()

    logging.info("Entering main event loop")
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()