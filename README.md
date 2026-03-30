# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling Features

PawPal+ includes several advanced scheduling capabilities:

**Recurring Task Management**
- Tasks support frequency levels: daily, weekly, monthly, as_needed
- Automatic `next_due_date` calculation using Python's `timedelta` — when a task is marked complete, the scheduler calculates when it will be due again
- Intelligent filtering with `get_due_tasks()` — only schedules tasks that are actually due today

**Time-Aware Scheduling**
- Sort tasks chronologically by `scheduled_time` (HH:MM format) using a readable key function
- Detect exact time conflicts — warns if multiple tasks are scheduled at the same time across all pets
- Prevent double-booking with `detect_time_conflicts()`

**Intelligent Prioritization**
- Greedy scheduling algorithm: high-priority tasks fit first; low-priority tasks may be dropped if time is tight
- Priority filtering with `filter_by_priority()` — view all high/medium/low priority tasks at a glance
- Clear reasoning for scheduling decisions — each plan includes explanations for why tasks were selected or rejected

**Conflict Detection** (lightweight, non-crashing)
- Duration conflicts: warns when total scheduled time exceeds owner's available time
- Time conflicts: warns when two tasks are scheduled for the exact same time (works across all pets)

## Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src="/course_images/ai110/pawpal_screenshot.png"></a>

<a href="/course_images/ai110/image-1.png" target="_blank"><img src="/course_images/ai110/image-1.png"></a>


