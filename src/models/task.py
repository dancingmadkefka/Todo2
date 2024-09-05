from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "Medium"
    completed: bool = False
    category: str = "Other"
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.due_date, datetime):
            self.due_date = self.due_date.strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "completed": self.completed,
            "category": self.category,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "Medium"),
            completed=data.get("completed", False),
            category=data.get("category", "Other"),
            tags=data.get("tags", [])
        )

    def __str__(self):
        status = "Completed" if self.completed else "Pending"
        due_date_str = f", Due: {self.due_date}" if self.due_date else ""
        tags_str = f", Tags: {', '.join(self.tags)}" if self.tags else ""
        return f"[{self.priority}] {self.title} ({status}{due_date_str}) - {self.category}{tags_str}"

    def is_overdue(self):
        if self.due_date:
            due_date = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            return due_date < datetime.now().date() and not self.completed
        return False

    def format_due_date(self):
        if not self.due_date:
            return ""
        try:
            date_obj = datetime.strptime(self.due_date, "%Y-%m-%d")
            return date_obj.strftime("%d%b%y").upper()
        except ValueError:
            return self.due_date  # Return original string if parsing fails

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.__post_init__()  # Ensure due_date is properly formatted after update