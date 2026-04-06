import re

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ is a pet care planning assistant. Add pets, add care tasks, and generate a daily plan.

This demo connects a Streamlit UI to a small scheduling backend (see `pawpal_system.py`).
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Time available today (minutes)",
    min_value=0,
    max_value=1440,
    value=60,
    help="If this is 0, PawPal+ will include all tasks. Otherwise it tries to fit tasks into this time.",
)

# ---------------------------
# Persist "backend" objects
# ---------------------------
# Streamlit reruns this file top-to-bottom on every interaction.
# To keep important objects (like your Owner/Pet/Scheduler) from being recreated each rerun,
# store them in `st.session_state` and only create them if they don't exist yet.

DEFAULT_OWNER_ID = 1

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id=DEFAULT_OWNER_ID, name=owner_name)

# Keep the stored Owner in sync with the UI inputs (without recreating it).
st.session_state.owner.name = owner_name
st.session_state.owner.available_time_minutes = int(available_minutes)

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "selected_pet_id" not in st.session_state:
    st.session_state.selected_pet_id = None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)
else:
    # Keep the scheduler pointing at the current owner.
    st.session_state.scheduler.owner = st.session_state.owner

# If you update `pawpal_system.py`, Streamlit may keep an older Scheduler instance in session state.
# If it doesn't have the expected methods, recreate it so the UI matches the latest backend.
if not hasattr(st.session_state.scheduler, "generate_daily_schedule") or not hasattr(
    st.session_state.scheduler, "sort_by_time"
):
    st.session_state.scheduler = Scheduler(st.session_state.owner)

st.markdown("### Pets")
st.caption("Add pets using the form below. Pets are stored on the Owner in session state.")

with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    new_age = st.number_input("Age (years)", min_value=0, max_value=100, value=0)
    submitted = st.form_submit_button("Add pet")

if submitted:
    name_clean = new_pet_name.strip()
    if not name_clean:
        st.warning("Please enter a pet name.")
    else:
        try:
            pet = Pet(
                pet_id=int(st.session_state.next_pet_id),
                name=name_clean,
                species=new_species,
                age=int(new_age),
                owner_id=st.session_state.owner.owner_id,
            )
            st.session_state.owner.add_pet(pet)
            st.session_state.next_pet_id = int(st.session_state.next_pet_id) + 1
            st.session_state.selected_pet_id = pet.pet_id
            st.success(f"Added {pet.name}.")
            st.rerun()
        except Exception:
            st.error("Sorry—something went wrong while adding that pet. Please try again.")

pets = st.session_state.owner.get_pets()
if pets:
    st.write(f"Current pets: {len(pets)}")
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks for a specific pet. Tasks are stored on each `Pet` in session state.")

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

pets = st.session_state.owner.get_pets()
if not pets:
    st.info("Add a pet first, then you can add tasks.")
else:
    # Pick a pet to attach the new task to.
    pet_options = {f"{p.name} (id={p.pet_id})": p.pet_id for p in pets}
    default_pet_id = st.session_state.selected_pet_id or pets[0].pet_id
    default_pet_label = next(
        (label for label, pet_id in pet_options.items() if pet_id == default_pet_id),
        list(pet_options.keys())[0],
    )
    selected_pet_label = st.selectbox(
        "Which pet is this task for?",
        options=list(pet_options.keys()),
        index=list(pet_options.keys()).index(default_pet_label),
    )
    selected_pet_id = int(pet_options[selected_pet_label])
    st.session_state.selected_pet_id = selected_pet_id

    with st.form("add_task_form", clear_on_submit=True):
        task_description = st.text_input("Task description", value="")
        task_time = st.text_input("Time (HH:MM)", value="07:30")
        task_frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"], index=0)
        task_duration = st.number_input("Duration (minutes)", min_value=0, max_value=600, value=15)
        task_priority = st.selectbox(
            "Priority (1 = highest)",
            options=[1, 2, 3, 4, 5],
            index=2,
            help="Higher priority tasks are picked first when time is limited.",
        )
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        description_clean = task_description.strip()
        time_clean = task_time.strip()
        if not description_clean:
            st.warning("Please enter a task description.")
        elif not time_clean:
            st.warning("Please enter a time like 07:30.")
        else:
            pet = st.session_state.owner.get_pet(selected_pet_id)
            if pet is None:
                st.warning("That pet was not found. Please pick a pet again.")
            else:
                try:
                    task = Task(
                        task_id=int(st.session_state.next_task_id),
                        description=description_clean,
                        time=time_clean,
                        frequency=task_frequency,
                        duration_minutes=int(task_duration),
                        priority=int(task_priority),
                    )
                    pet.add_task(task)
                    st.session_state.next_task_id = int(st.session_state.next_task_id) + 1
                    st.success(f"Added task for {pet.name}.")
                    st.rerun()
                except Exception:
                    st.error("Sorry—something went wrong while adding that task. Please try again.")

    st.markdown("#### Current pets & tasks")
    filter_pet_name = st.text_input("Filter tasks by pet name (optional)", value="")
    pets_for_display = st.session_state.owner.get_pets()
    if not pets_for_display:
        st.info("No pets yet. Add one above.")
    else:
        st.caption("Tasks are shown in time order (sorted using the Scheduler).")
        filter_clean = filter_pet_name.strip()
        if filter_clean:
            filtered_tasks = st.session_state.scheduler.filter_by_pet_name(filter_clean)
            filtered_tasks = st.session_state.scheduler.sort_by_time(filtered_tasks)
            if not filtered_tasks:
                st.info("No tasks found for that pet name. Tip: the match is exact (example: “Luna”).")
            else:
                st.success(f"Found {len(filtered_tasks)} task(s) for “{filter_clean}”.")
                with st.expander("Filtered results", expanded=True):
                    st.table(
                        [
                            {
                                "Time": t.time,
                                "Task": t.description,
                                "Frequency": t.frequency,
                                "Duration (min)": getattr(t, "duration_minutes", 0),
                                "Priority": getattr(t, "priority", ""),
                                "Status": "Done" if t.completed else "To do",
                            }
                            for t in filtered_tasks
                        ]
                    )
            st.divider()

        st.markdown("#### Mark a task complete (shows recurring tasks)")
        all_tasks: list[tuple[int, int, str]] = []
        for pet in pets_for_display:
            for t in pet.get_tasks():
                label = f"{pet.name} • id={t.task_id} • {t.time} • {t.description}"
                all_tasks.append((pet.pet_id, t.task_id, label))

        if all_tasks:
            label_to_ids = {label: (pet_id, task_id) for (pet_id, task_id, label) in all_tasks}
            selected_label = st.selectbox("Pick a task", options=list(label_to_ids.keys()))
            if st.button("Mark selected task complete"):
                pet_id, task_id = label_to_ids[selected_label]
                pet = st.session_state.owner.get_pet(int(pet_id))
                if pet is None:
                    st.error("Pet not found. Try again.")
                else:
                    ok = pet.complete_task(int(task_id))
                    if ok:
                        st.success("Task marked complete. If it was daily/weekly, the next occurrence was created.")
                        st.rerun()
                    else:
                        st.error("Task not found. Try again.")
        else:
            st.caption("No tasks yet to complete.")
        st.divider()

        for p in pets_for_display:
            st.markdown(f"**{p.name}**  \n{p.species}, {p.age} year(s) (id={p.pet_id})")
            tasks = st.session_state.scheduler.sort_by_time(p.get_tasks())
            if not tasks:
                st.caption("No tasks yet.")
            else:
                done_count = sum(1 for t in tasks if t.completed)
                todo_count = len(tasks) - done_count
                st.info(f"{todo_count} to do • {done_count} done")
                st.table(
                    [
                        {
                            "Time": t.time,
                            "Task": t.description,
                            "Frequency": t.frequency,
                            "Duration (min)": getattr(t, "duration_minutes", 0),
                            "Priority": getattr(t, "priority", ""),
                            "Status": "Done" if t.completed else "To do",
                        }
                        for t in tasks
                    ]
                )
            st.divider()

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily schedule from all pets' tasks (fits into available minutes if set).")

if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = []
if "last_schedule_explanation" not in st.session_state:
    st.session_state.last_schedule_explanation = ""
if "last_schedule_conflicts" not in st.session_state:
    st.session_state.last_schedule_conflicts = []

include_completed = st.checkbox("Include completed tasks", value=False)

if st.button("Generate schedule"):
    # Use the backend `Scheduler` logic, based on the pets/tasks stored in session state.
    try:
        st.session_state.last_schedule = st.session_state.scheduler.generate_daily_schedule(
            include_completed=include_completed
        )
        if hasattr(st.session_state.scheduler, "explain_schedule") and callable(
            getattr(st.session_state.scheduler, "explain_schedule")
        ):
            st.session_state.last_schedule_explanation = (
                st.session_state.scheduler.explain_schedule()
            )
        else:
            st.session_state.last_schedule_explanation = ""

        # Optional "smart scheduling" feedback: detect time conflicts.
        if hasattr(st.session_state.scheduler, "detect_time_conflicts") and callable(
            getattr(st.session_state.scheduler, "detect_time_conflicts")
        ):
            st.session_state.last_schedule_conflicts = (
                st.session_state.scheduler.detect_time_conflicts(
                    st.session_state.last_schedule,
                    include_completed=include_completed,
                )
            )
        else:
            st.session_state.last_schedule_conflicts = []

        if st.session_state.last_schedule:
            st.success("Schedule generated.")
        else:
            st.info("No tasks matched your current options, so there’s nothing to schedule yet.")
        st.rerun()
    except Exception:
        st.error("Sorry—something went wrong while generating the schedule. Please try again.")

schedule = st.session_state.last_schedule
if not schedule:
    st.info("No schedule yet. Add tasks, then click Generate schedule.")
else:
    st.markdown("#### Today's schedule")
    conflicts = st.session_state.last_schedule_conflicts or []
    if conflicts:
        st.warning(
            "Scheduling conflicts detected. This usually means two tasks are set for the same time. "
            "Consider moving one task a few minutes earlier/later."
        )
        conflict_rows = []
        for msg in conflicts:
            # Expected format from Scheduler: "Conflict at HH:MM: details..."
            text = (msg or "").strip()
            m = re.match(r"^Conflict at (\d{1,2}:\d{2}):\s*(.*)$", text, flags=re.I)
            if m:
                task_time = m.group(1)
                details_clean = m.group(2).strip()
            else:
                task_time = ""
                details_clean = text

            conflict_rows.append(
                {"Time": task_time, "Conflicting tasks": details_clean}
            )

        with st.expander("View conflict details", expanded=True):
            st.table(conflict_rows)
    else:
        st.success("No scheduling conflicts detected.")

    st.table(
        [
            {
                "Time": task_time,
                "Pet": pet.name,
                "Task": task.description,
                "Frequency": task.frequency,
                "Duration (min)": getattr(task, "duration_minutes", 0),
                "Priority": getattr(task, "priority", ""),
                "Status": "Done" if task.completed else "To do",
            }
            for (task_time, pet, task) in schedule
        ]
    )

    st.markdown("#### Daily plan (easy to read)")
    for task_time, pet, task in schedule:
        status = "done" if task.completed else "to do"
        dur = getattr(task, "duration_minutes", 0)
        pri = getattr(task, "priority", "")
        st.markdown(
            f"- **{task_time}** — **{pet.name}**: {task.description} "
            f"({task.frequency}, {dur} min, priority {pri}, {status})"
        )

    explanation = st.session_state.last_schedule_explanation
    if explanation:
        st.markdown("#### Why this schedule?")
        st.write(explanation)
