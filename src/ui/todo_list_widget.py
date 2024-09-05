from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt, Signal
from .task_widget import TaskWidget

class TodoListWidget(QScrollArea):
    taskChanged = Signal(object)  # Changed to match the old signal name
    taskDeleted = Signal(int)
    taskEdited = Signal(object)  # Added to match the old signal structure

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        content_widget = QWidget()
        self.setWidget(content_widget)
        self.layout = QVBoxLayout(content_widget)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setAlignment(Qt.AlignTop)

    def add_task(self, task):
        task_widget = TaskWidget(task)
        task_widget.taskChanged.connect(self.on_task_changed)
        task_widget.taskDeleted.connect(self.on_task_deleted)
        task_widget.taskEdited.connect(self.on_task_edited)
        self.layout.addWidget(task_widget)
        return task_widget

    def clear(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_task_changed(self, task):
        self.taskChanged.emit(task)

    def on_task_deleted(self, task_id):
        self.taskDeleted.emit(task_id)

    def on_task_edited(self, task):
        self.taskEdited.emit(task)