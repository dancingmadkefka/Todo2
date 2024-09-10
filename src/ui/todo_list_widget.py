from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal
from .task_widget import TaskWidget

class TodoListWidget(QScrollArea):
    taskChanged = Signal(object)
    taskDeleted = Signal(int)
    taskEdited = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        content_widget = QWidget()
        self.setWidget(content_widget)
        self.layout = QVBoxLayout(content_widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setAlignment(Qt.AlignTop)

    def add_task(self, task):
        task_widget = TaskWidget(task)
        task_widget.taskChanged.connect(self.on_task_changed)
        task_widget.taskDeleted.connect(self.on_task_deleted)
        task_widget.taskEdited.connect(self.on_task_edited)
        
        # Apply the current stylesheet to the new TaskWidget
        task_widget.setStyleSheet(self.styleSheet())
        
        self.layout.addWidget(task_widget)

        # Add a horizontal line after the task widget
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #CCCCCC;")
        self.layout.addWidget(line)

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

    def update_layout(self):
        # Remove the last line if it exists
        if self.layout.count() > 0:
            last_item = self.layout.itemAt(self.layout.count() - 1)
            if isinstance(last_item.widget(), QFrame):
                last_item.widget().deleteLater()
                self.layout.takeAt(self.layout.count() - 1)

    def add_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)
        self.update_layout()