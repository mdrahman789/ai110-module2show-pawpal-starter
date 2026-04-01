from __future__ import annotations

from pawpal_system import Owner, Pet, Scheduler, Task


def make_owner_with_pet() -> tuple[Owner, Pet]:
    owner = Owner(owner_id=1, name="Jordan")
    pet = Pet(pet_id=1, name="Luna", species="dog", age=3, owner_id=owner.owner_id)
    owner.add_pet(pet)
    return owner, pet


def test_conflict_detection_exact_same_time() -> None:
    owner, pet = make_owner_with_pet()
    pet.add_task(Task(task_id=1, description="Walk", time="07:30", frequency="daily"))
    pet.add_task(Task(task_id=2, description="Feed", time="07:30", frequency="daily"))

    scheduler = Scheduler(owner)
    schedule = scheduler.generate_daily_schedule()
    conflicts = scheduler.detect_time_conflicts(schedule)

    assert conflicts
    assert any("Conflict at 07:30" in msg for msg in conflicts)


def test_recurring_task_created_when_completed_daily() -> None:
    owner, pet = make_owner_with_pet()
    pet.add_task(
        Task(
            task_id=1,
            description="Medicine",
            time="08:00",
            frequency="daily",
            duration_minutes=5,
            priority=1,
        )
    )

    ok = pet.complete_task(1)
    assert ok is True

    tasks = pet.get_tasks()
    assert any(t.task_id == 1 and t.completed for t in tasks)
    assert any(
        (t.task_id != 1)
        and (t.description == "Medicine")
        and (t.frequency == "daily")
        and (t.completed is False)
        for t in tasks
    )


def test_schedule_fits_into_available_minutes_uses_priority() -> None:
    owner, pet = make_owner_with_pet()
    owner.available_time_minutes = 20

    # Total duration would be 35 minutes; only some should fit.
    pet.add_task(Task(task_id=1, description="High priority short", time="09:00", duration_minutes=10, priority=1))
    pet.add_task(Task(task_id=2, description="Low priority long", time="08:00", duration_minutes=25, priority=5))
    pet.add_task(Task(task_id=3, description="Medium priority short", time="07:00", duration_minutes=10, priority=3))

    scheduler = Scheduler(owner)
    schedule = scheduler.generate_daily_schedule()

    # Should fit two 10-min tasks; the 25-min one should be skipped.
    scheduled_descriptions = [task.description for _, _, task in schedule]
    assert "Low priority long" not in scheduled_descriptions
    assert "High priority short" in scheduled_descriptions
    assert "Medium priority short" in scheduled_descriptions

    # Display order should be time order (07:00 then 09:00).
    scheduled_times = [t for (t, _, _) in schedule]
    assert scheduled_times == sorted(scheduled_times)

