from pawpal_system import Pet, Task, Priority


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
