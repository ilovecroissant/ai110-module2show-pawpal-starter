from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List, Optional
from enum import Enum


class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    pet: "Pet"
    frequency: str = "daily"        # e.g. "daily", "weekly", or "once"
    start_time: str = "08:00"       # "HH:MM" format
    completed: bool = False
    due_date: Optional[date] = None  # None means no specific date

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task's completion status to incomplete."""
        self.completed = False

    _FREQUENCY_DELTAS = {
        "daily":  timedelta(days=1),
        "weekly": timedelta(weeks=1),
    }

    def next_occurrence(self) -> "Task":
        """Return a new Task for the next daily or weekly occurrence.

        The new task is identical to this one but with completed=False and
        due_date advanced by 1 day (daily) or 7 days (weekly).
        Raises ValueError for non-recurring frequencies (e.g. "once").
        """
        delta = self._FREQUENCY_DELTAS.get(self.frequency)
        if delta is None:
            raise ValueError(f"Task '{self.title}' has frequency '{self.frequency}' — no next occurrence.")
        return replace(self, completed=False, due_date=(self.due_date or date.today()) + delta)


@dataclass
class Pet:
    animal_type: str
    age: int
    color: str
    name: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's roster."""
        self.pets.remove(pet)

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a task to the specified pet."""
        pet.add_task(task)

    def edit_task(self, task: Task, title: str, duration_minutes: int, priority: Priority) -> None:
        """Update the title, duration, and priority of an existing task."""
        task.title = title
        task.duration_minutes = duration_minutes
        task.priority = priority

    @property
    def all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner, pets: List[Pet]):
        self.owner = owner
        self.pets = pets

    def generate_daily_schedule(self) -> List[Task]:
        """Return all daily tasks across assigned pets, sorted by priority."""
        relevant_tasks = [
            t for pet in self.pets
            for t in pet.tasks
            if t.frequency == "daily"
        ]
        return sorted(relevant_tasks, key=lambda t: t.priority.value)

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed yet."""
        return [t for t in self.generate_daily_schedule() if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return only tasks that have been marked complete."""
        return [t for t in self.generate_daily_schedule() if t.completed]

    def total_time_minutes(self) -> int:
        """Return the total duration in minutes of all pending tasks."""
        return sum(t.duration_minutes for t in self.get_pending_tasks())

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, return only
                       pending tasks. If None, completion status is not filtered.
            pet_name:  If provided, return only tasks belonging to that pet name.
                       If None, tasks for all pets are included.
        """
        tasks = self.generate_daily_schedule()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet.name.lower() == pet_name.lower()]
        return tasks

    def detect_conflicts(self) -> List[tuple[Task, Task]]:
        """Return pairs of pending tasks whose time windows overlap.

        Two tasks conflict when one starts before the other finishes:
            A.start < B.end  AND  B.start < A.end
        Works across all pets (same-pet and cross-pet conflicts are both reported).
        Each conflicting pair is returned once, in (earlier-starting, later-starting) order.
        """
        from datetime import datetime

        def to_minutes(hhmm: str) -> int:
            t = datetime.strptime(hhmm, "%H:%M")
            return t.hour * 60 + t.minute

        pending = self.get_pending_tasks()
        conflicts = []
        for i, a in enumerate(pending):
            a_start = to_minutes(a.start_time)
            a_end = a_start + a.duration_minutes
            for b in pending[i + 1:]:
                b_start = to_minutes(b.start_time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts

    def sort_by_time(self) -> List[Task]:
        """Return pending tasks sorted chronologically by start_time ("HH:MM")."""
        return sorted(self.get_pending_tasks(), key=lambda t: t.start_time)

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add the next occurrence to its pet.

        Returns the newly created Task for daily/weekly tasks, or None for one-off tasks.
        """
        task.mark_complete()
        if task.frequency in ("daily", "weekly"):
            next_task = task.next_occurrence()
            task.pet.add_task(next_task)
            return next_task
        return None

    def reset_all_tasks(self) -> None:
        """Reset completion status on all tasks across assigned pets."""
        for pet in self.pets:
            for task in pet.tasks:
                task.reset()
