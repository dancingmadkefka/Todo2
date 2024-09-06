from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

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
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

    @Slot(int)
    def on_checkbox_state_changed(self, state):  # Corrected method name
        self.task.completed = (state == Qt.Checked)
        self.taskChanged.emit(self.task)

    @Slot()
    def on_delete_clicked(self):
        self.taskDeleted.emit(self.task.id)

    @Slot()
    def on_edit_clicked(self):
        self.taskEdited.emit(self.task)