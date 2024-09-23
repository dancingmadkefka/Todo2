import os, sys 
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLineEdit, QComboBox,
                               QLabel, QMessageBox,
                               QStyledItemDelegate, QStyle,
                               QToolButton, QCalendarWidget, QInputDialog)
from PySide6.QtCore import Qt, QSize, Slot, QDate, QSettings, QEvent, QTimer
from PySide6.QtGui import QIcon, QColor, QAction

from models.task import Task
from .todo_list_widget import TodoListWidget
from .dialogs import TaskEditDialog, CategoryManageDialog
from .color_dialog import ColorCustomizationDialog
from .icon_utils import create_colored_icon
from .task_widget import TaskWidget
from .icon_color_adjuster import adjust_icon_color_for_theme

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
        
        # Load date format
        self.date_format = self.db_manager.get_date_format()
        
        self.setup_ui()
        self.connect_signals()
        self.load_and_apply_stylesheet()
        self.load_tasks()
        self.resize(self.restore_window_size())
        self.installEventFilter(self)

        # Set the application icon
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "app_icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        # Initialize flash timer
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.flash_add_button)
        self.flash_state = True

    # Load date format
        self.date_format = self.db_manager.get_date_format()

    def setup_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create menu bar
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Settings')

        # Add Date Format action to the Settings menu
        date_format_action = QAction('Date Format', self)
        date_format_action.triggered.connect(self.open_date_format_settings)
        settings_menu.addAction(date_format_action)

        # Input area
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task")
        input_layout.addWidget(self.task_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])  # Changed "Med" to "Medium"
        input_layout.addWidget(self.priority_combo)

        self.category_combo = CustomComboBox()
        self.category_combo.addItem("Manage Categories")
        self.category_combo.addItems(self.categories)
        input_layout.addWidget(self.category_combo)

        self.sub_category_input = QLineEdit()
        self.sub_category_input.setPlaceholderText("Enter sub-category")
        input_layout.addWidget(self.sub_category_input)

        # Create all buttons first
        self.due_date_button = QToolButton()
        self.add_button = QToolButton()

        # Now set icons for all buttons
        self.set_button_icon(self.due_date_button, "calendar")
        self.set_button_icon(self.add_button, "add")

        # Configure buttons
        self.due_date_button.setToolTip("Set due date")
        self.due_date_button.clicked.connect(self.show_date_picker)
        self.due_date_button.setFixedSize(40, 40)
        self.add_button.setFixedSize(40, 40)

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

        # Create sort order button
        self.sort_order_button = QToolButton()
        self.sort_order_button.setArrowType(Qt.UpArrow)
        self.sort_order_button.setToolTip("Ascending Order")
        self.sort_order_button.clicked.connect(self.toggle_sort_order)

        # Add category filter combo box
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("All Categories")
        self.category_filter_combo.addItems(self.categories)

        # Filter and sort options
        filter_sort_layout = QHBoxLayout()
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.setSpacing(5)  # Reduce spacing between label and combo box
        filter_sort_layout.addLayout(filter_layout)
        
        category_filter_layout = QHBoxLayout()
        category_filter_layout.addWidget(QLabel("Category:"))
        category_filter_layout.addWidget(self.category_filter_combo)
        category_filter_layout.setSpacing(5)
        filter_sort_layout.addLayout(category_filter_layout)
        
        filter_sort_layout.addSpacing(20)  # Add some space between filter and sort
        
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Sort by:"))
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addWidget(self.sort_order_button)
        sort_layout.setSpacing(5)  # Reduce spacing between label and combo box
        filter_sort_layout.addLayout(sort_layout)
        
        filter_sort_layout.addStretch(1)  # Push everything to the left

        # Add multi-delete button and label
        self.multi_delete_layout = QHBoxLayout()
        self.multi_delete_label = QLabel("Hold Shift to delete multiple")
        self.multi_delete_button = QToolButton()
        self.set_button_icon(self.multi_delete_button, "delete")
        self.multi_delete_button.setVisible(False)
        self.multi_delete_button.clicked.connect(self.on_multi_delete_clicked)
        self.multi_delete_layout.addWidget(self.multi_delete_label)
        self.multi_delete_layout.addWidget(self.multi_delete_button)
        filter_sort_layout.addLayout(self.multi_delete_layout)
        
        main_layout.addLayout(filter_sort_layout)

        # Todo list
        self.todo_list = TodoListWidget()
        main_layout.addWidget(self.todo_list)

        # Color customization button
        self.customize_colors_button = QPushButton("Customize Colors")
        self.customize_colors_button.clicked.connect(self.open_color_dialog)
        main_layout.addWidget(self.customize_colors_button)

        # Set initial button color
        self.update_customize_colors_button()

    def connect_signals(self):
        self.add_button.clicked.connect(self.add_task)
        self.category_combo.activated.connect(self.on_category_combo_changed)
        self.filter_combo.currentTextChanged.connect(self.apply_filter_and_sort)
        self.sort_combo.currentTextChanged.connect(self.apply_filter_and_sort)
        self.category_filter_combo.currentTextChanged.connect(self.apply_filter_and_sort)
        self.task_input.returnPressed.connect(self.add_task)
        self.sort_order_button.clicked.connect(self.apply_filter_and_sort)
        self.todo_list.taskDeleted.connect(self.delete_tasks)
        self.todo_list.multipleTasksSelected.connect(self.update_multi_delete_visibility)

        # Connect signals for updating the add button icon
        self.task_input.textChanged.connect(self.update_add_button_icon)
        self.due_date_button.clicked.connect(self.update_add_button_icon)

    def set_button_icon(self, button, icon_name, icon_color=None):
        icon_path = f":icons/src/ui/icons/{icon_name}.svg"
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        icon = create_colored_icon(icon_path, base_color, background_color, icon_color)
        if not icon.isNull():
            button.setIcon(icon)
            button.setIconSize(QSize(32, 32))
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
                sub_category = self.sub_category_input.text().strip()
                task = Task(
                    id=self.db_manager.add_task(
                        title,
                        priority=self.priority_combo.currentText(),
                        category=category,
                        due_date=due_date.toString("yyyy-MM-dd"),
                        sub_category=sub_category
                    ),
                    title=title,
                    priority=self.priority_combo.currentText(),
                    category=category,
                    due_date=due_date.toString("yyyy-MM-dd"),
                    sub_category=sub_category
                )
                self.all_tasks.append(task)
                self.task_input.clear()
                self.sub_category_input.clear()
                self.due_date_button.setToolTip("Set due date")
                self.category_combo.setCurrentIndex(0)  # Reset category to "Manage Categories"
                self.apply_filter_and_sort()
                self.update_categories(task.category)
                self.update_add_button_icon()  # Update the button icon
                self.flash_timer.stop()  # Stop flashing when task is added
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add task: {str(e)}")

    @Slot(Task)
    def update_task(self, task):
        try:
            self.db_manager.update_task(
                task.id, task.title, task.completed, task.due_date, task.priority, task.category, task.sub_category
            )
            for i, t in enumerate(self.all_tasks):
                if t.id == task.id:
                    self.all_tasks[i] = task
                    break
            self.apply_filter_and_sort()
            self.update_categories(task.category)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update task: {str(e)}")

    @Slot(list)
    def delete_tasks(self, task_ids):
        if len(task_ids) == 1:
            self.delete_single_task(task_ids[0])
        else:
            self.delete_multiple_tasks(task_ids)

    def delete_single_task(self, task_id):
        task = next((task for task in self.all_tasks if task.id == task_id), None)
        if task:
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete the task '{task.title}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.perform_delete([task_id])

    def delete_multiple_tasks(self, task_ids):
        reply = QMessageBox.question(
            self,
            "Confirm Multiple Deletion",
            f"Are you sure you want to delete {len(task_ids)} tasks?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.perform_delete(task_ids)

    def perform_delete(self, task_ids):
        try:
            for task_id in task_ids:
                self.db_manager.delete_task(task_id)
            self.all_tasks = [task for task in self.all_tasks if task.id not in task_ids]
            self.apply_filter_and_sort()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete tasks: {str(e)}")

    @Slot(Task)
    def edit_task(self, task):
        dialog = TaskEditDialog(task, self.categories, self, date_format=self.date_format)
        if dialog.exec_():
            updated_task = dialog.get_updated_task()
            self.update_task(updated_task)

    @Slot()
    def apply_filter_and_sort(self):
        filter_option = self.filter_combo.currentText()
        sort_option = self.sort_combo.currentText()
        category_filter = self.category_filter_combo.currentText()
        sort_order = Qt.AscendingOrder if self.sort_order_button.arrowType() == Qt.UpArrow else Qt.DescendingOrder

        filtered_tasks = [
            task for task in self.all_tasks
            if (filter_option == "All" or
                (filter_option == "Active" and not task.completed) or
                (filter_option == "Completed" and task.completed)) and
               (category_filter == "All Categories" or task.category == category_filter)
        ]

        sort_key = {
            "Due Date": lambda x: x.due_date or "9999-99-99",
            "Priority": lambda x: {"High": 0, "Medium": 1, "Med": 1, "Low": 2}.get(x.priority, 3),
            "Category": lambda x: (x.category.lower(), x.sub_category.lower())
        }[sort_option]

        filtered_tasks.sort(key=sort_key, reverse=(sort_order == Qt.DescendingOrder))

        self.todo_list.clear()
        self.todo_list.add_tasks(filtered_tasks, sort_criteria=sort_option, sort_order=sort_order)

        for task_widget in self.todo_list.findChildren(TaskWidget):
            task_widget.taskChanged.connect(self.update_task)
            task_widget.taskDeleted.connect(lambda id: self.delete_tasks([id]))
            task_widget.taskEdited.connect(self.edit_task)
            task_widget.taskSelectedForDeletion.connect(self.on_task_selected_for_deletion)
            task_widget.set_date_format(self.date_format)

    def update_categories(self, new_category):
        if new_category and new_category not in self.categories:
            self.categories.append(new_category)
            self.category_combo.addItem(new_category)
            self.category_filter_combo.addItem(new_category)
            self.db_manager.add_category(new_category)

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
        self.update_customize_colors_button()

    def refresh_icons(self):
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        
        self.set_button_icon(self.due_date_button, "calendar")
        self.set_button_icon(self.add_button, "add")
        self.set_button_icon(self.multi_delete_button, "delete")
        
        # Refresh icons for all TaskWidgets
        for task_widget in self.todo_list.findChildren(TaskWidget):
            task_widget.set_button_icon(task_widget.check_button, "check")
            task_widget.set_button_icon(task_widget.edit_button, "edit")
            task_widget.set_button_icon(task_widget.delete_button, "delete")

    def update_customize_colors_button(self):
        background_color = self.palette().color(self.backgroundRole())
        text_color = self.palette().color(self.foregroundRole())
        button_color = adjust_icon_color_for_theme(text_color, background_color)
        
        self.customize_colors_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_color.name()};
                color: {text_color.name()};
                border: 1px solid {text_color.name()};
                padding: 5px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {button_color.lighter(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {button_color.darker(110).name()};
            }}
        """)

    def show_date_picker(self):
        button_pos = self.due_date_button.mapToGlobal(self.due_date_button.rect().bottomLeft())
        self.calendar_widget.move(button_pos)
        self.calendar_widget.show()

    def on_date_selected(self, date):
        self.calendar_widget.hide()
        formatted_date = date.toString(self.date_format)
        self.due_date_button.setToolTip(f"Due: {formatted_date}")
        self.update_add_button_icon()

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.PaletteChange:
            self.refresh_icons()
            self.update_customize_colors_button()
        return super().eventFilter(obj, event)

    def toggle_sort_order(self):
        if self.sort_order_button.arrowType() == Qt.UpArrow:
            self.sort_order_button.setArrowType(Qt.DownArrow)
            self.sort_order_button.setToolTip("Descending Order")
        else:
            self.sort_order_button.setArrowType(Qt.UpArrow)
            self.sort_order_button.setToolTip("Ascending Order")
        
        self.apply_filter_and_sort()

    @Slot(bool)
    def update_multi_delete_visibility(self, visible):
        self.multi_delete_button.setVisible(visible)
        self.multi_delete_label.setVisible(not visible)
        if visible:
            count = len([task for task in self.todo_list.findChildren(TaskWidget) if task.is_selected_for_deletion])
            self.multi_delete_button.setText(f"x {count}")

    @Slot()
    def on_multi_delete_clicked(self):
        selected_tasks = [task.task.id for task in self.todo_list.findChildren(TaskWidget) if task.is_selected_for_deletion]
        self.delete_tasks(selected_tasks)

    @Slot(int, bool)
    def on_task_selected_for_deletion(self, task_id, selected):
        self.update_multi_delete_visibility(True)
        count = len([task for task in self.todo_list.findChildren(TaskWidget) if task.is_selected_for_deletion])
        if count > 0:
            self.multi_delete_button.setText(f"x {count}")
        else:
            self.update_multi_delete_visibility(False)

    def update_add_button_icon(self):
        task_text_filled = bool(self.task_input.text().strip())
        due_date_selected = self.due_date_button.toolTip() != "Set due date"

        if task_text_filled and due_date_selected:
            self.flash_timer.start(500)  # Flash every 500 ms
        else:
            self.flash_timer.stop()
            icon_color = QColor('orange') if task_text_filled else None
            self.set_button_icon(self.add_button, "add", icon_color)

    def flash_add_button(self):
        self.flash_state = not self.flash_state
        icon_color = QColor('green') if self.flash_state else QColor('orange')
        self.set_button_icon(self.add_button, "add", icon_color)

    def manage_categories(self):
        dialog = CategoryManageDialog(self.db_manager, self)
        if dialog.exec_():
            self.categories = dialog.categories
            current_index = self.category_combo.currentIndex()
            self.category_combo.clear()
            self.category_combo.addItem("Manage Categories")
            self.category_combo.addItems(self.categories)
            self.category_combo.setCurrentIndex(current_index)
            
            current_filter_index = self.category_filter_combo.currentIndex()
            self.category_filter_combo.clear()
            self.category_filter_combo.addItem("All Categories")
            self.category_filter_combo.addItems(self.categories)
            self.category_filter_combo.setCurrentIndex(current_filter_index)

    def open_date_format_settings(self):
        current_format = self.date_format
        new_format, ok = QInputDialog.getText(self, "Date Format Settings",
                                              "Enter the new date format:\n"
                                              "(%Y: year, %m: month, %d: day, %b: short month name, %B: full month name)",
                                              text=current_format)
        if ok and new_format:
            self.date_format = new_format
            self.db_manager.set_date_format(new_format)
            self.apply_filter_and_sort()  # Refresh the task list with the new date format
