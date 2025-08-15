"""
TaskTracker Models Module
Contains data models for Task and User entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


class TaskStatus(Enum):
    """Enumeration for task status values."""

    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class Priority(Enum):
    """Enumeration for task priority levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


@dataclass
class User:
    """User model with unique ID, name, email, and role."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    role: str = ""

    def __post_init__(self):
        """Validate user data after initialization."""
        if not self.name.strip():
            raise ValueError("User name cannot be empty")
        if not self.email.strip():
            raise ValueError("User email cannot be empty")
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    def to_dict(self) -> dict:
        """Convert user to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }


@dataclass
class Task:
    """Task model with unique ID, title, description, status, due date, and priority."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    assignees: List[str] = field(default_factory=list)  # List of user IDs
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.title.strip():
            raise ValueError("Task title cannot be empty")

    def assign_user(self, user_id: str) -> None:
        """Assign a user to this task."""
        if user_id not in self.assignees:
            self.assignees.append(user_id)
            self.updated_at = datetime.now()

    def unassign_user(self, user_id: str) -> None:
        """Remove a user from this task."""
        if user_id in self.assignees:
            self.assignees.remove(user_id)
            self.updated_at = datetime.now()

    def update_status(self, status: TaskStatus) -> None:
        """Update task status."""
        self.status = status
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority.value,
            "assignees": self.assignees,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.DONE:
            return datetime.now() > self.due_date
        return False
