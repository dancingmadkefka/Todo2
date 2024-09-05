import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, Slot, QSize, QRect, QPoint
from PySide6.QtGui import QFont, QIcon, QPainter, QColor, QLinearGradient, QPainterPath
from models.task import Task

class TaskWidget(QWidget):
    taskChanged = Signal(Task)
    taskDeleted = Signal(int)
    taskEdited = Signal(Task)

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("TaskWidget")  # Add this line
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.task.completed)
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        layout.addWidget(self.checkbox)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        self.title_label = QLabel(self.task.title)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        info_layout.addWidget(self.title_label)

        details_label = QLabel(f"{self.task.category} | Due: {self.task.format_due_date()}")
        details_label.setFont(QFont("Segoe UI", 10))
        info_layout.addWidget(details_label)

        layout.addLayout(info_layout, 1)

        self.priority_label = QLabel(self.task.priority)
        self.priority_label.setAlignment(Qt.AlignCenter)
        self.priority_label.setFixedSize(QSize(45, 30))
        self.priority_label.setProperty("class", "priority-label")
        self.priority_label.setProperty("priority", self.task.priority.lower())
        layout.addWidget(self.priority_label)

        edit_button = self.create_button("edit", "Edit", self.on_edit_clicked)
        layout.addWidget(edit_button)

        delete_button = self.create_button("delete", "Delete", self.on_delete_clicked)
        layout.addWidget(delete_button)

        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.updateStyle()

        # Remove any inline styles
        self.setStyleSheet("")  # Add this line

    def create_button(self, icon_name, text, slot):
        icon = self.load_icon(icon_name)
        button = QPushButton(text if not icon else "")
        if icon:
            button.setIcon(icon)
        button.clicked.connect(slot)
        button.setFixedSize(QSize(40, 30))
        return button

    @staticmethod
    def load_icon(icon_name):
        icon_path = os.path.join(os.path.dirname(__file__), "icons", f"{icon_name}.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                return icon
        return None

    def updateStyle(self):
        self.setProperty("completed", self.task.completed)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw shadow
        shadow_color = QColor(0, 0, 0, 30)
        shadow_width = 4
        
        gradient = QLinearGradient(QPoint(0, self.height()), QPoint(0, self.height() + shadow_width))
        gradient.setColorAt(0, shadow_color)
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        shadow_path = QPainterPath()
        shadow_path.addRect(QRect(0, self.height(), self.width(), shadow_width))
        painter.fillPath(shadow_path, gradient)

        # Draw main rectangle
        main_rect = QRect(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(main_rect, 4, 4)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawPath(path)

    @Slot(int)
    def on_checkbox_state_changed(self, state):
        self.task.completed = (state == Qt.Checked)
        self.updateStyle()
        self.taskChanged.emit(self.task)

    @Slot()
    def on_delete_clicked(self):
        self.taskDeleted.emit(self.task.id)

    @Slot()
    def on_edit_clicked(self):
        self.taskEdited.emit(self.task)