"""
TaskTracker Services Module
Contains business logic and data management services.
"""

from datetime import datetime
from typing import Dict, List, Optional
from models import Task, User, TaskStatus, Priority


class TaskTrackerService:
    """Main service class for managing tasks and users."""

    def __init__(self):
        """Initialize the service with empty data stores."""
        self.tasks: Dict[str, Task] = {}
        self.users: Dict[str, User] = {}

    # User Management Methods
    def create_user(self, name: str, email: str, role: str = "User") -> User:
        """Create a new user."""
        user = User(name=name, email=email, role=role)
        self.users[user.id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.users.get(user_id)

    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self.users.values())

    def update_user(
        self, user_id: str, name: str = None, email: str = None, role: str = None
    ) -> bool:
        """Update user information."""
        user = self.users.get(user_id)
        if not user:
            return False

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role

        return True

    def delete_user(self, user_id: str) -> bool:
        """Delete a user and remove from all assigned tasks."""
        if user_id not in self.users:
            return False

        # Remove user from all assigned tasks
        for task in self.tasks.values():
            task.unassign_user(user_id)

        del self.users[user_id]
        return True

    def find_user_by_email(self, email: str) -> Optional[User]:
        """Find a user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    # Task Management Methods
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """Create a new task."""
        task = Task(
            title=title, description=description, priority=priority, due_date=due_date
        )
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())

    def update_task(
        self,
        task_id: str,
        title: str = None,
        description: str = None,
        status: TaskStatus = None,
        priority: Priority = None,
        due_date: datetime = None,
    ) -> bool:
        """Update task information."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.update_status(status)
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date

        task.updated_at = datetime.now()
        return True

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id not in self.tasks:
            return False
        del self.tasks[task_id]
        return True

    # Task Assignment Methods
    def assign_task_to_user(self, task_id: str, user_id: str) -> bool:
        """Assign a task to a user."""
        task = self.tasks.get(task_id)
        user = self.users.get(user_id)

        if not task or not user:
            return False

        task.assign_user(user_id)
        return True

    def unassign_task_from_user(self, task_id: str, user_id: str) -> bool:
        """Unassign a task from a user."""
        task = self.tasks.get(task_id)

        if not task:
            return False

        task.unassign_user(user_id)
        return True

    def reassign_task(self, task_id: str, new_user_ids: List[str]) -> bool:
        """Reassign a task to new users (replaces current assignees)."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        # Validate all user IDs exist
        for user_id in new_user_ids:
            if user_id not in self.users:
                return False

        task.assignees = new_user_ids.copy()
        task.updated_at = datetime.now()
        return True

    # Task Filtering Methods
    def get_tasks_by_user(self, user_id: str) -> List[Task]:
        """Get all tasks assigned to a specific user."""
        return [task for task in self.tasks.values() if user_id in task.assignees]

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Get all tasks with a specific priority."""
        return [task for task in self.tasks.values() if task.priority == priority]

    def get_tasks_by_due_date(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> List[Task]:
        """Get tasks within a date range."""
        filtered_tasks = []

        for task in self.tasks.values():
            if task.due_date is None:
                continue

            if start_date and task.due_date < start_date:
                continue
            if end_date and task.due_date > end_date:
                continue

            filtered_tasks.append(task)

        return filtered_tasks

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return [task for task in self.tasks.values() if task.is_overdue()]

    def get_task_statistics(self) -> Dict[str, int]:
        """Get task statistics."""
        stats = {
            "total_tasks": len(self.tasks),
            "todo_tasks": len(self.get_tasks_by_status(TaskStatus.TODO)),
            "in_progress_tasks": len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS)),
            "done_tasks": len(self.get_tasks_by_status(TaskStatus.DONE)),
            "overdue_tasks": len(self.get_overdue_tasks()),
            "total_users": len(self.users),
        }
        return stats

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description."""
        query = query.lower()
        results = []

        for task in self.tasks.values():
            if query in task.title.lower() or query in task.description.lower():
                results.append(task)

        return results
