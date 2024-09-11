from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolButton, QSizePolicy, QApplication
from PySide6.QtCore import Qt, Signal, Slot, QSize, QEvent
from PySide6.QtGui import QColor, QFont
from .icon_utils import create_colored_icon

class TaskWidget(QWidget):
    taskChanged = Signal(object)
    taskDeleted = Signal(int)
    taskEdited = Signal(object)
    taskSelectedForDeletion = Signal(int, bool)  # New signal for task selection

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.is_selected_for_deletion = False  # New attribute for deletion selection state
        self.delete_button = None  # Initialize delete_button as None
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

        subtext = f"{self.task.priority} | {self.task.category or 'No Category'} | Due: {self.task.due_date or 'No Date'}"
        self.subtext_label = QLabel(subtext)
        self.subtext_label.setObjectName("subtextLabel")
        self.subtext_label.setWordWrap(True)
        self.subtext_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        text_layout.addWidget(self.subtext_label)

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

        # Set minimum width for the widget to ensure buttons are always visible
        self.setMinimumWidth(300)

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
        if modifiers == Qt.ShiftModifier:  # Using Shift key for multi-select
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