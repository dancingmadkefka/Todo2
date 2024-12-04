import os, sys, logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox,
                               QLabel, QMessageBox, QStyledItemDelegate, QStyle, QToolButton, QCalendarWidget, QInputDialog)
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
            
            painter.drawText(option.rect.adjusted(5, 0, -5, 0), Qt.AlignVCenter, "Manage Categories")
            painter.setPen(QColor(200, 200, 200))
            painter.drawLine(option.rect.left(), option.rect.bottom(), option.rect.right(), option.rect.bottom())
            painter.restore()
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        if index.row() == 0:
            size.setHeight(size.height() + 5)
        return size

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.all_tasks = []
        self.categories = self.db_manager.get_all_categories()
        self.sub_categories = self.db_manager.get_all_sub_categories()
        self.date_format = self.db_manager.get_date_format()
        
        self.setup_ui()
        self.connect_signals()
        self.load_and_apply_stylesheet()
        self.load_tasks()
        self.resize(self.restore_window_size())
        self.installEventFilter(self)

        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "app_icon.ico")))

        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.flash_add_button)
        self.flash_state = True

        for widget in [self.task_input, self.priority_combo, self.category_combo, self.sub_category_combo, self.due_date_button]:
            widget.setProperty("filled", False)

    def setup_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Settings')
        date_format_action = QAction('Date Format', self)
        date_format_action.triggered.connect(self.open_date_format_settings)
        settings_menu.addAction(date_format_action)

        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["", "Low", "Medium", "High"])
        self.category_combo = CustomComboBox()
        self.category_combo.addItems(["", "Manage Categories"] + self.categories)
        self.sub_category_combo = CustomComboBox()
        self.sub_category_combo.setObjectName("subCategoryCombo")
        self.sub_category_combo.addItems(["", "Manage Sub-Categories"] + self.sub_categories)

        self.due_date_button = QToolButton()
        self.add_button = QToolButton()
        self.set_button_icon(self.due_date_button, "calendar")
        self.set_button_icon(self.add_button, "add")

        self.due_date_button.setToolTip("Set due date")
        self.due_date_button.clicked.connect(self.show_date_picker)
        self.due_date_button.setFixedSize(40, 40)
        self.add_button.setFixedSize(40, 40)

        for widget in [self.task_input, self.priority_combo, self.category_combo, self.sub_category_combo, 
                       self.due_date_button, self.add_button]:
            input_layout.addWidget(widget)

        for button in [self.due_date_button, self.add_button]:
            button.setStyleSheet("background-color: transparent; border: none;")

        self.calendar_widget = QCalendarWidget(self)
        self.calendar_widget.setWindowFlags(Qt.Popup)
        self.calendar_widget.activated.connect(self.on_date_selected)
        self.calendar_widget.hide()

        main_layout.addLayout(input_layout)

        # Add search layout
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed"])
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Due Date", "Priority", "Category", "Sub-Category"])
        self.sort_order_button = QToolButton()
        self.sort_order_button.setArrowType(Qt.UpArrow)
        self.sort_order_button.setToolTip("Ascending Order")
        self.sort_order_button.clicked.connect(self.toggle_sort_order)
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("All Categories")
        self.category_filter_combo.addItems(self.categories)
        self.sub_category_filter_combo = QComboBox()
        self.sub_category_filter_combo.setObjectName("subCategoryCombo")
        self.sub_category_filter_combo.addItem("All Sub-Categories")
        self.sub_category_filter_combo.addItems(self.sub_categories)

        filter_sort_layout = QHBoxLayout()
        for label, widget in [("Filter:", self.filter_combo), ("Category:", self.category_filter_combo),
                              ("Sub-Category:", self.sub_category_filter_combo), ("Sort by:", self.sort_combo)]:
            layout = QHBoxLayout()
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)
            layout.setSpacing(5)
            filter_sort_layout.addLayout(layout)
        
        filter_sort_layout.addWidget(self.sort_order_button)
        filter_sort_layout.addStretch(1)

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

        self.todo_list = TodoListWidget()
        main_layout.addWidget(self.todo_list)

        self.customize_colors_button = QPushButton("Customize Colors")
        self.customize_colors_button.clicked.connect(self.open_color_dialog)
        main_layout.addWidget(self.customize_colors_button)

        self.update_customize_colors_button()

        # Initialize "filled" property for input widgets
        for widget in [self.task_input, self.priority_combo, self.category_combo, self.sub_category_combo]:
            widget.setProperty("filled", False)

    def connect_signals(self):
        self.add_button.clicked.connect(self.add_task)
        self.category_combo.activated.connect(self.on_category_combo_changed)
        self.sub_category_combo.activated.connect(self.on_sub_category_combo_changed)
        for widget in [self.filter_combo, self.sort_combo, self.category_filter_combo, self.sub_category_filter_combo]:
            widget.currentTextChanged.connect(self.apply_filter_and_sort)
        self.task_input.returnPressed.connect(self.add_task)
        self.sort_order_button.clicked.connect(self.apply_filter_and_sort)
        self.todo_list.taskDeleted.connect(self.delete_tasks)
        self.todo_list.multipleTasksSelected.connect(self.update_multi_delete_visibility)
        
        self.task_input.textChanged.connect(self.check_task_input)
        self.priority_combo.currentTextChanged.connect(self.check_dropdown)
        self.category_combo.currentTextChanged.connect(self.check_dropdown)
        self.sub_category_combo.currentTextChanged.connect(self.check_dropdown)
        self.due_date_button.clicked.connect(self.show_date_picker)
        
        # Connect search input
        self.search_input.textChanged.connect(self.apply_filter_and_sort)

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
        return settings.value("size", INITIAL_WINDOW_SIZE)

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

    def check_filled(self, widget, condition):
        widget.setProperty("filled", condition)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def on_date_selected(self, date):
        self.calendar_widget.hide()
        self.due_date_button.setToolTip(f"Due: {date.toString(self.date_format)}")
        self.check_filled(self.due_date_button, True)
        self.update_add_button_icon()

    def set_button_icon(self, button, icon_name, icon_color=None):
        icon_path = f":icons/src/ui/icons/{icon_name}.svg"
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        
        if button == self.due_date_button and button.property("filled"):
            icon_color = QColor("#4CAF50")
        
        icon = create_colored_icon(icon_path, base_color, background_color, icon_color)
        if icon.isNull():
            logging.warning(f"Failed to set icon for button: {icon_name}")
        else:
            button.setIcon(icon)
            button.setIconSize(QSize(32, 32))
    
    def check_task_input(self, text):
        filled = len(text.strip()) > 3
        self.task_input.setProperty("filled", filled)
        self.task_input.style().unpolish(self.task_input)
        self.task_input.style().polish(self.task_input)
        self.update_add_button_icon()

    def check_dropdown(self, text):
        sender = self.sender()
        filled = text != "" and text not in ["Manage Categories", "Manage Sub-Categories"]
        sender.setProperty("filled", filled)
        sender.style().unpolish(sender)
        sender.style().polish(sender)
        self.update_add_button_icon()

        self.priority_combo.currentTextChanged.connect(self.check_dropdown)
        self.category_combo.currentTextChanged.connect(self.check_dropdown)
        self.sub_category_combo.currentTextChanged.connect(self.check_dropdown)

    @Slot()
    def add_task(self):
        title = self.task_input.text().strip()
        if title:
            try:
                category = self.category_combo.currentText()
                category = "" if category == "Manage Categories" else category
                sub_category = self.sub_category_combo.currentText()
                sub_category = "" if sub_category == "Manage Sub-Categories" else sub_category
                due_date_str = self.due_date_button.toolTip().split(": ")[-1]
                due_date = QDate.fromString(due_date_str, "yyyy-MM-dd") if due_date_str != "Set due date" else QDate.currentDate()
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
                self.due_date_button.setToolTip("Set due date")
                for combo in [self.category_combo, self.sub_category_combo, self.priority_combo]:
                    combo.setCurrentIndex(0)
                self.apply_filter_and_sort()
                self.update_categories(task.category)
                self.update_sub_categories(task.sub_category)
                self.update_add_button_icon()
                self.flash_timer.stop()
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
            self.update_sub_categories(task.sub_category)
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
        if task and QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the task '{task.title}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.perform_delete([task_id])

    def delete_multiple_tasks(self, task_ids):
        if QMessageBox.question(self, "Confirm Multiple Deletion", f"Are you sure you want to delete {len(task_ids)} tasks?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
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
        dialog = TaskEditDialog(task, self.categories, self.sub_categories, self, date_format=self.date_format)
        if dialog.exec_():
            self.update_task(dialog.get_updated_task())

    @Slot()
    def apply_filter_and_sort(self):
        filter_option = self.filter_combo.currentText()
        sort_option = self.sort_combo.currentText()
        category_filter = self.category_filter_combo.currentText()
        sub_category_filter = self.sub_category_filter_combo.currentText()
        sort_order = Qt.AscendingOrder if self.sort_order_button.arrowType() == Qt.UpArrow else Qt.DescendingOrder
        search_text = self.search_input.text().lower()

        # First, apply completion status and category filters
        filtered_tasks = [
            task for task in self.all_tasks
            if (filter_option == "All" or
                (filter_option == "Active" and not task.completed) or
                (filter_option == "Completed" and task.completed)) and
               (category_filter == "All Categories" or task.category == category_filter) and
               (sub_category_filter == "All Sub-Categories" or task.sub_category == sub_category_filter)
        ]

        # Then apply search filter if there's search text
        if search_text:
            filtered_tasks = [task for task in filtered_tasks if search_text in task.title.lower()]

        # Sort the filtered tasks
        sort_key = {
            "Due Date": lambda x: x.due_date or "9999-99-99",
            "Priority": lambda x: {"High": 0, "Medium": 1, "Med": 1, "Low": 2}.get(x.priority, 3),
            "Category": lambda x: (x.category.lower(), x.sub_category.lower()),
            "Sub-Category": lambda x: (x.sub_category.lower(), x.category.lower())
        }[sort_option]

        filtered_tasks.sort(key=sort_key, reverse=(sort_order == Qt.DescendingOrder))

        # Separate tasks into active and completed
        active_tasks = [task for task in filtered_tasks if not task.completed]
        completed_tasks = [task for task in filtered_tasks if task.completed]

        # Clear and add tasks to the list
        self.todo_list.clear()
        
        # Add headers and tasks
        if search_text:
            if active_tasks:
                self.todo_list.add_bold_separator("Active Tasks - Search Results")
                for task in active_tasks:
                    self.todo_list.add_task(task)
            
            if completed_tasks:
                if active_tasks:  # Add extra separator if we had active tasks
                    self.todo_list.add_bold_separator("")  # Empty separator for spacing
                self.todo_list.add_bold_separator("Completed Tasks - Search Results")
                for task in completed_tasks:
                    self.todo_list.add_task(task)
        else:
            # If no search text, just add tasks normally
            for task in active_tasks:
                self.todo_list.add_task(task)
            for task in completed_tasks:
                self.todo_list.add_task(task)

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

    def update_sub_categories(self, new_sub_category):
        if new_sub_category and new_sub_category not in self.sub_categories:
            self.sub_categories.append(new_sub_category)
            self.sub_category_combo.addItem(new_sub_category)
            self.sub_category_filter_combo.addItem(new_sub_category)
            self.db_manager.add_sub_category(new_sub_category)

    @Slot(int)
    def on_category_combo_changed(self, index):
        if self.category_combo.itemText(index) == "Manage Categories":
            self.manage_categories()
            self.category_combo.setCurrentIndex(1 if self.category_combo.count() > 1 else 0)

    @Slot(int)
    def on_sub_category_combo_changed(self, index):
        if self.sub_category_combo.itemText(index) == "Manage Sub-Categories":
            self.manage_sub_categories()
            self.sub_category_combo.setCurrentIndex(1 if self.sub_category_combo.count() > 1 else 0)

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
        
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(combined_stylesheet)
        
        self.refresh_icons()
        self.update_customize_colors_button()

    def refresh_icons(self):
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        
        for button, icon_name in [(self.due_date_button, "calendar"), (self.add_button, "add"), (self.multi_delete_button, "delete")]:
            self.set_button_icon(button, icon_name)
        
        for task_widget in self.todo_list.findChildren(TaskWidget):
            for button, icon_name in [(task_widget.check_button, "check"), (task_widget.edit_button, "edit"), (task_widget.delete_button, "delete")]:
                task_widget.set_button_icon(button, icon_name)

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
        new_arrow_type = Qt.DownArrow if self.sort_order_button.arrowType() == Qt.UpArrow else Qt.UpArrow
        self.sort_order_button.setArrowType(new_arrow_type)
        self.sort_order_button.setToolTip("Descending Order" if new_arrow_type == Qt.DownArrow else "Ascending Order")
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
        task_text_filled = len(self.task_input.text().strip()) > 3
        due_date_selected = self.due_date_button.toolTip() != "Set due date"
        
        if task_text_filled and due_date_selected:
            self.flash_timer.start(500)
        else:
            self.flash_timer.stop()
            icon_color = QColor('orange') if task_text_filled else None
            self.set_button_icon(self.add_button, "add", icon_color)
        
        self.set_button_icon(self.due_date_button, "calendar", QColor('green') if due_date_selected else None)

    def flash_add_button(self):
        self.flash_state = not self.flash_state
        icon_color = QColor('green') if self.flash_state else QColor('orange')
        self.set_button_icon(self.add_button, "add", icon_color)

    def manage_categories(self):
        self._manage_category_or_subcategory(is_sub_category=False)

    def manage_sub_categories(self):
        self._manage_category_or_subcategory(is_sub_category=True)

    def _manage_category_or_subcategory(self, is_sub_category):
        dialog = CategoryManageDialog(self.db_manager, self, is_sub_category=is_sub_category)
        if dialog.exec_():
            category_list = self.sub_categories if is_sub_category else self.categories
            combo = self.sub_category_combo if is_sub_category else self.category_combo
            filter_combo = self.sub_category_filter_combo if is_sub_category else self.category_filter_combo
            
            category_list[:] = dialog.categories
            current_index = combo.currentIndex()
            combo.clear()
            combo.addItems(["", "Manage Sub-Categories" if is_sub_category else "Manage Categories"] + category_list)
            combo.setCurrentIndex(current_index)
            
            current_filter_index = filter_combo.currentIndex()
            filter_combo.clear()
            filter_combo.addItem("All Sub-Categories" if is_sub_category else "All Categories")
            filter_combo.addItems(category_list)
            filter_combo.setCurrentIndex(current_filter_index)

    def open_date_format_settings(self):
        new_format, ok = QInputDialog.getText(self, "Date Format Settings",
                                              "Enter the new date format:\n"
                                              "(%Y: year, %m: month, %d: day, %b: short month name, %B: full month name)",
                                              text=self.date_format)
        if ok and new_format:
            self.date_format = new_format
            self.db_manager.set_date_format(new_format)
            self.apply_filter_and_sort()
