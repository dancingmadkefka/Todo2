from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from .task_widget import TaskWidget
from datetime import datetime, date
import logging

class TodoListWidget(QScrollArea):
    taskChanged = Signal(object)
    taskDeleted = Signal(list)
    taskEdited = Signal(object)
    multipleTasksSelected = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_tasks = set()
        self.setup_ui()
        self.current_sort_criteria = None

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
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
        
        task_widget.setStyleSheet(self.styleSheet())
        
        if self.current_sort_criteria:
            task_widget.update_sort_criteria_style(self.current_sort_criteria)
        
        self.tasks_layout.addWidget(task_widget)
        return task_widget

    def add_bold_separator(self, text):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("BoldTaskSeparator")
        self.tasks_layout.addWidget(separator)

        label = QLabel(text)
        label.setObjectName("GroupHeader")
        font = QFont()
        font.setBold(True)
        label.setFont(font)
        self.tasks_layout.addWidget(label)

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

    def add_tasks(self, tasks, sort_criteria=None, sort_order=Qt.AscendingOrder):
        self.clear()
        self.current_sort_criteria = sort_criteria

        if sort_criteria == "Due Date":
            self.add_tasks_grouped_by_due_date(tasks, sort_order)
        elif sort_criteria == "Priority":
            self.add_tasks_grouped_by_priority(tasks, sort_order)
        elif sort_criteria == "Category":
            self.add_tasks_grouped_by_category(tasks, sort_order)
        else:
            for task in tasks:
                self.add_task(task)


    def add_tasks_grouped_by_due_date(self, tasks, sort_order):
        grouped_tasks = {}
        for task in tasks:
            due_date = task.due_date if task.due_date else "No Due Date"
            if due_date not in grouped_tasks:
                grouped_tasks[due_date] = []
            grouped_tasks[due_date].append(task)

        sorted_dates = sorted(grouped_tasks.keys(), key=lambda x: (x == "No Due Date", x), reverse=(sort_order == Qt.DescendingOrder))

        for date in sorted_dates:
            if date == "No Due Date":
                self.add_bold_separator("No Due Date")
            else:
                self.add_bold_separator(f"Due: {date}")

            for task in grouped_tasks[date]:
                self.add_task(task)



    def add_tasks_grouped_by_priority(self, tasks, sort_order):
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        grouped_tasks = {"High": [], "Medium": [], "Low": []}

        for task in tasks:
            priority = task.priority if task.priority in priority_order else "Medium"
            grouped_tasks[priority].append(task)

        priorities = sorted(grouped_tasks.keys(), key=lambda x: priority_order[x], reverse=(sort_order == Qt.DescendingOrder))

        for priority in priorities:
            if grouped_tasks[priority]:
                self.add_bold_separator(f"Priority: {priority}")
                for task in grouped_tasks[priority]:
                    self.add_task(task)


    def add_tasks_grouped_by_category(self, tasks, sort_order):
        grouped_tasks = {}
        for task in tasks:
            category = task.category if task.category else "No Category"
            if category not in grouped_tasks:
                grouped_tasks[category] = []
            grouped_tasks[category].append(task)

        categories = sorted(grouped_tasks.keys(), reverse=(sort_order == Qt.DescendingOrder))

        for category in categories:
            self.add_bold_separator(f"Category: {category}")
            for task in grouped_tasks[category]:
                self.add_task(task)


    def set_sort_criteria(self, criteria):
        self.current_sort_criteria = criteria
        for i in range(self.tasks_layout.count()):
            widget = self.tasks_layout.itemAt(i).widget()
            if isinstance(widget, TaskWidget):
                widget.update_sort_criteria_style(criteria)