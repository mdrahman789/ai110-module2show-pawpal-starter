from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from typing import Optional

@dataclass
class Owner:
    """Represents the owner and their pets."""

    owner_id: int
    name: str
    available_time_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def update_preferences(self, preferences: list[str]) -> None:
        """Update the owner's preferences list."""
        self.preferences = list(preferences)

    def set_available_time(self, available_time_minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        self.available_time_minutes = int(available_time_minutes)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if pet.owner_id != self.owner_id:
            pet.owner_id = self.owner_id
        self.pets.append(pet)

    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Return a pet by id, or None if not found."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None

    def get_pets(self) -> list[Pet]:
        """Return a copy of the pets list."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


@dataclass
class Pet:
    """Stores pet details and their tasks."""

    pet_id: int
    name: str
    species: str
    age: int
    owner_id: int
    tasks: list[Task] = field(default_factory=list)

    def update_info(
        self,
        *,
        name: Optional[str] = None,
        species: Optional[str] = None,
        age: Optional[int] = None,
    ) -> None:
        """Update this pet's basic info."""
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            self.age = int(age)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def get_task(self, task_id: int) -> Optional[Task]:
        """Return a task by id, or None if not found."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def edit_task(
        self,
        task_id: int,
        *,
        description: Optional[str] = None,
        task_time: Optional[str] = None,
        frequency: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> bool:
        """Edit a task by id and return True if it exists."""
        task = self.get_task(task_id)
        if task is None:
            return False
        task.update_task(
            description=description,
            task_time=task_time,
            frequency=frequency,
            completed=completed,
        )
        return True

    def remove_task(self, task_id: int) -> bool:
        """Remove a task by id and return True if it was removed."""
        for i, task in enumerate(self.tasks):
            if task.task_id == task_id:
                self.tasks.pop(i)
                return True
        return False


@dataclass
class Task:
    """Represents a single pet care activity."""

    task_id: int
    description: str
    # Kept as a string like "07:30" to stay beginner-friendly.
    time: str
    frequency: str = "daily"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def update_task(
        self,
        *,
        description: Optional[str] = None,
        task_time: Optional[str] = None,
        frequency: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> None:
        """Update one or more fields on this task."""
        if description is not None:
            self.description = description
        if task_time is not None:
            self.time = task_time
        if frequency is not None:
            self.frequency = frequency
        if completed is not None:
            self.completed = bool(completed)


class Scheduler:
    """Acts as the brain of the app: collects and orders tasks for the day."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for a specific owner."""
        self.owner: Owner = owner
        self._last_schedule: list[tuple[str, Pet, Task]] = []
        self._last_explanation: str = ""

    @staticmethod
    def _parse_time(value: str) -> time:
        """Parse a 'HH:MM' time string into a sortable `datetime.time`."""
        try:
            parts = value.strip().split(":")
            if len(parts) != 2:
                raise ValueError("Expected HH:MM")
            hour = int(parts[0])
            minute = int(parts[1])
            return time(hour=hour, minute=minute)
        except Exception:
            return time(hour=23, minute=59)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across the owner's pets."""
        pairs: list[tuple[Pet, Task]] = []
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                pairs.append((pet, task))
        return pairs

    def generate_daily_schedule(self, *, include_completed: bool = False) -> list[tuple[str, Pet, Task]]:
        """Collect tasks across all pets and return them sorted by time."""
        items: list[tuple[str, Pet, Task]] = []
        for pet, task in self.get_all_tasks():
            if (not include_completed) and task.completed:
                continue
            items.append((task.time, pet, task))

        items.sort(key=lambda x: self._parse_time(x[0]))
        self._last_schedule = items
        self._last_explanation = (
            "Tasks were collected from all pets and sorted by time so the plan follows a simple, "
            "easy-to-follow day order (earliest tasks first)."
        )
        return list(items)

    def explain_schedule(self) -> str:
        """Explain why the most recent schedule was chosen."""
        if not self._last_schedule:
            return "No schedule has been generated yet (or there were no tasks to schedule)."
        return self._last_explanation

