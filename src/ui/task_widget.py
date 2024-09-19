from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolButton, QSizePolicy, QApplication
from PySide6.QtCore import Qt, Signal, Slot, QSize, QEvent
from PySide6.QtGui import QFont
from .icon_utils import create_colored_icon
from datetime import datetime

class TaskWidget(QWidget):
    taskChanged = Signal(object)
    taskDeleted = Signal(int)
    taskEdited = Signal(object)
    taskSelectedForDeletion = Signal(int, bool)

    def __init__(self, task, date_format="%Y-%m-%d"):
        super().__init__()
        self.task = task
        self.date_format = date_format
        self.is_selected_for_deletion = False
        self.delete_button = None
        self.setup_ui()
        self.update_text_style()
        self.installEventFilter(self)

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        self.check_button = QToolButton()
        self.check_button.setObjectName("checkButton")
        self.set_button_icon(self.check_button, "check")
        self.check_button.setCheckable(True)
        self.check_button.setChecked(self.task.completed)
        self.check_button.clicked.connect(self.on_check_button_clicked)
        self.check_button.setFixedSize(32, 32)
        layout.addWidget(self.check_button)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self.title_label = QLabel(self.task.title)
        self.title_label.setWordWrap(True)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        text_layout.addWidget(self.title_label)

        self.subtext_label = QLabel()
        self.subtext_label.setObjectName("subtextLabel")
        self.subtext_label.setWordWrap(True)
        self.subtext_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        text_layout.addWidget(self.subtext_label)

        self.update_subtext()

        layout.addLayout(text_layout, 1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        self.edit_button = QToolButton()
        self.edit_button.setObjectName("editButton")
        self.set_button_icon(self.edit_button, "edit")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        self.edit_button.setFixedSize(40, 40)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QToolButton()
        self.delete_button.setObjectName("deleteButton")
        self.set_button_icon(self.delete_button, "delete")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setFixedSize(40, 40)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.setMinimumWidth(300)

    def update_subtext(self):
        due_date = self.format_due_date(self.task.due_date)
        subtext = f"{self.task.priority} | {self.task.category or 'No Category'} | Due: {due_date}"
        self.subtext_label.setText(subtext)

    def format_due_date(self, due_date):
        if not due_date:
            return "No Date"
        date = datetime.strptime(due_date, "%Y-%m-%d")
        return date.strftime(self.date_format)

    def set_button_icon(self, button, icon_name):
        icon_path = f":icons/src/ui/icons/{icon_name}.svg"
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        if hasattr(self, 'delete_button') and button == self.delete_button and self.is_selected_for_deletion:
            base_color = base_color.lighter(150)
        icon = create_colored_icon(icon_path, base_color, background_color)
        button.setIcon(icon)
        button.setIconSize(QSize(32, 32))

    @Slot(bool)
    def on_check_button_clicked(self, checked):
        self.task.completed = checked
        self.check_button.setProperty("checked", checked)
        self.check_button.style().unpolish(self.check_button)
        self.check_button.style().polish(self.check_button)
        self.update_icon_colors()
        self.update_text_style()
        self.taskChanged.emit(self.task)

    def update_icon_colors(self):
        self.set_button_icon(self.check_button, "check")
        self.set_button_icon(self.edit_button, "edit")
        self.set_button_icon(self.delete_button, "delete")

    def update_text_style(self):
        font = QFont()
        if self.task.completed:
            font.setStrikeOut(True)
        else:
            font.setStrikeOut(False)
        self.title_label.setFont(font)
        self.subtext_label.setFont(font)

    @Slot()
    def on_delete_clicked(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            self.toggle_selection_for_deletion()
        else:
            self.taskDeleted.emit(self.task.id)

    def toggle_selection_for_deletion(self):
        self.is_selected_for_deletion = not self.is_selected_for_deletion
        self.update_deletion_selection_style()
        self.taskSelectedForDeletion.emit(self.task.id, self.is_selected_for_deletion)

    def update_deletion_selection_style(self):
        self.setProperty("selected", self.is_selected_for_deletion)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update_icon_colors()

    @Slot()
    def on_edit_clicked(self):
        self.taskEdited.emit(self.task)

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.PaletteChange:
            self.update_icon_colors()
        return super().eventFilter(obj, event)

    def set_selected_for_deletion(self, selected):
        self.is_selected_for_deletion = selected
        self.update_deletion_selection_style()

    def update_sort_criteria_style(self, sort_criteria):
        if sort_criteria == "Priority":
            self.bold_subtext_part(0)
        elif sort_criteria == "Category":
            self.bold_subtext_part(1)
        elif sort_criteria == "Due Date":
            self.bold_subtext_part(2)
        else:
            self.reset_subtext_style()

    def bold_subtext_part(self, index):
        parts = self.subtext_label.text().split('|')
        if 0 <= index < len(parts):
            parts[index] = f"<b>{parts[index].strip()}</b>"
            self.subtext_label.setText(' | '.join(parts))
            self.subtext_label.setProperty("sortCriteria", "true")
        self.style().unpolish(self.subtext_label)
        self.style().polish(self.subtext_label)

    def reset_subtext_style(self):
        self.update_subtext()
        self.subtext_label.setProperty("sortCriteria", "false")
        self.style().unpolish(self.subtext_label)
        self.style().polish(self.subtext_label)

    def set_date_format(self, date_format):
        self.date_format = date_format
        self.update_subtext()