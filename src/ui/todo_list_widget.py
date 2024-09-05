from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PySide6.QtCore import Signal, Slot
from ui.task_widget import TaskWidget
from models.task import Task

class TodoListWidget(QScrollArea):
    task_updated = Signal(Task)
    task_deleted = Signal(int)

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        content_widget = QWidget()
        self.setWidget(content_widget)
        self.layout = QVBoxLayout(content_widget)
        self.layout.addStretch(1)

        # Remove any inline styles
        self.setStyleSheet("")
        content_widget.setStyleSheet("")

    def add_task(self, task):
        task_widget = TaskWidget(task)
        task_widget.taskChanged.connect(self.on_task_changed)
        task_widget.taskDeleted.connect(self.on_task_deleted)
        task_widget.taskEdited.connect(self.on_edit_requested)  # Change this line
        self.layout.insertWidget(self.layout.count() - 1, task_widget)
        return task_widget  # Return the created widget

    def clear(self):
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @Slot(Task)
    def on_task_changed(self, task):
        self.task_updated.emit(task)

    @Slot(int)
    def on_task_deleted(self, task_id):
        self.task_deleted.emit(task_id)
        for i in range(self.layout.count() - 1):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, TaskWidget) and widget.task.id == task_id:
                self.layout.removeWidget(widget)
                widget.deleteLater()
                break

    @Slot(Task)
    def on_edit_requested(self, task):
        self.parent().edit_task(task)

    def update_task(self, updated_task):
        for i in range(self.layout.count() - 1):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, TaskWidget) and widget.task.id == updated_task.id:
                widget.update_task(updated_task)
                break

    def apply_filter_and_sort(self, filter_category, sort_criteria):
        tasks = self.db_manager.get_tasks(filter_category, sort_criteria)
        self.clear()
        for task in tasks:
            self.add_task(task)

