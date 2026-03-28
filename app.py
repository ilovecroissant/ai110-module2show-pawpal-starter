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
    st.write("Your pets:")
    st.table([{"Name": p.name, "Type": p.animal_type, "Color": p.color} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

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
        st.write("Current tasks:")
        st.table([
            {
                "Pet": t.pet.name,
                "Task": t.title,
                "Start": t.start_time,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.name,
                "Done": t.completed,
            }
            for t in owner.all_tasks
        ])
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
        schedule = scheduler.generate_daily_schedule()

        st.success(f"Today's plan for {owner.name} — {scheduler.total_time_minutes()} min total")
        for task in scheduler.sort_by_time():
            st.markdown(f"- **{task.start_time}** [{task.priority.name}] {task.pet.name}: {task.title} ({task.duration_minutes} min)")
