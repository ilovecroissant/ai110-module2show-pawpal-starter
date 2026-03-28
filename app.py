import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

# --- Owner Setup ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state or st.session_state.owner.name != owner_name:
    st.session_state.owner = Owner(name=owner_name)

owner = st.session_state.owner

# --- Add a Pet ---
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    pet_color = st.text_input("Color", value="Brown")

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, animal_type=species, age=0, color=pet_color)
    owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species}.")

if owner.pets:
    st.caption("Your pets")
    st.table([{"Name": p.name, "Type": p.animal_type, "Color": p.color} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

PRIORITY_BADGE = {"HIGH": "🔴 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🟢 LOW"}

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    pet_options = {p.name: p for p in owner.pets}

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_str = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"])
    with col4:
        start_time = st.text_input("Start time (HH:MM)", value="08:00")
    with col5:
        selected_pet_name = st.selectbox("For pet", list(pet_options.keys()))

    if st.button("Add task"):
        selected_pet = pet_options[selected_pet_name]
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=Priority[priority_str],
            start_time=start_time,
            pet=selected_pet,
        )
        owner.add_task(selected_pet, new_task)
        st.success(f"Added '{task_title}' for {selected_pet_name}.")

    if owner.all_tasks:
        st.caption("All tasks — click a column header to sort")
        st.dataframe(
            [
                {
                    "Pet": t.pet.name,
                    "Task": t.title,
                    "Start": t.start_time,
                    "Duration (min)": t.duration_minutes,
                    "Priority": PRIORITY_BADGE[t.priority.name],
                    "Done": t.completed,
                }
                for t in owner.all_tasks
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not owner.pets or not owner.all_tasks:
        st.warning("Add at least one pet and one task first.")
    else:
        scheduler = Scheduler(owner=owner, pets=owner.pets)

        pending_count   = len(scheduler.get_pending_tasks())
        completed_count = len(scheduler.get_completed_tasks())
        total_min       = scheduler.total_time_minutes()

        # Summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Pending tasks",   pending_count)
        m2.metric("Completed tasks", completed_count)
        m3.metric("Time remaining",  f"{total_min} min")

        # Conflict warnings
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for a, b in conflicts:
                st.warning(
                    f"Scheduling conflict: **{a.title}** ({a.start_time}, {a.duration_minutes} min) "
                    f"overlaps with **{b.title}** ({b.start_time}, {b.duration_minutes} min)"
                )
        else:
            st.success("No scheduling conflicts detected.")

        # Sorted pending task list with Done buttons
        st.caption("Today's schedule — sorted by start time")
        for task in scheduler.sort_by_time():
            col_badge, col_info, col_btn = st.columns([1, 5, 1])
            with col_badge:
                st.markdown(PRIORITY_BADGE[task.priority.name])
            with col_info:
                st.markdown(
                    f"**{task.start_time}** &nbsp; {task.pet.name}: {task.title} "
                    f"<span style='color:grey'>({task.duration_minutes} min)</span>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("Done", key=f"done_{id(task)}"):
                    scheduler.complete_task(task)
                    st.rerun()

        # Completed tasks
        if completed_count:
            with st.expander(f"Completed tasks ({completed_count})"):
                st.table([
                    {
                        "Pet": t.pet.name,
                        "Task": t.title,
                        "Start": t.start_time,
                        "Duration (min)": t.duration_minutes,
                    }
                    for t in scheduler.get_completed_tasks()
                ])
