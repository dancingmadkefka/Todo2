import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QColorDialog
from PySide6.QtCore import QSettings

class ColorCustomizationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Colors")
        self.setup_ui()
        self.load_colors()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.color_buttons = {}
        
        for element in ["Background", "Task", "Text", "Button", "ScrollArea"]:
            button = QPushButton(f"Change {element} Color")
            button.clicked.connect(lambda _, e=element: self.pick_color(e))
            layout.addWidget(button)
            self.color_buttons[element.lower()] = button
        
        save_button = QPushButton("Save Colors")
        save_button.clicked.connect(self.save_colors)
        layout.addWidget(save_button)

    def pick_color(self, element):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_buttons[element.lower()].setStyleSheet(f"background-color: {color.name()};")

    def save_colors(self):
        settings = QSettings("YourCompany", "TodoApp")
        stylesheet = ""
        for element, button in self.color_buttons.items():
            color = button.palette().button().color().name()
            settings.setValue(f"{element}_color", color)
            
            if element == "background":
                stylesheet += f"QWidget, QMainWindow {{ background-color: {color}; }}\n"
            elif element == "text":
                stylesheet += f"QWidget {{ color: {color}; }}\n"
            elif element == "button":
                stylesheet += f"QPushButton {{ background-color: {color}; }}\n"
            elif element == "task":
                stylesheet += f"QWidget#TaskWidget {{ background-color: {color}; }}\n"
            elif element == "scrollarea":
                stylesheet += f"QScrollArea, QScrollArea > QWidget > QWidget {{ background-color: {color}; }}\n"

        # Get the absolute path to the user_colors.qss file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        user_colors_path = os.path.join(base_dir, "src", "ui", "user_colors.qss")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(user_colors_path), exist_ok=True)

        # Save the generated stylesheet
        with open(user_colors_path, "w") as f:
            f.write(stylesheet)
        self.accept()

    def load_colors(self):
        settings = QSettings("YourCompany", "TodoApp")
        for element, button in self.color_buttons.items():
            color = settings.value(f"{element}_color", "#FFFFFF")
            button.setStyleSheet(f"background-color: {color};")
