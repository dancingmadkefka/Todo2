import os, sys
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLineEdit, QComboBox, QDateEdit,
                               QLabel, QScrollArea, QFrame, QMessageBox,
                               QApplication, QStyledItemDelegate, QStyle,
                               QToolButton, QCalendarWidget)
from PySide6.QtCore import Qt, QSize, Slot, QDate, QSettings, QRect, QFile, QEvent
from PySide6.QtGui import QIcon, QPainter, QColor, QFont, QPixmap
from PySide6.QtSvg import QSvgRenderer

from models.task import Task
from .todo_list_widget import TodoListWidget
from .dialogs import TaskEditDialog, CategoryManageDialog
from .color_dialog import ColorCustomizationDialog
from .icon_utils import create_colored_icon
from .task_widget import TaskWidget

WINDOW_TITLE = "Todo App"
INITIAL_WINDOW_SIZE = QSize(900, 700)

class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(CustomItemDelegate(self))

class CustomItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.row() == 0:  # "Manage Categories" option
            painter.save()
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                painter.setPen(option.palette.highlightedText().color())
            else:
                painter.setPen(option.palette.text().color())
            
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            
            text_rect = option.rect.adjusted(5, 0, -5, 0)  # Add some padding
            painter.drawText(text_rect, Qt.AlignVCenter, "Manage Categories")
            
            painter.setPen(QColor(200, 200, 200))  # Light gray color for the line
            painter.drawLine(option.rect.left(), option.rect.bottom(),
                             option.rect.right(), option.rect.bottom())
            painter.restore()
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        if index.row() == 0:
            size.setHeight(size.height() + 5)  # Make the "Manage Categories" option slightly taller
        return size

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.all_tasks = []
        self.categories = self.db_manager.get_all_categories()
        self.setup_ui()
        self.connect_signals()
        self.load_and_apply_stylesheet()
        self.load_tasks()
        self.resize(self.restore_window_size())
        self.installEventFilter(self)

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

        self.category_combo = CustomComboBox()
        self.category_combo.addItem("Manage Categories")
        self.category_combo.addItems(self.categories)
        input_layout.addWidget(self.category_combo)

        # Create all buttons first
        self.due_date_button = QToolButton()
        self.add_button = QToolButton()

        # Now set icons for all buttons
        self.set_button_icon(self.due_date_button, "calendar")
        self.set_button_icon(self.add_button, "add")

        # Configure buttons
        self.due_date_button.setToolTip("Set due date")
        self.due_date_button.clicked.connect(self.show_date_picker)
        self.add_button.setFixedSize(32, 32)  # Increased size from 24x24 to 32x32

        # Add buttons to layout
        input_layout.addWidget(self.due_date_button)
        input_layout.addWidget(self.add_button)

        # Set transparent backgrounds for buttons
        self.due_date_button.setStyleSheet("background-color: transparent; border: none;")
        self.add_button.setStyleSheet("background-color: transparent; border: none;")

        # Create a QCalendarWidget for date picking
        self.calendar_widget = QCalendarWidget(self)
        self.calendar_widget.setWindowFlags(Qt.Popup)
        self.calendar_widget.activated.connect(self.on_date_selected)
        self.calendar_widget.hide()

        main_layout.addLayout(input_layout)

        # Create filter and sort combos
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed"])
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Due Date", "Priority", "Category"])

        # Filter and sort options
        filter_sort_layout = QHBoxLayout()
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.setSpacing(5)  # Reduce spacing between label and combo box
        filter_sort_layout.addLayout(filter_layout)
        
        filter_sort_layout.addSpacing(20)  # Add some space between filter and sort
        
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Sort by:"))
        sort_layout.addWidget(self.sort_combo)
        sort_layout.setSpacing(5)  # Reduce spacing between label and combo box
        filter_sort_layout.addLayout(sort_layout)
        
        filter_sort_layout.addStretch(1)  # Push everything to the left
        
        main_layout.addLayout(filter_sort_layout)

        # Todo list
        self.todo_list = TodoListWidget()
        main_layout.addWidget(self.todo_list)

        # Color customization button
        customize_colors_button = QPushButton("Customize Colors")
        customize_colors_button.setObjectName("customizeColorsButton")
        customize_colors_button.clicked.connect(self.open_color_dialog)
        main_layout.addWidget(customize_colors_button)

    def connect_signals(self):
        self.add_button.clicked.connect(self.add_task)
        self.category_combo.activated.connect(self.on_category_combo_changed)
        self.filter_combo.currentTextChanged.connect(self.apply_filter_and_sort)
        self.sort_combo.currentTextChanged.connect(self.apply_filter_and_sort)
        self.task_input.returnPressed.connect(self.add_task)

    def set_button_icon(self, button, icon_name):
        icon_path = f":icons/src/ui/icons/{icon_name}.svg"
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        icon = create_colored_icon(icon_path, base_color, background_color)
        if not icon.isNull():
            button.setIcon(icon)
            button.setIconSize(QSize(32, 32))
            logging.info(f"Set icon for button: {icon_name}")
        else:
            logging.warning(f"Failed to set icon for button: {icon_name}")

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
        self.calendar_widget.hide()
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
                category = self.category_combo.currentText()
                if category == "Manage Categories":
                    category = ""  # Set to empty string if "Manage Categories" is selected
                due_date_str = self.due_date_button.toolTip().split(": ")[-1]
                due_date = QDate.fromString(due_date_str, "yyyy-MM-dd") if due_date_str != "Set due date" else QDate.currentDate()
                task = Task(
                    id=self.db_manager.add_task(
                        title,
                        priority=self.priority_combo.currentText(),
                        category=category,
                        due_date=due_date.toString("yyyy-MM-dd")
                    ),
                    title=title,
                    priority=self.priority_combo.currentText(),
                    category=category,
                    due_date=due_date.toString("yyyy-MM-dd")
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
            current_index = self.category_combo.currentIndex()
            self.category_combo.clear()
            self.category_combo.addItem("Manage Categories")
            self.category_combo.addItems(self.categories)
            self.category_combo.setCurrentIndex(current_index)

    @Slot(int)
    def on_category_combo_changed(self, index):
        if self.category_combo.itemText(index) == "Manage Categories":
            self.manage_categories()
            # Reset to the previously selected category or the first category
            self.category_combo.setCurrentIndex(1 if self.category_combo.count() > 1 else 0)

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
        
        # Apply stylesheet to all existing widgets
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(combined_stylesheet)
        
        self.refresh_icons()

    def refresh_icons(self):
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        
        self.set_button_icon(self.due_date_button, "calendar")
        self.set_button_icon(self.add_button, "add")
        
        # Refresh icons for all TaskWidgets
        for task_widget in self.todo_list.findChildren(TaskWidget):
            task_widget.set_button_icon(task_widget.check_button, "check")
            task_widget.set_button_icon(task_widget.edit_button, "edit")
            task_widget.set_button_icon(task_widget.delete_button, "delete")

    def show_date_picker(self):
        button_pos = self.due_date_button.mapToGlobal(self.due_date_button.rect().bottomLeft())
        self.calendar_widget.move(button_pos)
        self.calendar_widget.show()

    def on_date_selected(self, date):
        self.calendar_widget.hide()
        self.due_date_button.setToolTip(f"Due: {date.toString('yyyy-MM-dd')}")

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.PaletteChange:
            self.refresh_icons()
        return super().eventFilter(obj, event)