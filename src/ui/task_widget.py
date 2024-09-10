from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, Slot, QSize, QEvent
from PySide6.QtGui import QColor
from .icon_utils import create_colored_icon

class TaskWidget(QWidget):
    taskChanged = Signal(object)
    taskDeleted = Signal(int)
    taskEdited = Signal(object)

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.setup_ui()
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
        self.edit_button.setFixedSize(32, 32)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QToolButton()
        self.delete_button.setObjectName("deleteButton")
        self.set_button_icon(self.delete_button, "delete")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setFixedSize(32, 32)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        # Set minimum width for the widget to ensure buttons are always visible
        self.setMinimumWidth(300)

    def set_button_icon(self, button, icon_name):
        icon_path = f":icons/src/ui/icons/{icon_name}.svg"
        base_color = self.palette().text().color()
        background_color = self.palette().window().color()
        icon = create_colored_icon(icon_path, base_color, background_color)
        button.setIcon(icon)
        button.setIconSize(QSize(24, 24))

    @Slot(bool)
    def on_check_button_clicked(self, checked):
        self.task.completed = checked
        self.check_button.setProperty("checked", checked)
        self.check_button.style().unpolish(self.check_button)
        self.check_button.style().polish(self.check_button)
        self.update_icon_colors()
        self.taskChanged.emit(self.task)

    def update_icon_colors(self):
        self.set_button_icon(self.check_button, "check")
        self.set_button_icon(self.edit_button, "edit")
        self.set_button_icon(self.delete_button, "delete")

    @Slot()
    def on_delete_clicked(self):
        self.taskDeleted.emit(self.task.id)

    @Slot()
    def on_edit_clicked(self):
        self.taskEdited.emit(self.task)

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.PaletteChange:
            self.update_icon_colors()
        return super().eventFilter(obj, event)