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
        
        for element in ["Background", "Text", "Subtext"]:
            row_layout = QHBoxLayout()
            label = QLabel(f"{element} Color:")
            row_layout.addWidget(label)
            
            button = QPushButton()
            button.setFixedSize(50, 25)
            button.setStyleSheet("border: 2px dashed white;")  # Add white dashed border
            button.clicked.connect(lambda _, e=element: self.pick_color(e))
            row_layout.addWidget(button)
            
            self.color_buttons[element.lower()] = button
            layout.addLayout(row_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_colors)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def pick_color(self, element):
        color = QColorDialog.getColor()
        if color.isValid():
            button = self.color_buttons[element.lower()]
            button.setStyleSheet(f"background-color: {color.name()}; border: 2px dashed white;")  # Keep the white dashed border

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
            elif element == "subtext":
                stylesheet += f"QLabel#subtextLabel {{ color: {color} !important; }}\n"

        # Add fixed style for buttons
        stylesheet += """
        QPushButton {
            background-color: #F0F0F0;
            border: 1px solid #CCCCCC;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #E0E0E0;
        }
        QPushButton:pressed {
            background-color: #D0D0D0;
        }
        """

        user_colors_path = os.path.join(os.path.dirname(__file__), "user_colors.qss")
        with open(user_colors_path, "w") as f:
            f.write(stylesheet)
        
        self.accept()

    def load_colors(self):
        settings = QSettings("YourCompany", "TodoApp")
        for element, button in self.color_buttons.items():
            color = settings.value(f"{element}_color", "#FFFFFF")
            button.setStyleSheet(f"background-color: {color}; border: 2px dashed white;")  # Keep the white dashed border