"""
Tests for PawPal+ system.

Tests core functionality:
- Task completion status
- Task addition to pets
- Owner task retrieval
- Scheduler plan generation
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


@pytest.fixture
def task():
    """Create a sample task for testing."""
    return Task(
        title="Morning Walk",
        duration=30,
        priority="high",
        frequency="daily",
        notes="Test walk"
    )


@pytest.fixture
def pet():
    """Create a sample pet for testing."""
    return Pet(name="Max", species="Golden Retriever")


@pytest.fixture
def owner():
    """Create a sample owner for testing."""
    return Owner(name="Sarah", time_available=120)


class TestTaskCompletion:
    """Test task completion status changes."""

    def test_task_completion_mark_complete(self, task):
        """Verify that calling mark_complete() changes the task's completion status to True."""
        # Arrange: task starts incomplete
        assert task.completion_status == False
        
        # Act: mark the task as complete
        task.mark_complete()
        
        # Assert: task is now marked complete
        assert task.completion_status == True

    def test_task_completion_mark_incomplete(self, task):
        """Verify that calling mark_incomplete() changes the task's completion status to False."""
        # Arrange: task is marked complete first
        task.mark_complete()
        assert task.completion_status == True
        
        # Act: mark the task as incomplete
        task.mark_incomplete()
        
        # Assert: task is now marked incomplete
        assert task.completion_status == False

    def test_task_initial_status_incomplete(self, task):
        """Verify that new tasks are created with incomplete status."""
        assert task.completion_status == False


class TestTaskAddition:
    """Test task addition to pets."""

    def test_add_task_to_pet_increases_count(self, pet, task):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Arrange: pet starts with no tasks
        assert len(pet.tasks) == 0
        
        # Act: add a task to the pet
        pet.add_task(task)
        
        # Assert: pet now has one task
        assert len(pet.tasks) == 1
        assert task in pet.tasks

    def test_add_multiple_tasks_to_pet(self, pet):
        """Verify that multiple tasks can be added to a pet."""
        # Arrange: create multiple tasks
        task1 = Task(title="Walk", duration=30, priority="high")
        task2 = Task(title="Feeding", duration=10, priority="high")
        task3 = Task(title="Playtime", duration=20, priority="medium")
        
        # Act: add all tasks to pet
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        # Assert: pet has all three tasks
        assert len(pet.tasks) == 3
        assert task1 in pet.tasks
        assert task2 in pet.tasks
        assert task3 in pet.tasks

    def test_remove_task_from_pet(self, pet, task):
        """Verify that tasks can be removed from a pet."""
        # Arrange: add a task first
        pet.add_task(task)
        assert len(pet.tasks) == 1
        
        # Act: remove the task
        pet.remove_task(task)
        
        # Assert: pet has no tasks
        assert len(pet.tasks) == 0
        assert task not in pet.tasks


class TestPetIncompleteTasks:
    """Test retrieving incomplete tasks from pets."""

    def test_get_incomplete_tasks_empty_list(self, pet):
        """Verify that a pet with no tasks returns empty incomplete tasks."""
        incomplete = pet.get_incomplete_tasks()
        assert incomplete == []

    def test_get_incomplete_tasks_filters_completed(self, pet):
        """Verify that get_incomplete_tasks() only returns tasks with completion_status = False."""
        # Arrange: add tasks, mark one complete
        task1 = Task(title="Walk", duration=30, priority="high")
        task2 = Task(title="Feeding", duration=10, priority="high")
        
        pet.add_task(task1)
        pet.add_task(task2)
        task1.mark_complete()
        
        # Act: get incomplete tasks
        incomplete = pet.get_incomplete_tasks()
        
        # Assert: only task2 is in incomplete list
        assert len(incomplete) == 1
        assert task2 in incomplete
        assert task1 not in incomplete


class TestOwnerTaskManagement:
    """Test Owner's task management across multiple pets."""

    def test_owner_get_all_tasks(self, owner):
        """Verify that owner.get_all_tasks() retrieves tasks from all pets."""
        # Arrange: create pets with tasks
        dog = Pet(name="Max", species="Dog")
        cat = Pet(name="Whiskers", species="Cat")
        
        dog_walk = Task(title="Walk", duration=30, priority="high")
        dog_feed = Task(title="Feed", duration=10, priority="high")
        cat_litter = Task(title="Litter", duration=5, priority="high")
        
        dog.add_task(dog_walk)
        dog.add_task(dog_feed)
        cat.add_task(cat_litter)
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        # Act: get all tasks
        all_tasks = owner.get_all_tasks()
        
        # Assert: all three tasks are retrieved
        assert len(all_tasks) == 3
        assert dog_walk in all_tasks
        assert dog_feed in all_tasks
        assert cat_litter in all_tasks

    def test_owner_get_incomplete_tasks(self, owner):
        """Verify that owner.get_incomplete_tasks() only returns incomplete tasks."""
        # Arrange: create pets with mixed task completion
        dog = Pet(name="Max", species="Dog")
        walk = Task(title="Walk", duration=30, priority="high")
        feed = Task(title="Feed", duration=10, priority="high")
        
        dog.add_task(walk)
        dog.add_task(feed)
        walk.mark_complete()
        
        owner.add_pet(dog)
        
        # Act: get incomplete tasks
        incomplete = owner.get_incomplete_tasks()
        
        # Assert: only feed task is returned
        assert len(incomplete) == 1
        assert feed in incomplete
        assert walk not in incomplete


class TestSchedulerPlanGeneration:
    """Test Scheduler's plan generation logic."""

    def test_scheduler_generates_plan(self, owner):
        """Verify that scheduler generates a DailyPlan."""
        # Arrange: set up owner with pet and tasks
        pet = Pet(name="Max", species="Dog")
        task = Task(title="Walk", duration=30, priority="high")
        pet.add_task(task)
        owner.add_pet(pet)
        
        # Act: generate plan
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        
        # Assert: plan is created and contains task
        assert plan is not None
        assert len(plan.scheduled_tasks) > 0
        assert task in plan.scheduled_tasks

    def test_scheduler_respects_time_constraint(self, owner):
        """Verify that scheduler doesn't schedule tasks exceeding available time."""
        # Arrange: owner has 30min, but tasks need 60min
        owner.time_available = 30
        pet = Pet(name="Max", species="Dog")
        task1 = Task(title="Walk", duration=25, priority="high")
        task2 = Task(title="Play", duration=20, priority="medium")
        
        pet.add_task(task1)
        pet.add_task(task2)
        owner.add_pet(pet)
        
        # Act: generate plan
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        
        # Assert: plan total time does not exceed available time
        assert plan.total_time <= owner.time_available
        # task1 fits but task2 doesn't
        assert task1 in plan.scheduled_tasks

    def test_scheduler_prioritizes_high_priority_tasks(self, owner):
        """Verify that scheduler prioritizes high-priority tasks."""
        # Arrange: create high and low priority tasks with limited time
        owner.time_available = 30
        pet = Pet(name="Max", species="Dog")
        
        high_priority = Task(title="Walk", duration=20, priority="high")
        low_priority = Task(title="Play", duration=15, priority="low")
        
        pet.add_task(low_priority)
        pet.add_task(high_priority)
        owner.add_pet(pet)
        
        # Act: generate plan
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        
        # Assert: high priority task is scheduled
        assert high_priority in plan.scheduled_tasks
