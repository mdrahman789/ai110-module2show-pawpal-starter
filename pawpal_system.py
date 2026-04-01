from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Owner:
    owner_id: int
    name: str
    available_time: int
    preferences: list[str] = field(default_factory=list)

    def update_preferences(self, preferences: list[str]) -> None:
        pass

    def set_available_time(self, available_time: int) -> None:
        pass


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    age: int
    owner_id: int

    def update_info(self) -> None:
        pass


@dataclass
class Task:
    task_id: int
    name: str
    duration: int
    priority: int
    category: str
    notes: str
    completed: bool

    def mark_complete(self) -> None:
        pass

    def update_task(self) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task] | None = None) -> None:
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.tasks: list[Task] = tasks if tasks is not None else []

    def add_task(self) -> None:
        pass

    def edit_task(self) -> None:
        pass

    def generate_daily_plan(self) -> None:
        pass

    def explain_plan(self) -> None:
        pass

    def get_tasks_by_priority(self) -> None:
        pass

