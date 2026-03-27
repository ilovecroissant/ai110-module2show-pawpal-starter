# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PawPal+** is a Python/Streamlit pet care planning assistant (Module 2 educational project). The starter app provides only a UI scaffold — the scheduling backend must be designed and implemented by the developer.

## Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run tests
pytest

# Run a single test file
pytest tests/test_scheduler.py

# Run a single test
pytest tests/test_scheduler.py::test_function_name
```

## Architecture

This is a **starter project** — only `app.py` and `requirements.txt` exist. The developer must build the backend and wire it up.

**Tech stack:** Python 3, Streamlit (>=1.30), pytest (>=7.0)

### Intended design

The system should have three layers:

1. **Data models** — Python classes for `Pet`, `Owner`, and `Task` (title, duration, priority). Tasks stored in Streamlit `st.session_state` for the demo UI.

2. **Scheduler** — Core algorithm that takes an owner, pet, and list of tasks, then produces an ordered daily plan based on priority and constraints (time available, preferences).

3. **UI** (`app.py`) — Streamlit frontend. Currently has input widgets and a placeholder "Generate schedule" button. The button should call your scheduler and display results once implemented.

### Suggested workflow (from README)

1. Draft a UML diagram (classes, attributes, methods, relationships)
2. Convert UML into Python class stubs (no logic)
3. Implement scheduling logic in small increments
4. Add pytest tests for key scheduling behaviors
5. Connect backend to `app.py` and display the plan + reasoning
6. Refine UML to match what was actually built

### Key integration point

`app.py:76` — the "Generate schedule" `st.button` handler is where scheduler logic should be called. Tasks are available as `st.session_state.tasks` (list of dicts with `title`, `duration_minutes`, `priority`).
