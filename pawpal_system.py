from dataclasses import dataclass
from typing import List
from enum import Enum


class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Pet:
    animal_type: str
    age: int
    color: str


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    pet: Pet


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def edit_task(self, task: "Task", title: str, duration_minutes: int, priority: Priority) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pets: List[Pet], tasks: List[Task]):
        self.owner = owner
        self.pets = pets
        self.tasks = tasks

    def generate_daily_schedule(self) -> List[Task]:
        pass
