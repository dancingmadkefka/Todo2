from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

class TaskWidget(QWidget):
    taskChanged = Signal(object)
    taskDeleted = Signal(int)
    taskEdited = Signal(object)

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.task.completed)
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        layout.addWidget(self.checkbox)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        self.title_label = QLabel(self.task.title)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        info_layout.addWidget(self.title_label)

        details_label = QLabel(f"{self.task.category} | Due: {self.task.format_due_date()}")
        details_label.setFont(QFont("Segoe UI", 10))
        info_layout.addWidget(details_label)

        layout.addLayout(info_layout, 1)

        self.priority_label = QLabel(self.task.priority)
        self.priority_label.setAlignment(Qt.AlignCenter)
        self.priority_label.setProperty("class", "priority-label")
        self.priority_label.setProperty("priority", self.task.priority.lower())
        layout.addWidget(self.priority_label)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.on_edit_clicked)
        layout.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.on_delete_clicked)
        layout.addWidget(delete_button)

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