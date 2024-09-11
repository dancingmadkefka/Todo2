from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal
from .task_widget import TaskWidget

class TodoListWidget(QScrollArea):
    taskChanged = Signal(object)
    taskDeleted = Signal(list)  # Changed to emit a list of task IDs
    taskEdited = Signal(object)
    multipleTasksSelected = Signal(bool)  # New signal to indicate if multiple tasks are selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_tasks = set()  # Set to store selected task IDs
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Layout for task widgets
        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(self.tasks_layout)

    def add_task(self, task):
        task_widget = TaskWidget(task)
        task_widget.setObjectName("TaskWidget")
        task_widget.taskChanged.connect(self.on_task_changed)
        task_widget.taskDeleted.connect(self.on_task_deleted)
        task_widget.taskEdited.connect(self.on_task_edited)
        task_widget.taskSelectedForDeletion.connect(self.on_task_selected_for_deletion)
        
        # Apply the current stylesheet to the new TaskWidget
        task_widget.setStyleSheet(self.styleSheet())
        
        self.tasks_layout.addWidget(task_widget)
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("TaskSeparator")
        self.tasks_layout.addWidget(separator)
        
        return task_widget

    def clear(self):
        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.selected_tasks.clear()
        self.multipleTasksSelected.emit(False)

    def on_task_changed(self, task):
        self.taskChanged.emit(task)

    def on_task_deleted(self, task_id):
        self.taskDeleted.emit([task_id])

    def on_task_edited(self, task):
        self.taskEdited.emit(task)

    def on_task_selected_for_deletion(self, task_id, selected):
        if selected:
            self.selected_tasks.add(task_id)
        else:
            self.selected_tasks.discard(task_id)
        self.multipleTasksSelected.emit(len(self.selected_tasks) > 0)

    def add_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)