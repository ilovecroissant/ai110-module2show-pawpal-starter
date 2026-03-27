from dataclasses import dataclass
from typing import List


@dataclass
class Pet:
    animal_type: str
    age: int
    color: str


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: List[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_daily_schedule(self) -> List[Task]:
        pass
