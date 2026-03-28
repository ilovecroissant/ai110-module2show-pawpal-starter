from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def test_mark_complete_changes_status():
    pet = Pet(name="Buddy", animal_type="Dog", age=3, color="Golden")
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, pet=pet)

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Luna", animal_type="Cat", age=5, color="Gray")
    task = Task(title="Clean litter box", duration_minutes=10, priority=Priority.HIGH, pet=pet)

    assert len(pet.tasks) == 0
    pet.add_task(task)
    assert len(pet.tasks) == 1


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order():
    """Tasks with different start times come back earliest-first."""
    pet = Pet(name="Buddy", animal_type="Dog", age=3, color="Golden")
    owner = Owner("Alice")
    owner.add_pet(pet)

    late  = Task(title="Evening walk",   duration_minutes=30, priority=Priority.HIGH,   pet=pet, start_time="18:00")
    early = Task(title="Morning walk",   duration_minutes=30, priority=Priority.HIGH,   pet=pet, start_time="07:00")
    mid   = Task(title="Afternoon play", duration_minutes=20, priority=Priority.MEDIUM, pet=pet, start_time="13:00")
    for t in (late, early, mid):
        pet.add_task(t)

    scheduler = Scheduler(owner, [pet])
    ordered = scheduler.sort_by_time()

    assert [t.start_time for t in ordered] == ["07:00", "13:00", "18:00"]


def test_sort_by_time_excludes_completed_tasks():
    """Completed tasks must not appear in sort_by_time results."""
    pet = Pet(name="Mochi", animal_type="Cat", age=2, color="White")
    owner = Owner("Bob")
    owner.add_pet(pet)

    done    = Task(title="Pill",  duration_minutes=5,  priority=Priority.HIGH, pet=pet, start_time="08:00", completed=True)
    pending = Task(title="Brush", duration_minutes=10, priority=Priority.LOW,  pet=pet, start_time="09:00")
    pet.add_task(done)
    pet.add_task(pending)

    scheduler = Scheduler(owner, [pet])
    result = scheduler.sort_by_time()

    assert len(result) == 1
    assert result[0].title == "Brush"


# --- Recurrence logic ---

def test_complete_daily_task_creates_next_day_occurrence():
    """Completing a daily task adds a new task due one day later."""
    pet = Pet(name="Rex", animal_type="Dog", age=5, color="Brown")
    owner = Owner("Carol")
    owner.add_pet(pet)

    today = date.today()
    walk = Task(
        title="Walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        pet=pet,
        frequency="daily",
        due_date=today,
    )
    pet.add_task(walk)

    scheduler = Scheduler(owner, [pet])
    next_task = scheduler.complete_task(walk)

    assert walk.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task in pet.tasks


def test_complete_once_task_returns_none_and_no_new_task():
    """Completing a one-off task must not create a follow-up."""
    pet = Pet(name="Nala", animal_type="Cat", age=4, color="Orange")
    owner = Owner("Dave")
    owner.add_pet(pet)

    vet = Task(title="Vet visit", duration_minutes=60, priority=Priority.HIGH, pet=pet, frequency="once")
    pet.add_task(vet)

    scheduler = Scheduler(owner, [pet])
    result = scheduler.complete_task(vet)

    assert result is None
    assert len(pet.tasks) == 1   # no new task added


# --- Conflict detection ---

def test_detect_conflicts_flags_overlapping_tasks():
    """Two pending tasks whose windows overlap must be reported as a conflict."""
    pet = Pet(name="Pip", animal_type="Dog", age=1, color="Black")
    owner = Owner("Eve")
    owner.add_pet(pet)

    # 09:00–09:30 overlaps with 09:15–09:45
    a = Task(title="Groom",    duration_minutes=30, priority=Priority.HIGH,   pet=pet, start_time="09:00")
    b = Task(title="Feed",     duration_minutes=30, priority=Priority.MEDIUM, pet=pet, start_time="09:15")
    pet.add_task(a)
    pet.add_task(b)

    scheduler = Scheduler(owner, [pet])
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert (a, b) in conflicts


def test_detect_conflicts_no_false_positive_for_back_to_back():
    """Tasks that touch but do not overlap must NOT be flagged."""
    pet = Pet(name="Zara", animal_type="Dog", age=2, color="White")
    owner = Owner("Frank")
    owner.add_pet(pet)

    # 08:00–08:30 ends exactly when 08:30 begins — no overlap
    a = Task(title="Walk",  duration_minutes=30, priority=Priority.HIGH, pet=pet, start_time="08:00")
    b = Task(title="Feed",  duration_minutes=30, priority=Priority.HIGH, pet=pet, start_time="08:30")
    pet.add_task(a)
    pet.add_task(b)

    scheduler = Scheduler(owner, [pet])
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks():
    """A completed task's window must not trigger a conflict."""
    pet = Pet(name="Koda", animal_type="Dog", age=6, color="Gray")
    owner = Owner("Grace")
    owner.add_pet(pet)

    done    = Task(title="Done task",    duration_minutes=60, priority=Priority.HIGH, pet=pet, start_time="09:00", completed=True)
    pending = Task(title="Pending task", duration_minutes=60, priority=Priority.HIGH, pet=pet, start_time="09:00")
    pet.add_task(done)
    pet.add_task(pending)

    scheduler = Scheduler(owner, [pet])
    assert scheduler.detect_conflicts() == []
