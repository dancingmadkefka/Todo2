import os, sys
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLineEdit, QComboBox, QDateEdit,
                               QLabel, QScrollArea, QFrame, QMessageBox,
                               QApplication)
from PySide6.QtCore import Qt, QSize, Slot, QDate, QSettings
from PySide6.QtGui import QIcon

from models.task import Task
from .todo_list_widget import TodoListWidget
from .dialogs import TaskEditDialog, CategoryManageDialog
from .color_dialog import ColorCustomizationDialog

WINDOW_TITLE = "Todo App"
INITIAL_WINDOW_SIZE = QSize(900, 700)

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.all_tasks = []
        self.categories = self.db_manager.get_all_categories()
        self.setup_ui()
        self.connect_signals()
        self.load_tasks()
        self.resize(self.restore_window_size())
        self.load_and_apply_stylesheet()

    def setup_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Input area
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task")
        input_layout.addWidget(self.task_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Med", "High"])
        input_layout.addWidget(self.priority_combo)

        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        input_layout.addWidget(self.category_combo)

        self.due_date_edit = QDateEdit()
        self.due_date_edit.setDate(QDate.currentDate())
        input_layout.addWidget(self.due_date_edit)

        self.add_button = QPushButton("Add Task")
        self.set_button_icon(self.add_button, "add")
        input_layout.addWidget(self.add_button)

        self.manage_categories_button = QPushButton("Manage Categories")
        self.set_button_icon(self.manage_categories_button, "categories")
        input_layout.addWidget(self.manage_categories_button)

        main_layout.addLayout(input_layout)

        # Filter and sort options
        filter_sort_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed"])
        filter_sort_layout.addWidget(QLabel("Filter:"))
        filter_sort_layout.addWidget(self.filter_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Due Date", "Priority", "Category"])
        filter_sort_layout.addWidget(QLabel("Sort by:"))
        filter_sort_layout.addWidget(self.sort_combo)

        main_layout.addLayout(filter_sort_layout)

        # Todo list
        self.todo_list = TodoListWidget()
        main_layout.addWidget(self.todo_list)

        # Color customization button
        customize_colors_button = QPushButton("Customize Colors")
        customize_colors_button.clicked.connect(self.open_color_dialog)
        main_layout.addWidget(customize_colors_button)

    def connect_signals(self):
        self.add_button.clicked.connect(self.add_task)
        self.manage_categories_button.clicked.connect(self.manage_categories)
        self.filter_combo.currentTextChanged.connect(self.apply_filter_and_sort)
        self.sort_combo.currentTextChanged.connect(self.apply_filter_and_sort)
        self.task_input.returnPressed.connect(self.add_task)

    def set_button_icon(self, button, icon_name):
        icon = self.load_icon(icon_name)
        if icon:
            button.setIcon(icon)

    @staticmethod
    def load_icon(icon_name):
        icon_path = os.path.join(os.path.dirname(__file__), "icons", f"{icon_name}.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                return icon
        logging.warning(f"Warning: Icon file not found or invalid: {icon_path}")
        return None

    def restore_window_size(self):
        settings = QSettings("TodoApp", "MainWindow")
        size = settings.value("size", INITIAL_WINDOW_SIZE)
        return size

    def save_window_size(self):
        settings = QSettings("TodoApp", "MainWindow")
        settings.setValue("size", self.size())

    def resizeEvent(self, event):
        self.save_window_size()
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.save_window_size()
        super().closeEvent(event)

    def load_tasks(self):
        self.all_tasks = [Task.from_dict(task_data) for task_data in self.db_manager.get_all_tasks()]
        self.apply_filter_and_sort()

    @Slot()
    def add_task(self):
        title = self.task_input.text().strip()
        if title:
            try:
                task = Task(
                    id=self.db_manager.add_task(
                        title,
                        priority=self.priority_combo.currentText(),
                        category=self.category_combo.currentText(),
                        due_date=self.due_date_edit.date().toString("yyyy-MM-dd")
                    ),
                    title=title,
                    priority=self.priority_combo.currentText(),
                    category=self.category_combo.currentText(),
                    due_date=self.due_date_edit.date().toString("yyyy-MM-dd")
                )
                self.all_tasks.append(task)
                self.task_input.clear()
                self.apply_filter_and_sort()
                self.update_categories(task.category)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add task: {str(e)}")

    @Slot(Task)
    def update_task(self, task):
        try:
            self.db_manager.update_task(
                task.id, task.title, task.completed, task.due_date, task.priority, task.category
            )
            for i, t in enumerate(self.all_tasks):
                if t.id == task.id:
                    self.all_tasks[i] = task
                    break
            self.apply_filter_and_sort()
            self.update_categories(task.category)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update task: {str(e)}")

    @Slot(int)
    def delete_task(self, task_id):
        try:
            self.db_manager.delete_task(task_id)
            self.all_tasks = [task for task in self.all_tasks if task.id != task_id]
            self.apply_filter_and_sort()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete task: {str(e)}")

    @Slot(Task)
    def edit_task(self, task):
        dialog = TaskEditDialog(task, self.categories, self)
        if dialog.exec_():
            self.update_task(dialog.get_updated_task())

    @Slot()
    def apply_filter_and_sort(self):
        filter_option = self.filter_combo.currentText()
        sort_option = self.sort_combo.currentText()

        filtered_tasks = [
            task for task in self.all_tasks
            if filter_option == "All" or
            (filter_option == "Active" and not task.completed) or
            (filter_option == "Completed" and task.completed)
        ]

        sort_key = {
            "Due Date": lambda x: x.due_date or "9999-99-99",
            "Priority": lambda x: {"High": 0, "Med": 1, "Low": 2}.get(x.priority, 3),
            "Category": lambda x: x.category.lower()
        }[sort_option]

        filtered_tasks.sort(key=sort_key)

        self.todo_list.clear()
        for task in filtered_tasks:
            task_widget = self.todo_list.add_task(task)
            task_widget.taskChanged.connect(self.update_task)
            task_widget.taskDeleted.connect(self.delete_task)
            task_widget.taskEdited.connect(self.edit_task)

    def update_categories(self, new_category):
        if new_category and new_category not in self.categories:
            self.categories.append(new_category)
            self.category_combo.addItem(new_category)
            self.db_manager.add_category(new_category)

    @Slot()
    def manage_categories(self):
        dialog = CategoryManageDialog(self.db_manager, self)
        if dialog.exec_():
            self.categories = dialog.categories
            self.category_combo.clear()
            self.category_combo.addItems(self.categories)

    def open_color_dialog(self):
        dialog = ColorCustomizationDialog(self)
        if dialog.exec_():
            self.load_and_apply_stylesheet()

    def load_and_apply_stylesheet(self):
        base_stylesheet = ""
        user_stylesheet = ""
        
        base_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(base_path):
            with open(base_path, "r") as f:
                base_stylesheet = f.read()
        
        user_path = os.path.join(os.path.dirname(__file__), "user_colors.qss")
        if os.path.exists(user_path):
            with open(user_path, "r") as f:
                user_stylesheet = f.read()
        
        combined_stylesheet = base_stylesheet + "\n" + user_stylesheet
        self.setStyleSheet(combined_stylesheet)
        for child in self.findChildren(QWidget):
            child.setStyleSheet(combined_stylesheet)