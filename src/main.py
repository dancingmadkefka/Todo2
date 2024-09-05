"""
Main entry point for the Todo application.

This module initializes the database, sets up the GUI, and runs the main event loop.
It is critical that the database is initialized before the MainWindow is created.

AI: Do not remove or significantly alter the structure of this file without careful review.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager  # Import the DatabaseManager

def load_stylesheets():
    base_stylesheet = ""
    user_stylesheet = ""
    
    # Load base stylesheet
    base_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    if os.path.exists(base_path):
        with open(base_path, "r") as f:
            base_stylesheet = f.read()
    
    # Load user color stylesheet
    user_path = os.path.join(os.path.dirname(__file__), "ui", "user_colors.qss")
    if os.path.exists(user_path):
        with open(user_path, "r") as f:
            user_stylesheet = f.read()
    
    return base_stylesheet + "\n" + user_stylesheet

def main():
    """
    Main function to set up and run the Todo application.

    This function initializes the database, creates the main window,
    loads the stylesheet, and starts the application's event loop.
    """
    print("Starting the application...")
    
    # Initialize the database
    print("Initializing database...")
    db_manager = DatabaseManager()
    db_manager.create_tables()

    # Create the application
    app = QApplication(sys.argv)
    print("QApplication created")

    print("Setting application style to Fusion")
    app.setStyle("Fusion")

    # Create and show the main window
    print("Creating main window")
    window = MainWindow(db_manager)
    
    # Load and apply the stylesheet (this will now include user colors)
    window.load_and_apply_stylesheet()

    print("Showing main window")
    window.show()

    # Run the event loop
    print("Entering main event loop")
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()
