from dataclasses import dataclass, field
from typing import List
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
    frequency: str = "daily"        # e.g. "daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task's completion status to incomplete."""
        self.completed = False


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

    def reset_all_tasks(self) -> None:
        """Reset completion status on all tasks across assigned pets."""
        for pet in self.pets:
            for task in pet.tasks:
                task.reset()
