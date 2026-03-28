# PawPal+ Project Reflection

## 1. System Design
Three core actions:
    1. Enter owner name and pet info
    2. Add/ edit tasks
    3. Generate daily schedule

Four objects:
    1. Owner
        Attributes: Name
        Methods: 
    2. Pet
        Attributes: animal_type, age, color
        Methods: add_pet
    3. Task
        Attributes:
        Methods: add_task, edit_task
    4. Scheduler
        Attributes:
        Methods: generate_daily_schedule

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I chose 4 classes: Owner, Pet, Task, Scheduler
    1. Owner: Have information about the Owner
    2. Pet: data container for pets
    3. Task: data container for tasks
    4. Scheduler: To keep track of the Owner, their Pet and the tasks assigned

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design change during implementation. I added Priority enum:

Replaced the raw String priority field on Task with a Priority enum (HIGH, MEDIUM, LOW). A plain string has no constraints — someone could pass "urgent" or "banana" and the scheduler would either crash or silently produce a wrong order when sorting. The enum makes invalid values impossible at the code level and gives generate_daily_schedule a reliable way to compare and sort tasks.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two main constraints: **time windows** and **priority**. Every task has a `start_time` (HH:MM) and a `duration_minutes`, so the scheduler knows exactly when each task occupies the calendar. Priority (HIGH, MEDIUM, LOW) is used to sort tasks in `generate_daily_schedule`, and time is used to sort in `sort_by_time` for the displayed schedule. `detect_conflicts` enforces the time constraint by flagging any two pending tasks whose windows overlap.

I decided time-window validity mattered most because a schedule with collisions is useless in practice — the owner simply cannot do two things at once. Priority matters second because it communicates urgency (e.g., medication before grooming), but it does not automatically resolve conflicts; the owner decides. Frequency ("daily" vs "once") also acts as a lightweight filter: `generate_daily_schedule` only surfaces daily tasks, so one-off tasks like a vet visit don't clutter the recurring view.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The conflict detector checks whether two tasks' *time windows overlap* (start time + duration) rather than only flagging exact same-start-time matches. This means a task starting at 07:35 is correctly flagged as conflicting with one that started at 07:30 and runs for 10 minutes (ending at 07:40), even though their start times differ.

The tradeoff is that the scheduler treats every conflict as equally urgent — it does not distinguish between a 1-minute overlap and a full 30-minute collision, and it does not attempt to automatically resolve conflicts by reordering tasks. For a demo app where the owner manually reviews the schedule, this is reasonable: surfacing all overlaps as warnings gives the owner full visibility without the scheduler making assumptions about which task to move. A production scheduler might rank conflicts by severity or auto-shift lower-priority tasks, but that added complexity is unnecessary here.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI at three stages. First, during **design brainstorming**: I described the problem in plain English ("I need a pet care scheduler with owners, pets, and tasks") and asked what classes made sense. This helped me arrive at the four-class design quickly instead of staring at a blank file. Second, during **implementation**: I asked for help writing the conflict-detection logic — specifically how to represent time windows as integer minutes so overlaps could be checked with simple arithmetic. Third, during **testing**: I asked "what edge cases should I test for a conflict detector?" which surfaced the back-to-back (non-overlapping) case and the completed-task case that I might have missed.

The most helpful prompt pattern was **concrete + constrained**: "given these two tasks with start times and durations, write a function that returns True if they overlap." Vague prompts like "help me with scheduling" produced generic code that didn't fit the data model.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked for help with `complete_task`, the AI's first suggestion simply called `task.mark_complete()` and returned `None`. It did not handle recurrence at all. I pushed back because the design doc called for recurring tasks — completing a daily walk should automatically add tomorrow's walk, not just mark today's done. I asked specifically: "how do I create a copy of the task with the due_date advanced by one day?" The AI then suggested `dataclasses.replace()`, which was the right tool. I verified it by writing `test_complete_daily_task_creates_next_day_occurrence`: the test checks that `next_task.due_date == today + timedelta(days=1)` and that the new task appears in `pet.tasks`. Running `pytest` confirmed the behavior was correct before I moved on.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested six behaviors across three categories:

1. **Core data model** — `test_mark_complete_changes_status` and `test_add_task_increases_pet_task_count` verify that the building blocks work. These matter because every scheduler method depends on `completed` being set correctly and tasks actually living on the pet.

2. **Sorting** — `test_sort_by_time_returns_chronological_order` checks that three tasks with different start times come back in the right order, and `test_sort_by_time_excludes_completed_tasks` checks that done tasks are filtered out. These are important because the UI renders the schedule from `sort_by_time`; a wrong order or a stale completed task showing up would confuse the user.

3. **Recurrence** — `test_complete_daily_task_creates_next_day_occurrence` and `test_complete_once_task_returns_none_and_no_new_task` verify the two branches of `complete_task`. Without these, a bug in recurrence logic could silently flood the pet's task list or fail to create the next day's entry.

4. **Conflict detection** — `test_detect_conflicts_flags_overlapping_tasks`, `test_detect_conflicts_no_false_positive_for_back_to_back`, and `test_detect_conflicts_ignores_completed_tasks` cover the true-positive, boundary, and false-positive cases. The boundary test (back-to-back tasks must NOT conflict) was especially important because an off-by-one error (`<=` vs `<`) in the overlap formula would silently break it.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm confident in the behaviors that are tested, but I know there are gaps. All 9 tests pass and they cover the main happy paths and a few boundary cases. However, if I had more time I would test:

- **Cross-pet conflicts**: both conflict tests use a single pet. A conflict between a task for "Buddy" and a task for "Luna" assigned to the same owner should also be detected — the code says it handles this but I haven't verified it with a test.
- **Midnight wrap-around**: a task at 23:45 for 30 minutes runs until 00:15 the next day. The current `to_minutes` arithmetic doesn't handle this and would silently produce a wrong result.
- **Invalid start_time format**: if a user types "8:00" instead of "08:00", `datetime.strptime` raises an exception. The app should validate input before creating a Task.
- **Weekly recurrence advancing due_date by 7 days**: the code supports "weekly" but there is no test for it.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the conflict-detection logic. The `detect_conflicts` method is short (about 15 lines), but it handles a non-trivial problem: checking every pair of pending tasks for time-window overlap in O(n²) time without double-counting pairs. Using the standard interval-overlap condition `a_start < b_end AND b_start < a_end` — and converting "HH:MM" strings to integer minutes once per task — kept the logic readable. The fact that the boundary test (`test_detect_conflicts_no_false_positive_for_back_to_back`) passes gives me extra confidence that the formula is exactly right and not off-by-one.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add **input validation to the Task dataclass**. Right now, nothing stops a caller from creating a Task with `duration_minutes=-5` or `start_time="banana"`. A `__post_init__` method could raise a `ValueError` for invalid data immediately at creation time rather than letting bad data silently propagate until `detect_conflicts` crashes. I would also persist tasks between sessions (Streamlit resets `session_state` on refresh), likely by saving to a JSON file. In the current state, every page reload wipes all pets and tasks, which makes it hard to use as a real planning tool even for a demo.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that **AI is a fast first draft, not a final answer**. The AI could generate plausible-looking code for almost every method I asked about, but that code was rarely correct on the first try for the specific constraints of this system — it didn't know that tasks have a `frequency` field, that conflict detection should exclude completed tasks, or that recurrence should use `dataclasses.replace` to avoid mutating the original. Every AI suggestion needed to be read carefully, compared against the actual data model, and verified with a test. The workflow that worked best was: describe the problem precisely → get a draft → run the tests → fix whatever broke. Skipping any of those steps produced subtle bugs that were hard to catch later.
