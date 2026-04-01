from __future__ import annotations

from datetime import time as dt_time

from pawpal_system import Owner, Pet, Scheduler, Task


def format_time_12h(value: str) -> str:
    """
    Convert "HH:MM" (24-hour) into "HH:MM AM/PM".
    If the time can't be parsed, return the original string.
    """
    try:
        parts = value.strip().split(":")
        if len(parts) != 2:
            return value
        hour = int(parts[0])
        minute = int(parts[1])
        return dt_time(hour=hour, minute=minute).strftime("%I:%M %p")
    except Exception:
        return value


def friendly_task_text(pet: Pet, task: Task) -> str:
    desc = task.description.strip()
    if pet.name.lower() in desc.lower():
        return desc
    return f"{desc} {pet.name}"


def print_schedule(owner: Owner, schedule: list[tuple[str, Pet, Task]]) -> None:
    print("Today's Schedule:")
    if not schedule:
        print("No tasks scheduled for today.")
        return

    for task_time, pet, task in schedule:
        task_text = friendly_task_text(pet, task)
        time_text = format_time_12h(task_time)
        print(f"- {time_text} | {task_text} | {pet.species} | {task.frequency.title()}")


def main() -> None:
    # 1) Create an owner
    owner = Owner(owner_id=1, name="Alex")

    # 2) Create at least 2 pets
    luna = Pet(pet_id=101, name="Luna", species="Cat", age=3, owner_id=owner.owner_id)
    max_pet = Pet(pet_id=102, name="Max", species="Dog", age=5, owner_id=owner.owner_id)

    # 3) Add the pets to the owner
    owner.add_pet(luna)
    owner.add_pet(max_pet)

    # 4) Create at least 3 tasks with different times
    breakfast = Task(task_id=1, description="Feed", time="08:00", frequency="daily")
    walk = Task(task_id=2, description="Walk", time="12:00", frequency="daily")
    meds = Task(task_id=3, description="Give medicine to", time="18:00", frequency="once")

    # 5) Add tasks to the pets
    luna.add_task(breakfast)
    max_pet.add_task(walk)
    luna.add_task(meds)

    # 6) Use the Scheduler to generate a daily schedule
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_daily_schedule()

    # 7) Print to the terminal in a clean format
    print_schedule(owner, schedule)


if __name__ == "__main__":
    main()

