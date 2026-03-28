from pawpal_system import Owner, Pet, Task, Scheduler, Priority

# --- Setup ---
owner = Owner(name="Alex")

dog = Pet(name="Buddy", animal_type="Dog", age=3, color="Golden")
cat = Pet(name="Luna", animal_type="Cat", age=5, color="Gray")

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks added OUT OF ORDER (intentionally scrambled times) ---
owner.add_task(dog, Task("Evening walk",      duration_minutes=30, priority=Priority.HIGH,   pet=dog, start_time="18:00"))
owner.add_task(dog, Task("Feed breakfast",    duration_minutes=10, priority=Priority.HIGH,   pet=dog, start_time="07:30"))
owner.add_task(dog, Task("Brush coat",        duration_minutes=15, priority=Priority.LOW,    pet=dog, start_time="12:00"))
owner.add_task(dog, Task("Morning walk",      duration_minutes=30, priority=Priority.HIGH,   pet=dog, start_time="08:00"))

owner.add_task(cat, Task("Playtime",          duration_minutes=20, priority=Priority.MEDIUM, pet=cat, start_time="19:00"))
owner.add_task(cat, Task("Clean litter box",  duration_minutes=10, priority=Priority.HIGH,   pet=cat, start_time="09:00"))
owner.add_task(cat, Task("Evening feed",      duration_minutes=10, priority=Priority.HIGH,   pet=cat, start_time="17:30"))

# --- Intentional conflicts for testing detect_conflicts() ---
# Conflict 1 (same pet): "Vet check" starts at 08:00, overlaps Buddy's "Morning walk" (08:00–08:30)
owner.add_task(dog, Task("Vet check",         duration_minutes=20, priority=Priority.HIGH,   pet=dog, start_time="08:00"))
# Conflict 2 (cross-pet): "Groom Luna" starts at 07:35, overlaps Buddy's "Feed breakfast" (07:30–07:40)
owner.add_task(cat, Task("Groom Luna",        duration_minutes=15, priority=Priority.LOW,    pet=cat, start_time="07:35"))

scheduler = Scheduler(owner=owner, pets=owner.pets)

# Mark "Brush coat" complete via scheduler so the next occurrence is auto-created
brush_coat = owner.all_tasks[2]   # "Brush coat"
next_task = scheduler.complete_task(brush_coat)
if next_task:
    print(f"Auto-scheduled next occurrence: '{next_task.title}' due {next_task.due_date}")


def print_tasks(label: str, tasks: list) -> None:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    if not tasks:
        print("  (no tasks)")
        return
    for t in tasks:
        status = "X" if t.completed else " "
        print(f"  [{status}] {t.start_time}  {t.pet.name:<6}  {t.title:<22}  {t.duration_minutes} min  |  {t.priority.name}")


# 1. Sorted by time (all pending tasks, chronological)
print_tasks("Sorted by start time — pending only", scheduler.sort_by_time())

# 2. Filter: completed tasks only
print_tasks("Completed tasks", scheduler.filter_tasks(completed=True))

# 3. Filter: all of Buddy's tasks
print_tasks("All tasks for Buddy", scheduler.filter_tasks(pet_name="Buddy"))

# 4. Filter: Luna's pending tasks only
print_tasks("Luna's pending tasks", scheduler.filter_tasks(completed=False, pet_name="Luna"))

print(f"\nTotal pending time: {scheduler.total_time_minutes()} minutes")

# 5. Conflict detection
print(f"\n{'='*50}")
print("  Scheduling conflicts")
print(f"{'='*50}")
conflicts = scheduler.detect_conflicts()
if not conflicts:
    print("  (no conflicts)")
else:
    for a, b in conflicts:
        print(f"  CONFLICT: [{a.pet.name}] {a.title} ({a.start_time}, {a.duration_minutes} min)"
              f"  <->  [{b.pet.name}] {b.title} ({b.start_time}, {b.duration_minutes} min)")
