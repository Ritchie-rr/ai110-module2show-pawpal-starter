#!/usr/bin/env python3
"""
Testing ground for PawPal+ system logic.
Verifies that Owner, Pet, Task, and Scheduler work correctly.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    print("=" * 60)
    print("🐾 PawPal+ System Test")
    print("=" * 60)
    print()

    # Create an Owner
    owner = Owner(name="Sarah", time_available=120, preferences=["morning walks", "play time"])
    print(f"Owner Created: {owner}")
    print()

    # Create Pets
    dog = Pet(name="Max", species="Golden Retriever")
    cat = Pet(name="Whiskers", species="Maine Coon")
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    print(f"Pets added: {dog}, {cat}")
    print()

    # Add Tasks to Dog (Max) - OUT OF ORDER intentionally to test sorting
    task1 = Task(
        title="Morning Walk",
        duration=30,
        priority="high",
        frequency="daily",
        scheduled_time="09:00",
        notes="Max needs 30min morning walk"
    )
    task2 = Task(
        title="Feeding",
        duration=10,
        priority="high",
        frequency="daily",
        scheduled_time="07:30",
        notes="Breakfast and dinner"
    )
    task3 = Task(
        title="Play Time",
        duration=20,
        priority="medium",
        frequency="daily",
        scheduled_time="14:00",
        notes="Interactive fetch"
    )
    
    dog.add_task(task1)
    dog.add_task(task2)
    dog.add_task(task3)

    # Add Tasks to Cat (Whiskers) - also out of order
    task4 = Task(
        title="Litter Box",
        duration=5,
        priority="high",
        frequency="daily",
        scheduled_time="18:00",
        notes="Clean litter box"
    )
    task5 = Task(
        title="Petting",
        duration=15,
        priority="medium",
        frequency="daily",
        scheduled_time="19:30",
        notes="Affection time"
    )
    
    cat.add_task(task4)
    cat.add_task(task5)

    print("Tasks Added:")
    print(f"  {dog.name}'s tasks ({len(dog.tasks)}):")
    for task in dog.tasks:
        print(f"    - {task}")
    print(f"  {cat.name}'s tasks ({len(cat.tasks)}):")
    for task in cat.tasks:
        print(f"    - {task}")
    print()

    # Show all tasks from Owner's perspective
    all_tasks = owner.get_all_tasks()
    print(f"Total tasks across all pets: {len(all_tasks)}")
    print()

    # Generate and display the daily plan
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("=" * 60)
    print(plan.display())
    print()

    print("=" * 60)
    print("📋 Plan Explanation:")
    print("=" * 60)
    print(scheduler.explain_plan(plan))
    print()

    # Show plan as dictionary (useful for Streamlit)
    print("=" * 60)
    print("Plan Data (as dictionary):")
    print("=" * 60)
    import json
    print(json.dumps(plan.to_dict(), indent=2))
    print()

    # --- TEST: SORTING BY TIME ---
    print("=" * 60)
    print("🕐 TESTING: sort_by_time()")
    print("=" * 60)
    print("Tasks BEFORE sorting by time (out of order):")
    all_tasks = owner.get_all_tasks()
    for i, task in enumerate(all_tasks, 1):
        time_str = task.scheduled_time if task.scheduled_time else "NOT SCHEDULED"
        print(f"  {i}. {task.title:20} | {time_str} | {task.priority}")
    print()
    
    print("Tasks AFTER sorting by time (chronological):")
    sorted_by_time = scheduler.sort_by_time(all_tasks)
    for i, task in enumerate(sorted_by_time, 1):
        time_str = task.scheduled_time if task.scheduled_time else "NOT SCHEDULED"
        print(f"  {i}. {task.title:20} | {time_str} | {task.priority}")
    print()

    # --- TEST: FILTERING BY PRIORITY ---
    print("=" * 60)
    print("🎯 TESTING: filter_by_priority()")
    print("=" * 60)
    
    high_priority = scheduler.filter_by_priority("high")
    print(f"HIGH priority tasks: ({len(high_priority)})")
    for task in high_priority:
        print(f"  ✓ {task.title:20} | {task.priority:6} | {task.duration}min")
    print()
    
    medium_priority = scheduler.filter_by_priority("medium")
    print(f"MEDIUM priority tasks: ({len(medium_priority)})")
    for task in medium_priority:
        print(f"  ✓ {task.title:20} | {task.priority:6} | {task.duration}min")
    print()
    
    low_priority = scheduler.filter_by_priority("low")
    print(f"LOW priority tasks: ({len(low_priority)})")
    if low_priority:
        for task in low_priority:
            print(f"  ✓ {task.title:20} | {task.priority:6} | {task.duration}min")
    else:
        print("  (none)")
    print()

    # --- TEST: GET DUE TASKS ---
    print("=" * 60)
    print("📋 TESTING: get_due_tasks()")
    print("=" * 60)
    due_tasks = scheduler.get_due_tasks()
    print(f"Tasks due today: ({len(due_tasks)})")
    for task in due_tasks:
        print(f"  • {task.title:20} | Freq: {task.frequency:10} | Priority: {task.priority}")
    print()

    # --- TEST: CONFLICT DETECTION ---
    print("=" * 60)
    print("⚠️  TESTING: detect_conflicts()")
    print("=" * 60)
    conflicts = scheduler.detect_conflicts(plan)
    print(f"Conflicts detected: {len(conflicts)}")
    if conflicts:
        for conflict in conflicts:
            print(f"  ⚠️  {conflict}")
    else:
        print("  ✓ No conflicts! All tasks fit within available time.")
    print()

    # --- TEST: TASK COMPLETION & NEXT DUE DATE ---
    print("=" * 60)
    print("✓ TESTING: mark_complete() & next_due_date")
    print("=" * 60)
    print("Before marking complete:")
    print(f"  • {task1.title}")
    print(f"    └─ last_completed: {task1.last_completed}")
    print(f"    └─ next_due_date: {task1.next_due_date}")
    print(f"  • {task3.title}")
    print(f"    └─ last_completed: {task3.last_completed}")
    print(f"    └─ next_due_date: {task3.next_due_date}")
    print()
    
    # Mark tasks complete - this triggers next_due_date calculation
    print("Marking tasks complete...")
    task1.mark_complete()  # Daily task
    task3.mark_complete()  # Daily task
    print()
    
    print("After marking complete (using timedelta):")
    print(f"  • {task1.title} (DAILY)")
    print(f"    └─ last_completed: {task1.last_completed}")
    print(f"    └─ next_due_date: {task1.next_due_date} (today + 1 day)")
    print(f"  • {task3.title} (DAILY)")
    print(f"    └─ last_completed: {task3.last_completed}")
    print(f"    └─ next_due_date: {task3.next_due_date} (today + 1 day)")
    print()
    
    # Test with weekly task
    task5.frequency = "weekly"
    print(f"Testing with WEEKLY task: {task5.title}")
    print(f"  Before: next_due_date = {task5.next_due_date}")
    task5.mark_complete()
    print(f"  After:  next_due_date = {task5.next_due_date} (today + 7 days)")
    print()

    # --- TEST: TIME CONFLICT DETECTION ---
    print("=" * 60)
    print("⏰ TESTING: detect_time_conflicts()")
    print("=" * 60)
    print("Creating two tasks scheduled at the SAME time (11:30)...")
    
    # Create two tasks with the same scheduled_time to test conflict detection
    conflict_task1 = Task(
        title="Grooming",
        duration=25,
        priority="medium",
        frequency="daily",
        scheduled_time="11:30",
        notes="Dog grooming session"
    )
    conflict_task2 = Task(
        title="Vet Check-up",
        duration=30,
        priority="high",
        frequency="as_needed",
        scheduled_time="11:30",
        notes="Regular vet visit"
    )
    
    # Add to pets
    dog.add_task(conflict_task1)
    cat.add_task(conflict_task2)
    
    print(f"  • {conflict_task1.title} scheduled at {conflict_task1.scheduled_time}")
    print(f"  • {conflict_task2.title} scheduled at {conflict_task2.scheduled_time}")
    print()
    
    # Detect time conflicts
    time_conflicts = scheduler.detect_time_conflicts()
    
    print(f"Time conflicts detected: {len(time_conflicts)}")
    if time_conflicts:
        for conflict in time_conflicts:
            print(f"  {conflict}")
    else:
        print("  ✓ No time conflicts!")
    print()

    # --- TEST: NO TIME CONFLICTS (different times) ---
    print("=" * 60)
    print("✓ TESTING: detect_time_conflicts() with different times")
    print("=" * 60)
    
    # Create tasks with DIFFERENT times
    no_conflict_task1 = Task(
        title="Evening Walk",
        duration=20,
        priority="high",
        frequency="daily",
        scheduled_time="18:00",
        notes="Evening dog walk"
    )
    no_conflict_task2 = Task(
        title="Night Feeding",
        duration=10,
        priority="high",
        frequency="daily",
        scheduled_time="20:00",
        notes="Night feeding for both pets"
    )
    
    dog.add_task(no_conflict_task1)
    cat.add_task(no_conflict_task2)
    
    print(f"  • {no_conflict_task1.title} scheduled at {no_conflict_task1.scheduled_time}")
    print(f"  • {no_conflict_task2.title} scheduled at {no_conflict_task2.scheduled_time}")
    print()
    
    # Detect time conflicts (should be none for these new tasks)
    no_conflicts = scheduler.detect_time_conflicts([no_conflict_task1, no_conflict_task2])
    
    print(f"Time conflicts detected: {len(no_conflicts)}")
    if no_conflicts:
        for conflict in no_conflicts:
            print(f"  {conflict}")
    else:
        print("  ✓ No time conflicts! Tasks are at different times.")
    print()


if __name__ == "__main__":
    main()
