import os
import logging
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QPushButton, QToolButton
from PySide6.QtCore import Qt, Signal, Slot, QSize, QFile
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

class TaskWidget(QWidget):
    taskChanged = Signal(object)
    taskDeleted = Signal(int)
    taskEdited = Signal(object)

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.task.completed)
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        layout.addWidget(self.checkbox)

        text_layout = QVBoxLayout()
        self.title_label = QLabel(self.task.title)
        text_layout.addWidget(self.title_label)

        subtext = f"{self.task.priority} | {self.task.category or 'No Category'} | Due: {self.task.due_date or 'No Date'}"
        self.subtext_label = QLabel(subtext)
        self.subtext_label.setStyleSheet("color: gray; font-size: 10px;")
        text_layout.addWidget(self.subtext_label)

        layout.addLayout(text_layout, 1)  # Give the text layout a stretch factor

        button_layout = QHBoxLayout()
        self.edit_button = QToolButton()
        self.set_button_icon(self.edit_button, "edit")
        self.edit_button.setToolTip("Edit")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QToolButton()
        self.set_button_icon(self.delete_button, "delete")
        self.delete_button.setToolTip("Delete")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

    def set_button_icon(self, button, icon_name):
        icon = self.create_colored_icon(icon_name)
        if not icon.isNull():
            button.setIcon(icon)
            button.setIconSize(QSize(16, 16))  # Adjust size as needed
            logging.info(f"Set icon for button: {icon_name}")
        else:
            logging.warning(f"Failed to set icon for button: {icon_name}")
            button.setText(icon_name.capitalize())  # Fallback to text if icon loading fails

    def create_colored_icon(self, icon_name):
        try:
            # Try to load from resource system first
            resource_path = f":icons/src/ui/icons/{icon_name}.svg"
            logging.info(f"Attempting to load icon from resource: {resource_path}")
            
            if QFile.exists(resource_path):
                logging.info(f"Icon found in resources: {resource_path}")
                icon_path = resource_path
            else:
                logging.warning(f"Icon not found in resources: {resource_path}")
                # Fall back to file system
                file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "icons", f"{icon_name}.svg"))
                logging.info(f"Attempting to load icon from file system: {file_path}")
                if os.path.exists(file_path):
                    logging.info(f"Icon found in file system: {file_path}")
                    icon_path = file_path
                else:
                    logging.error(f"Icon not found in file system: {file_path}")
                    return QIcon()
            
            renderer = QSvgRenderer(icon_path)
            if not renderer.isValid():
                logging.error(f"SVG renderer is not valid for: {icon_path}")
                return QIcon()
            
            pixmap = QPixmap(16, 16)  # Adjust size as needed
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            icon = QIcon(pixmap)
            if icon.isNull():
                logging.error(f"Failed to create icon: {icon_path}")
                return QIcon()
            
            logging.info(f"Successfully created icon: {icon_path}")
            return icon
        except Exception as e:
            logging.error(f"Exception while loading icon {icon_name}: {str(e)}")
            return QIcon()

    @Slot(int)
    def on_checkbox_state_changed(self, state):
        self.task.completed = (state == Qt.Checked)
        self.taskChanged.emit(self.task)

    @Slot()
    def on_delete_clicked(self):
        self.taskDeleted.emit(self.task.id)

    @Slot()
    def on_edit_clicked(self):
        self.taskEdited.emit(self.task)