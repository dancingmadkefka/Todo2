from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                                    QToolButton, QSizePolicy, QApplication, QTextEdit)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QEvent, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor
from .icon_utils import create_colored_icon
from datetime import datetime
import logging

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
        self.is_expanded = False
        self.shift_held = False
        self.setup_ui()
        self.update_text_style()
        self.installEventFilter(self)
        self.update_tooltip()
        self.setObjectName("TaskWidget")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Task content
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)
        task_layout.setContentsMargins(5, 5, 5, 5)
        task_layout.setSpacing(10)

        self.check_button = QToolButton()
        self.check_button.setObjectName("checkButton")
        self.set_button_icon(self.check_button, "check")
        self.check_button.setCheckable(True)
        self.check_button.setChecked(self.task.completed)
        self.check_button.clicked.connect(self.on_check_button_clicked)
        self.check_button.setFixedSize(32, 32)
        task_layout.addWidget(self.check_button)

        # Main content area (clickable)
        content_widget = QWidget()
        content_widget.setCursor(Qt.PointingHandCursor)
        content_widget.mousePressEvent = self.on_content_clicked
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel(self.task.title)
        self.title_label.setWordWrap(True)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        title_layout.addWidget(self.title_label)
        
        if self.task.notes:
            self.notes_indicator = QLabel("📝")
            self.notes_indicator.setObjectName("notesIndicator")
            title_layout.addWidget(self.notes_indicator)
        
        content_layout.addLayout(title_layout)

        self.subtext_label = QLabel()
        self.subtext_label.setObjectName("subtextLabel")
        self.subtext_label.setWordWrap(True)
        self.subtext_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        content_layout.addWidget(self.subtext_label)

        self.update_subtext()
        task_layout.addWidget(content_widget, 1)

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

        task_layout.addLayout(button_layout)
        layout.addWidget(task_widget)

        # Notes editor
        self.notes_editor = QTextEdit()
        self.notes_editor.setVisible(False)
        self.notes_editor.setMinimumHeight(0)
        self.notes_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if self.task.notes:
            self.notes_editor.setPlainText(self.task.notes)
        self.notes_editor.focusOutEvent = self.on_notes_focus_lost
        layout.addWidget(self.notes_editor)

        self.setMinimumWidth(300)

    def on_content_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_notes_section()

    def on_animation_finished(self):
        if not self.is_expanded:
            self.notes_editor.setVisible(False)

    def toggle_notes_section(self):
        if not hasattr(self, 'animation'):
            self.animation = QPropertyAnimation(self.notes_editor, b"minimumHeight")
            self.animation.setDuration(200)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        if self.animation.state() == QPropertyAnimation.Running:
            return

        # Disconnect any existing finished connections
        try:
            self.animation.finished.disconnect()
        except:
            pass

        if not self.is_expanded:
            self.notes_editor.setVisible(True)
            self.animation.setStartValue(0)
            self.animation.setEndValue(100)
        else:
            self.animation.setStartValue(100)
            self.animation.setEndValue(0)
            self.animation.finished.connect(self.on_animation_finished)

        self.animation.start()
        self.is_expanded = not self.is_expanded

    def on_notes_focus_lost(self, event):
        super(QTextEdit, self.notes_editor).focusOutEvent(event)
        new_notes = self.notes_editor.toPlainText()
        if new_notes != self.task.notes:
            self.task.notes = new_notes
            self.taskChanged.emit(self.task)
            
            # Update notes indicator
            if self.task.notes and not hasattr(self, 'notes_indicator'):
                self.notes_indicator = QLabel("📝")
                self.notes_indicator.setObjectName("notesIndicator")
                self.title_label.parent().layout().addWidget(self.notes_indicator)
            elif not self.task.notes and hasattr(self, 'notes_indicator'):
                self.notes_indicator.deleteLater()
                delattr(self, 'notes_indicator')

    def update_subtext(self):
        due_date = self.format_due_date(self.task.due_date)
        sub_category = self.task.sub_category or 'No Sub-category'
        subtext = f"{self.task.priority} | {self.task.category} | {due_date} | <span class='sub-category'>{sub_category}</span>"
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
        icon_color = None
        
        if button == self.delete_button:
            if self.shift_held:
                icon_color = QColor("#FF0000")  # Red color for shift-held state
            elif self.is_selected_for_deletion:
                icon_color = base_color.lighter(150)
                
        icon = create_colored_icon(icon_path, base_color, background_color, icon_color)
        if not icon.isNull():
            button.setIcon(icon)
            button.setIconSize(QSize(32, 32))
        else:
            logging.warning(f"Failed to set icon for button: {icon_name}")

    def update_tooltip(self):
        tooltip_text = f"Title: {self.task.title}\n"
        if self.task.description:
            tooltip_text += f"Description: {self.task.description}\n"
        if self.task.notes:
            # Show first 100 characters of notes with ellipsis if longer
            notes_preview = self.task.notes[:100] + ("..." if len(self.task.notes) > 100 else "")
            tooltip_text += f"Notes: {notes_preview}\n"
        tooltip_text += f"Priority: {self.task.priority}\n"
        tooltip_text += f"Category: {self.task.category}\n"
        if self.task.sub_category:
            tooltip_text += f"Sub-category: {self.task.sub_category}\n"
        if self.task.due_date:
            tooltip_text += f"Due: {self.format_due_date(self.task.due_date)}"
        
        self.setToolTip(tooltip_text)

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
        if hasattr(self, 'notes_indicator'):
            self.notes_indicator.setFont(font)

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
        if obj == self:
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Shift:
                self.shift_held = True
                self.update_icon_colors()
            elif event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Shift:
                self.shift_held = False
                self.update_icon_colors()
            elif event.type() == QEvent.PaletteChange:
                self.update_icon_colors()
        return super().eventFilter(obj, event)

    def set_selected_for_deletion(self, selected):
        self.is_selected_for_deletion = selected
        self.update_deletion_selection_style()

    def update_sort_criteria_style(self, sort_criteria):
        parts = self.subtext_label.text().split('|')
        bold_font = QFont(self.subtext_label.font())
        bold_font.setBold(True)
        self.subtext_label.setFont(bold_font)

        if sort_criteria == "Priority":
            index = 0
        elif sort_criteria == "Category":
            index = 1
        elif sort_criteria == "Due Date":
            index = 2
        elif sort_criteria == "Sub-Category":
            index = 3
        else:
            self.reset_subtext_style()
            return

        parts[index] = f'<b>{parts[index].strip()}</b>'
        formatted_text = ' | '.join(parts)
        self.subtext_label.setText(formatted_text)
        self.subtext_label.setProperty("sortCriteria", "true")

        self.style().unpolish(self.subtext_label)
        self.style().polish(self.subtext_label)

    def reset_subtext_style(self):
        self.update_subtext()
        normal_font = QFont(self.subtext_label.font())
        normal_font.setBold(False)
        self.subtext_label.setFont(normal_font)
        self.subtext_label.setProperty("sortCriteria", "false")
        self.style().unpolish(self.subtext_label)
        self.style().polish(self.subtext_label)

    def set_date_format(self, date_format):
        self.date_format = date_format
        self.update_subtext()
