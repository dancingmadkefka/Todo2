import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("todo_app.log"),
                        logging.StreamHandler()
                    ])

# Add the parent directory (project root) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.debug("Python path: %s", sys.path)
logging.debug("Current working directory: %s", os.getcwd())

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager

try:
    import resources_rc
    logging.debug("resources_rc imported successfully")
    resources_rc.qInitResources()
except ImportError as e:
    logging.error(f"Failed to import resources_rc: {e}")
    logging.error(f"Looked in these locations: {sys.path}")

def load_stylesheets():
    base_stylesheet = ""
    user_stylesheet = ""
    
    base_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    if os.path.exists(base_path):
        with open(base_path, "r") as f:
            base_stylesheet = f.read()
        logging.debug("Base stylesheet loaded")
    else:
        logging.warning("Base stylesheet not found")
    
    user_path = os.path.join(os.path.dirname(__file__), "ui", "user_colors.qss")
    if os.path.exists(user_path):
        with open(user_path, "r") as f:
            user_stylesheet = f.read()
        logging.debug("User stylesheet loaded")
    else:
        logging.debug("User stylesheet not found")
    
    return base_stylesheet + "\n" + user_stylesheet

def main():
    logging.info("Starting the application...")
    
    logging.info("Initializing database...")
    db_manager = DatabaseManager()
    db_manager.create_tables()

    # Initialize date format if it doesn't exist
    if not db_manager.get_date_format():
        logging.info("Initializing default date format...")
        db_manager.set_date_format("%Y-%m-%d")

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