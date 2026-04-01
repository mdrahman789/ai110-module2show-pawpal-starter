from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta
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
        duration_minutes: Optional[int] = None,
        priority: Optional[int] = None,
        completed: Optional[bool] = None,
    ) -> bool:
        """Edit a task by id and return True if it exists."""
        task = self.get_task(task_id)
        if task is None:
            return False
        was_completed = task.completed
        task.update_task(
            description=description,
            task_time=task_time,
            frequency=frequency,
            duration_minutes=duration_minutes,
            priority=priority,
            completed=completed,
        )
        if (not was_completed) and task.completed:
            self._create_next_recurring_task_if_needed(task)
        return True

    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task completed.

        If it's a daily/weekly task, also create the next occurrence.
        """
        task = self.get_task(task_id)
        if task is None:
            return False

        if task.completed:
            return True

        task.mark_complete()
        self._create_next_recurring_task_if_needed(task)
        return True

    def _next_task_id(self) -> int:
        """Return a new unique task id for this pet."""
        if not self.tasks:
            return 1
        return max(t.task_id for t in self.tasks) + 1

    def _create_next_recurring_task_if_needed(self, task: Task) -> None:
        """If `task` is daily/weekly, add the next occurrence."""
        freq = (task.frequency or "").strip().lower()
        if freq not in {"daily", "weekly"}:
            return

        base_due = task.due_date or date.today()
        if freq == "daily":
            next_due = base_due + timedelta(days=1)
        else:
            next_due = base_due + timedelta(days=7)

        next_task = Task(
            task_id=self._next_task_id(),
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            duration_minutes=getattr(task, "duration_minutes", 15),
            priority=getattr(task, "priority", 3),
            completed=False,
            due_date=next_due,
        )
        self.add_task(next_task)

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
    duration_minutes: int = 15
    # Priority: 1 = highest, 5 = lowest (simple scale for beginners).
    priority: int = 3
    completed: bool = False
    due_date: Optional[date] = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def update_task(
        self,
        *,
        description: Optional[str] = None,
        task_time: Optional[str] = None,
        frequency: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[int] = None,
        completed: Optional[bool] = None,
    ) -> None:
        """Update one or more fields on this task."""
        if description is not None:
            self.description = description
        if task_time is not None:
            self.time = task_time
        if frequency is not None:
            self.frequency = frequency
        if duration_minutes is not None:
            self.duration_minutes = max(0, int(duration_minutes))
        if priority is not None:
            p = int(priority)
            self.priority = min(5, max(1, p))
        if completed is not None:
            self.completed = bool(completed)


class Scheduler:
    """Acts as the brain of the app: collects and orders tasks for the day."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for a specific owner."""
        self.owner: Owner = owner
        self._last_schedule: list[tuple[str, Pet, Task]] = []
        self._last_explanation: str = ""

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by their time (using the 'HH:MM' string)."""
        return sorted(tasks, key=lambda task: task.time)

    def filter_by_completion(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Filter tasks by whether they are completed."""
        return [task for task in tasks if task.completed == completed]

    def filter_by_pet_name(self, pet_name: str) -> list[Task]:
        """Return tasks for any pet whose name matches `pet_name`."""
        target = pet_name.strip().lower()
        matches: list[Task] = []
        for pet in self.owner.get_pets():
            if pet.name.strip().lower() == target:
                matches.extend(pet.get_tasks())
        return matches

    @staticmethod
    def _parse_time(value: str) -> time:
        """Convert 'HH:MM' into a `time` so it sorts correctly."""
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
        """Return all (pet, task) pairs for this owner."""
        pairs: list[tuple[Pet, Task]] = []
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                pairs.append((pet, task))
        return pairs

    def generate_daily_schedule(self, *, include_completed: bool = False) -> list[tuple[str, Pet, Task]]:
        """
        Build a daily schedule.

        How it chooses tasks (simple + beginner-friendly):
        - Optionally exclude completed tasks.
        - Sort by priority first (1 highest), then by time.
        - If the owner set `available_time_minutes` (> 0), only include tasks that fit.
        """
        candidates: list[tuple[Pet, Task]] = []
        for pet, task in self.get_all_tasks():
            if (not include_completed) and task.completed:
                continue
            candidates.append((pet, task))

        candidates.sort(
            key=lambda pt: (
                getattr(pt[1], "priority", 3),
                self._parse_time(pt[1].time),
            )
        )

        limit = int(getattr(self.owner, "available_time_minutes", 0) or 0)
        minutes_used = 0

        chosen: list[tuple[str, Pet, Task]] = []
        skipped_for_time: int = 0
        for pet, task in candidates:
            duration = int(getattr(task, "duration_minutes", 15) or 0)
            duration = max(0, duration)

            if limit > 0 and (minutes_used + duration) > limit:
                skipped_for_time += 1
                continue

            chosen.append((task.time, pet, task))
            minutes_used += duration

        # Final display order: time-based so it reads like a day plan.
        chosen.sort(key=lambda x: self._parse_time(x[0]))

        self._last_schedule = chosen

        if limit > 0:
            self._last_explanation = (
                f"Tasks were picked by priority (1 highest) and then fit into your available time "
                f"({limit} minutes). The final schedule is shown in time order for readability. "
                f"Planned {minutes_used} minute(s); skipped {skipped_for_time} task(s) that did not fit."
            )
        else:
            self._last_explanation = (
                "Tasks were collected from all pets, then the schedule was shown in time order so it "
                "follows a simple, easy-to-follow day (earliest tasks first)."
            )

        return list(chosen)

    def explain_schedule(self) -> str:
        """Explain why the most recent schedule was chosen."""
        if not self._last_schedule:
            return "No schedule has been generated yet (or there were no tasks to schedule)."
        return self._last_explanation

    def detect_time_conflicts(
        self,
        schedule: Optional[list[tuple[str, Pet, Task]]] = None,
        *,
        include_completed: bool = False,
    ) -> list[str]:
        """Return warnings for tasks that share the exact same 'HH:MM' time."""
        if schedule is None:
            schedule = self.generate_daily_schedule(include_completed=include_completed)

        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for task_time, pet, task in schedule:
            key = (task_time or "").strip()
            by_time.setdefault(key, []).append((pet, task))

        warnings: list[str] = []
        for task_time, items in sorted(by_time.items(), key=lambda x: self._parse_time(x[0])):
            if len(items) <= 1:
                continue

            details = ", ".join(f"{pet.name}: {task.description}" for pet, task in items)
            warnings.append(f"Conflict at {task_time}: {details}")

        return warnings

