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


def print_section(title: str) -> None:
    bar = "-" * len(title)
    print(f"\n{title}\n{bar}")


def print_task_list(items: list[tuple[Pet, Task]]) -> None:
    if not items:
        print("(none)")
        return

    for pet, task in items:
        status = "done" if task.completed else "to do"
        time_text = format_time_12h(task.time)
        task_text = friendly_task_text(pet, task)
        print(f"- {time_text} | {pet.name:<5} | {task_text:<22} | {status}")


def print_sorted_schedule_from_pairs(items: list[tuple[Pet, Task]]) -> None:
    if not items:
        print("(none)")
        return

    for pet, task in items:
        time_text = format_time_12h(task.time)
        status = "done" if task.completed else "to do"
        print(f"- {time_text} | {pet.name} | {friendly_task_text(pet, task)} ({status})")


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
    # Intentionally created and added out-of-order by time (to prove sorting works).
    dinner = Task(task_id=1, description="Feed", time="18:00", frequency="daily")
    early_walk = Task(task_id=2, description="Walk", time="07:15", frequency="daily")
    meds = Task(task_id=3, description="Give medicine to", time="12:05", frequency="once")
    nails = Task(task_id=4, description="Trim nails for", time="09:30", frequency="weekly")
    # Two tasks intentionally at the same exact time (to test conflict detection).
    breakfast = Task(task_id=5, description="Feed breakfast for", time="08:00", frequency="daily")
    training = Task(task_id=6, description="Training session for", time="08:00", frequency="weekly")

    # 5) Add tasks to the pets
    luna.add_task(dinner)        # 6:00 PM
    max_pet.add_task(early_walk) # 7:15 AM
    luna.add_task(meds)          # 12:05 PM
    max_pet.add_task(nails)      # 9:30 AM
    luna.add_task(breakfast)     # 8:00 AM (conflict)
    max_pet.add_task(training)   # 8:00 AM (conflict)

    # Mark one task complete so we can prove completion filtering works.
    nails.mark_complete()

    # 6) Use the Scheduler to generate a daily schedule
    scheduler = Scheduler(owner)

    # 7) Print to the terminal in a clean format
    raw_pairs = scheduler.get_all_tasks()
    pet_by_task_obj = {id(task): pet for pet, task in raw_pairs}

    print_section("Unsorted task setup (as added)")
    print_task_list(scheduler.get_all_tasks())

    print_section("Sorted schedule (using Scheduler.sort_by_time)")
    sorted_tasks = scheduler.sort_by_time([task for _, task in raw_pairs])
    sorted_pairs = [(pet_by_task_obj[id(task)], task) for task in sorted_tasks]
    print_sorted_schedule_from_pairs(sorted_pairs)

    print_section("Filtered results")
    print("Incomplete only (then sorted):")
    incomplete = scheduler.filter_by_completion([task for _, task in raw_pairs], completed=False)
    incomplete_sorted = scheduler.sort_by_time(incomplete)
    incomplete_pairs = [(pet_by_task_obj[id(task)], task) for task in incomplete_sorted]
    print_sorted_schedule_from_pairs(incomplete_pairs)

    print("\nPet name = Luna (then sorted):")
    luna_tasks = scheduler.filter_by_pet_name("Luna")
    luna_tasks_sorted = scheduler.sort_by_time(luna_tasks)
    luna_pairs = [(pet_by_task_obj[id(task)], task) for task in luna_tasks_sorted]
    print_sorted_schedule_from_pairs(luna_pairs)

    print_section("Daily schedule (Scheduler.generate_daily_schedule)")
    schedule = scheduler.generate_daily_schedule()
    print_schedule(owner, schedule)

    print_section("Conflict warnings (Scheduler.detect_time_conflicts)")
    warnings = scheduler.detect_time_conflicts(schedule)
    if not warnings:
        print("No exact-time conflicts found.")
    else:
        for msg in warnings:
            print(f"- WARNING: {msg}")


if __name__ == "__main__":
    main()

