import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QColorDialog, QDialogButtonBox)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor

class ColorCustomizationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Colors")
        self.color_buttons = {}
        self.setup_ui()
        self.load_colors()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        for element in ["Background", "Text", "Button", "Task", "Completed Task"]:
            row_layout = QHBoxLayout()
            label = QLabel(f"{element} Color:")
            row_layout.addWidget(label)
            
            button = QPushButton()
            button.setFixedSize(50, 25)
            button.clicked.connect(lambda _, e=element: self.pick_color(e))
            row_layout.addWidget(button)
            
            self.color_buttons[element.lower().replace(" ", "_")] = button
            layout.addLayout(row_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_colors)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def pick_color(self, element):
        color = QColorDialog.getColor()
        if color.isValid():
            button = self.color_buttons[element.lower().replace(" ", "_")]
            button.setStyleSheet(f"background-color: {color.name()};")

    def save_colors(self):
        settings = QSettings("YourCompany", "TodoApp")
        stylesheet = ""
        
        for element, button in self.color_buttons.items():
            color = button.palette().button().color().name()
            settings.setValue(f"{element}_color", color)
            
            if element == "background":
                stylesheet += f"QWidget {{ background-color: {color}; }}\n"
            elif element == "text":
                stylesheet += f"QWidget {{ color: {color}; }}\n"
            elif element == "button":
                stylesheet += f"QPushButton {{ background-color: {color}; }}\n"
            elif element == "task":
                stylesheet += f"QWidget#TaskWidget {{ background-color: {color}; }}\n"
            elif element == "completed_task":
                stylesheet += f"QWidget#TaskWidget[completed=\"true\"] {{ background-color: {color}; }}\n"

        user_colors_path = os.path.join(os.path.dirname(__file__), "user_colors.qss")
        with open(user_colors_path, "w") as f:
            f.write(stylesheet)
        
        self.accept()

    def load_colors(self):
        settings = QSettings("YourCompany", "TodoApp")
        for element, button in self.color_buttons.items():
            color = settings.value(f"{element}_color", "#FFFFFF")
            button.setStyleSheet(f"background-color: {color};")