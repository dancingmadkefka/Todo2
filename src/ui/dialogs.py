from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QComboBox, QLabel, QDialogButtonBox,
                               QListWidget, QPushButton, QInputDialog, QMessageBox,
                               QCalendarWidget)
from PySide6.QtCore import QDate, Qt
from datetime import datetime

class TaskEditDialog(QDialog):
    def __init__(self, task, categories, parent=None, date_format="%Y-%m-%d"):
        super().__init__(parent)
        self.task = task
        self.categories = categories
        self.date_format = date_format
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Edit Task")
        layout = QVBoxLayout(self)

        self.title_input = QLineEdit(self.task.title)
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setCurrentText(self.task.priority)
        layout.addWidget(QLabel("Priority:"))
        layout.addWidget(self.priority_combo)

        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        self.category_combo.setCurrentText(self.task.category)
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_combo)

        self.due_date_button = QPushButton()
        self.due_date_button.clicked.connect(self.show_calendar)
        layout.addWidget(QLabel("Due Date:"))
        layout.addWidget(self.due_date_button)

        self.calendar_widget = QCalendarWidget(self)
        self.calendar_widget.setWindowFlags(Qt.Popup)
        self.calendar_widget.activated.connect(self.on_date_selected)
        self.calendar_widget.hide()

        if self.task.due_date:
            self.set_date(QDate.fromString(self.task.due_date, "yyyy-MM-dd"))
        else:
            self.set_date(QDate.currentDate())

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def show_calendar(self):
        button_pos = self.due_date_button.mapToGlobal(self.due_date_button.rect().bottomLeft())
        self.calendar_widget.move(button_pos)
        self.calendar_widget.show()

    def on_date_selected(self, date):
        self.calendar_widget.hide()
        self.set_date(date)

    def set_date(self, date):
        formatted_date = date.toString("yyyy-MM-dd")
        displayed_date = datetime.strptime(formatted_date, "%Y-%m-%d").strftime(self.date_format)
        self.due_date_button.setText(displayed_date)
        self.due_date_button.setToolTip(f"Due: {displayed_date}")

    def get_updated_task(self):
        self.task.title = self.title_input.text()
        self.task.priority = self.priority_combo.currentText()
        self.task.category = self.category_combo.currentText()
        # Convert the displayed date back to yyyy-MM-dd format for storage
        displayed_date = self.due_date_button.text()
        try:
            parsed_date = datetime.strptime(displayed_date, self.date_format)
            self.task.due_date = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing fails, keep the original date
            pass
        return self.task

class CategoryManageDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.categories = self.db_manager.get_all_categories()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Manage Categories")
        layout = QVBoxLayout(self)

        self.category_list = QListWidget()
        self.category_list.addItems(self.categories)
        layout.addWidget(self.category_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Category")
        self.add_button.clicked.connect(self.add_category)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Category")
        self.remove_button.clicked.connect(self.remove_category)
        button_layout.addWidget(self.remove_button)

        layout.addLayout(button_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def add_category(self):
        category, ok = QInputDialog.getText(self, "Add Category", "Enter new category name:")
        if ok and category:
            if category not in self.categories:
                self.db_manager.add_category(category)
                self.category_list.addItem(category)
                self.categories.append(category)
            else:
                QMessageBox.warning(self, "Warning", "Category already exists.")

    def remove_category(self):
        current_item = self.category_list.currentItem()
        if current_item:
            category = current_item.text()
            reply = QMessageBox.question(self, "Confirm Deletion",
                                         f"Are you sure you want to delete '{category}'?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db_manager.delete_category(category)
                self.category_list.takeItem(self.category_list.row(current_item))
                self.categories.remove(category)
        else:
            QMessageBox.warning(self, "Warning", "Please select a category to delete.")