from pawpal_system import Owner, Pet, Task, Scheduler, Priority

# --- Setup ---
owner = Owner(name="Alex")

dog = Pet(name="Buddy", animal_type="Dog", age=3, color="Golden")
cat = Pet(name="Luna", animal_type="Cat", age=5, color="Gray")

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks for Buddy ---
owner.add_task(dog, Task("Morning walk",       duration_minutes=30, priority=Priority.HIGH,   pet=dog))
owner.add_task(dog, Task("Feed breakfast",     duration_minutes=10, priority=Priority.HIGH,   pet=dog))
owner.add_task(dog, Task("Brush coat",         duration_minutes=15, priority=Priority.LOW,    pet=dog))

# --- Tasks for Luna ---
owner.add_task(cat, Task("Clean litter box",   duration_minutes=10, priority=Priority.HIGH,   pet=cat))
owner.add_task(cat, Task("Playtime",           duration_minutes=20, priority=Priority.MEDIUM, pet=cat))

# --- Generate Schedule ---
scheduler = Scheduler(owner=owner, pets=owner.pets)
schedule = scheduler.generate_daily_schedule()

# --- Print Schedule ---
print(f"=== Today's Schedule for {owner.name} ===\n")

current_pet = None
for task in schedule:
    if task.pet != current_pet:
        current_pet = task.pet
        print(f"  {current_pet.name} ({current_pet.animal_type})")

    status = "X" if task.completed else " "
    print(f"    [{status}] {task.title:<25} {task.duration_minutes} min  |  {task.priority.name}")

print(f"\nTotal time: {scheduler.total_time_minutes()} minutes")
