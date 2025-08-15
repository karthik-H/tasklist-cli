"""
TaskTracker CLI Module
Command-line interface for the TaskTracker application.
"""

import sys
from datetime import datetime
from typing import List
from models import TaskStatus, Priority
from services import TaskTrackerService


class TaskTrackerCLI:
    """Command-line interface for TaskTracker."""

    def __init__(self):
        """Initialize CLI with service instance."""
        self.service = TaskTrackerService()
        self.commands = {
            # User commands
            "add-user": self.add_user,
            "list-users": self.list_users,
            "update-user": self.update_user,
            "delete-user": self.delete_user,
            # Task commands
            "add-task": self.add_task,
            "list-tasks": self.list_tasks,
            "update-task": self.update_task,
            "delete-task": self.delete_task,
            # Assignment commands
            "assign-task": self.assign_task,
            "unassign-task": self.unassign_task,
            "reassign-task": self.reassign_task,
            # View commands
            "view-by-user": self.view_tasks_by_user,
            "view-by-status": self.view_tasks_by_status,
            "view-by-priority": self.view_tasks_by_priority,
            "view-overdue": self.view_overdue_tasks,
            # Utility commands
            "search": self.search_tasks,
            "stats": self.show_statistics,
            "help": self.show_help,
        }

    def run(self, args: List[str]) -> None:
        """Run the CLI with given arguments."""
        if not args or args[0] not in self.commands:
            self.show_help()
            return

        command = args[0]
        try:
            self.commands[command](args[1:])
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    def show_help(self, args: List[str] = None) -> None:
        """Show help information."""
        help_text = """
TaskTracker - Task Management System

USAGE:
    python main.py <command> [arguments]

USER COMMANDS:
    add-user <name> <email> [role]        - Add a new user
    list-users                            - List all users
    update-user <user_id> [--name <name>] [--email <email>] [--role <role>]
    delete-user <user_id>                 - Delete a user

TASK COMMANDS:
    add-task <title> [--desc <description>] [--priority <priority>] [--due <YYYY-MM-DD>]
    list-tasks                            - List all tasks
    update-task <task_id> [--title <title>] [--desc <description>] [--status <status>] [--priority <priority>] [--due <YYYY-MM-DD>]
    delete-task <task_id>                 - Delete a task

ASSIGNMENT COMMANDS:
    assign-task <task_id> <user_id>       - Assign task to user
    unassign-task <task_id> <user_id>     - Unassign task from user
    reassign-task <task_id> <user_id1,user_id2,...> - Reassign task to new users

VIEW COMMANDS:
    view-by-user <user_id>                - View tasks assigned to user
    view-by-status <status>               - View tasks by status (todo/progress/done)
    view-by-priority <priority>           - View tasks by priority (low/medium/high/urgent)
    view-overdue                          - View overdue tasks

UTILITY COMMANDS:
    search <query>                        - Search tasks by title/description
    stats                                 - Show task statistics
    help                                  - Show this help message

EXAMPLES:
    python main.py add-user "John Doe" "john@example.com" "Developer"
    python main.py add-task "Fix bug" --desc "Fix login issue" --priority high --due 2024-12-31
    python main.py assign-task task123 user456
    python main.py view-by-status todo
        """
        print(help_text)

    # User Management Commands
    def add_user(self, args: List[str]) -> None:
        """Add a new user."""
        if len(args) < 2:
            print("Usage: add-user <name> <email> [role]")
            return

        name = args[0]
        email = args[1]
        role = args[2] if len(args) > 2 else "User"

        user = self.service.create_user(name, email, role)
        print(f"User created successfully!")
        print(f"ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")

    def list_users(self, args: List[str]) -> None:
        """List all users."""
        users = self.service.get_all_users()
        if not users:
            print("No users found.")
            return

        print(f"\n{'ID':<40} {'Name':<20} {'Email':<30} {'Role':<15}")
        print("-" * 105)
        for user in users:
            print(f"{user.id:<40} {user.name:<20} {user.email:<30} {user.role:<15}")

    def update_user(self, args: List[str]) -> None:
        """Update user information."""
        if not args:
            print(
                "Usage: update-user <user_id> [--name <name>] [--email <email>] [--role <role>]"
            )
            return

        user_id = args[0]
        name = None
        email = None
        role = None

        i = 1
        while i < len(args):
            if args[i] == "--name" and i + 1 < len(args):
                name = args[i + 1]
                i += 2
            elif args[i] == "--email" and i + 1 < len(args):
                email = args[i + 1]
                i += 2
            elif args[i] == "--role" and i + 1 < len(args):
                role = args[i + 1]
                i += 2
            else:
                i += 1

        if self.service.update_user(user_id, name, email, role):
            print("User updated successfully!")
        else:
            print("User not found.")

    def delete_user(self, args: List[str]) -> None:
        """Delete a user."""
        if not args:
            print("Usage: delete-user <user_id>")
            return

        user_id = args[0]
        if self.service.delete_user(user_id):
            print("User deleted successfully!")
        else:
            print("User not found.")

    # Task Management Commands
    def add_task(self, args: List[str]) -> None:
        """Add a new task."""
        if not args:
            print(
                "Usage: add-task <title> [--desc <description>] [--priority <priority>] [--due <YYYY-MM-DD>]"
            )
            return

        title = args[0]
        description = ""
        priority = Priority.MEDIUM
        due_date = None

        i = 1
        while i < len(args):
            if args[i] == "--desc" and i + 1 < len(args):
                description = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                try:
                    priority = Priority(args[i + 1].title())
                except ValueError:
                    print("Invalid priority. Use: low, medium, high, urgent")
                    return
                i += 2
            elif args[i] == "--due" and i + 1 < len(args):
                try:
                    due_date = datetime.strptime(args[i + 1], "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. Use: YYYY-MM-DD")
                    return
                i += 2
            else:
                i += 1

        task = self.service.create_task(title, description, priority, due_date)
        print(f"Task created successfully!")
        print(f"ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Status: {task.status.value}")
        print(f"Priority: {task.priority.value}")

    def list_tasks(self, args: List[str]) -> None:
        """List all tasks."""
        tasks = self.service.get_all_tasks()
        if not tasks:
            print("No tasks found.")
            return

        print(
            f"\n{'ID':<40} {'Title':<25} {'Status':<12} {'Priority':<10} {'Due Date':<12} {'Assignees':<15}"
        )
        print("-" * 125)
        for task in tasks:
            due_date_str = (
                task.due_date.strftime("%Y-%m-%d") if task.due_date else "None"
            )
            assignee_count = len(task.assignees)
            assignee_str = f"{assignee_count} user(s)"
            print(
                f"{task.id:<40} {task.title:<25} {task.status.value:<12} {task.priority.value:<10} {due_date_str:<12} {assignee_str:<15}"
            )

    def update_task(self, args: List[str]) -> None:
        """Update task information."""
        if not args:
            print(
                "Usage: update-task <task_id> [--title <title>] [--desc <description>] [--status <status>] [--priority <priority>] [--due <YYYY-MM-DD>]"
            )
            return

        task_id = args[0]
        title = None
        description = None
        status = None
        priority = None
        due_date = None

        i = 1
        while i < len(args):
            if args[i] == "--title" and i + 1 < len(args):
                title = args[i + 1]
                i += 2
            elif args[i] == "--desc" and i + 1 < len(args):
                description = args[i + 1]
                i += 2
            elif args[i] == "--status" and i + 1 < len(args):
                status_map = {
                    "todo": TaskStatus.TODO,
                    "progress": TaskStatus.IN_PROGRESS,
                    "done": TaskStatus.DONE,
                }
                status_key = args[i + 1].lower()
                if status_key in status_map:
                    status = status_map[status_key]
                else:
                    print("Invalid status. Use: todo, progress, done")
                    return
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                try:
                    priority = Priority(args[i + 1].title())
                except ValueError:
                    print("Invalid priority. Use: low, medium, high, urgent")
                    return
                i += 2
            elif args[i] == "--due" and i + 1 < len(args):
                try:
                    due_date = datetime.strptime(args[i + 1], "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. Use: YYYY-MM-DD")
                    return
                i += 2
            else:
                i += 1

        if self.service.update_task(
            task_id, title, description, status, priority, due_date
        ):
            print("Task updated successfully!")
        else:
            print("Task not found.")

    def delete_task(self, args: List[str]) -> None:
        """Delete a task."""
        if not args:
            print("Usage: delete-task <task_id>")
            return

        task_id = args[0]
        if self.service.delete_task(task_id):
            print("Task deleted successfully!")
        else:
            print("Task not found.")

    # Assignment Commands
    def assign_task(self, args: List[str]) -> None:
        """Assign a task to a user."""
        if len(args) < 2:
            print("Usage: assign-task <task_id> <user_id>")
            return

        task_id, user_id = args[0], args[1]
        if self.service.assign_task_to_user(task_id, user_id):
            print("Task assigned successfully!")
        else:
            print("Task or user not found.")

    def unassign_task(self, args: List[str]) -> None:
        """Unassign a task from a user."""
        if len(args) < 2:
            print("Usage: unassign-task <task_id> <user_id>")
            return

        task_id, user_id = args[0], args[1]
        if self.service.unassign_task_from_user(task_id, user_id):
            print("Task unassigned successfully!")
        else:
            print("Task not found.")

    def reassign_task(self, args: List[str]) -> None:
        """Reassign a task to new users."""
        if len(args) < 2:
            print("Usage: reassign-task <task_id> <user_id1,user_id2,...>")
            return

        task_id = args[0]
        user_ids = args[1].split(",")

        if self.service.reassign_task(task_id, user_ids):
            print("Task reassigned successfully!")
        else:
            print("Task not found or invalid user IDs.")

    # View Commands
    def view_tasks_by_user(self, args: List[str]) -> None:
        """View tasks assigned to a specific user."""
        if not args:
            print("Usage: view-by-user <user_id>")
            return

        user_id = args[0]
        user = self.service.get_user(user_id)
        if not user:
            print("User not found.")
            return

        tasks = self.service.get_tasks_by_user(user_id)
        print(f"\nTasks assigned to {user.name} ({user.email}):")
        self._display_tasks(tasks)

    def view_tasks_by_status(self, args: List[str]) -> None:
        """View tasks by status."""
        if not args:
            print("Usage: view-by-status <status> (todo/progress/done)")
            return

        status_map = {
            "todo": TaskStatus.TODO,
            "progress": TaskStatus.IN_PROGRESS,
            "done": TaskStatus.DONE,
        }
        status_key = args[0].lower()

        if status_key not in status_map:
            print("Invalid status. Use: todo, progress, done")
            return

        status = status_map[status_key]
        tasks = self.service.get_tasks_by_status(status)
        print(f"\nTasks with status '{status.value}':")
        self._display_tasks(tasks)

    def view_tasks_by_priority(self, args: List[str]) -> None:
        """View tasks by priority."""
        if not args:
            print("Usage: view-by-priority <priority> (low/medium/high/urgent)")
            return

        try:
            priority = Priority(args[0].title())
        except ValueError:
            print("Invalid priority. Use: low, medium, high, urgent")
            return

        tasks = self.service.get_tasks_by_priority(priority)
        print(f"\nTasks with priority '{priority.value}':")
        self._display_tasks(tasks)

    def view_overdue_tasks(self, args: List[str]) -> None:
        """View overdue tasks."""
        tasks = self.service.get_overdue_tasks()
        print("\nOverdue tasks:")
        self._display_tasks(tasks)

    # Utility Commands
    def search_tasks(self, args: List[str]) -> None:
        """Search tasks by title or description."""
        if not args:
            print("Usage: search <query>")
            return

        query = " ".join(args)
        tasks = self.service.search_tasks(query)
        print(f"\nSearch results for '{query}':")
        self._display_tasks(tasks)

    def show_statistics(self, args: List[str]) -> None:
        """Show task statistics."""
        stats = self.service.get_task_statistics()
        print("\nTask Statistics:")
        print("-" * 30)
        print(f"Total Tasks: {stats['total_tasks']}")
        print(f"To Do: {stats['todo_tasks']}")
        print(f"In Progress: {stats['in_progress_tasks']}")
        print(f"Done: {stats['done_tasks']}")
        print(f"Overdue: {stats['overdue_tasks']}")
        print(f"Total Users: {stats['total_users']}")

    def _display_tasks(self, tasks: List) -> None:
        """Helper method to display a list of tasks."""
        if not tasks:
            print("No tasks found.")
            return

        print(
            f"\n{'ID':<40} {'Title':<25} {'Status':<12} {'Priority':<10} {'Due Date':<12}"
        )
        print("-" * 110)
        for task in tasks:
            due_date_str = (
                task.due_date.strftime("%Y-%m-%d") if task.due_date else "None"
            )
            print(
                f"{task.id:<40} {task.title:<25} {task.status.value:<12} {task.priority.value:<10} {due_date_str:<12}"
            )
        print(f"\nTotal: {len(tasks)} task(s)")


def main():
    """Main entry point for CLI."""
    cli = TaskTrackerCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
