import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

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

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "selected_pet_id" not in st.session_state:
    st.session_state.selected_pet_id = None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)
else:
    # If you ever replace/update the owner object, make sure the scheduler points at it.
    st.session_state.scheduler.owner = st.session_state.owner

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
                    )
                    pet.add_task(task)
                    st.session_state.next_task_id = int(st.session_state.next_task_id) + 1
                    st.success(f"Added task for {pet.name}.")
                    st.rerun()
                except Exception:
                    st.error("Sorry—something went wrong while adding that task. Please try again.")

    def _time_sort_key(value: str) -> tuple[int, int, str]:
        try:
            hh, mm = value.strip().split(":")
            return (int(hh), int(mm), "")
        except Exception:
            return (99, 99, value)

    st.markdown("#### Current pets & tasks")
    pets_for_display = st.session_state.owner.get_pets()
    if not pets_for_display:
        st.info("No pets yet. Add one above.")
    else:
        for p in pets_for_display:
            st.markdown(f"**{p.name}**  \n{p.species}, {p.age} year(s) (id={p.pet_id})")
            tasks = sorted(p.get_tasks(), key=lambda t: _time_sort_key(t.time))
            if not tasks:
                st.caption("No tasks yet.")
            else:
                st.table(
                    [
                        {
                            "time": t.time,
                            "task": t.description,
                            "frequency": t.frequency,
                            "completed": t.completed,
                        }
                        for t in tasks
                    ]
                )
            st.divider()

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a simple daily schedule from all pets' tasks.")

if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = []
if "last_schedule_explanation" not in st.session_state:
    st.session_state.last_schedule_explanation = ""

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
    st.table(
        [
            {
                "time": task_time,
                "pet": pet.name,
                "task": task.description,
                "frequency": task.frequency,
                "completed": task.completed,
            }
            for (task_time, pet, task) in schedule
        ]
    )

    st.markdown("#### Daily plan (easy to read)")
    for task_time, pet, task in schedule:
        status = "done" if task.completed else "to do"
        st.markdown(f"- **{task_time}** — **{pet.name}**: {task.description} ({task.frequency}, {status})")

    explanation = st.session_state.last_schedule_explanation
    if explanation:
        st.markdown("#### Why this schedule?")
        st.write(explanation)
