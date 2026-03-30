import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan, Priority, Frequency
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")

# --- Session State Init ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "plan" not in st.session_state:
    st.session_state.plan = None

# --- Owner + Pet Setup ---
st.subheader("Owner & Pet Info")

col1, col2, col3, col4 = st.columns(4)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    time_available = st.number_input("Time available (min)", min_value=10, max_value=480, value=60)
with col3:
    pet_name = st.text_input("Pet name", value="Mochi")
with col4:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save Owner & Pet"):
    pet = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name, time_available=int(time_available))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.plan = None  # reset plan on owner change
    st.success(f"Saved! {owner_name} with pet {pet_name} ({species})")

if st.session_state.owner:
    st.caption(f"Current owner: {st.session_state.owner}")

st.divider()

# --- Add Tasks ---
st.subheader("Tasks")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly", "as_needed"], index=0)

if st.button("Add task"):
    if st.session_state.owner is None:
        st.warning("Save an owner and pet first.")
    else:
        task = Task(
            title=task_title,
            duration=int(duration),
            priority=priority,
            frequency=frequency
        )
        st.session_state.owner.add_task(st.session_state.pet, task)
        st.success(f"Added: {task_title} ({frequency})")

if st.session_state.pet and st.session_state.pet.tasks:
    st.write("### View & Manage Tasks")
    
    # Filtering and Sorting Options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.radio("Status", ["All", "Incomplete", "Completed"], horizontal=True)
    with col2:
        sort_by = st.radio("Sort by", ["Priority", "Duration", "Added"], horizontal=True)
    with col3:
        priority_filter = st.multiselect("Priority", ["low", "medium", "high"], default=["low", "medium", "high"])
    
    # Filter tasks by status
    filtered_tasks = st.session_state.pet.tasks
    if status_filter == "Incomplete":
        filtered_tasks = st.session_state.pet.get_incomplete_tasks()
    elif status_filter == "Completed":
        filtered_tasks = [t for t in filtered_tasks if t.completion_status]
    
    # Filter by priority
    filtered_tasks = [t for t in filtered_tasks if t.priority in priority_filter]
    
    # Sort tasks
    if sort_by == "Duration":
        filtered_tasks = sorted(filtered_tasks, key=lambda t: t.duration, reverse=True)
    elif sort_by == "Priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered_tasks = sorted(filtered_tasks, key=lambda t: priority_order.get(t.priority, 3))
    
    # Display tasks with toggle for completion
    if filtered_tasks:
        for idx, task in enumerate(filtered_tasks):
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            
            with col1:
                # Mark complete/incomplete
                new_status = st.checkbox(
                    "Done",
                    value=task.completion_status,
                    key=f"task_status_{id(task)}"
                )
                if new_status != task.completion_status:
                    if new_status:
                        task.mark_complete()
                        st.session_state.plan = None  # reset plan when task status changes
                    else:
                        task.mark_incomplete()
                        st.session_state.plan = None
            
            with col2:
                st.write(f"**{task.title}**")
            with col3:
                st.write(f"⏱️ {task.duration}min")
            with col4:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                st.write(f"{priority_emoji.get(task.priority, '⚪')} {task.priority}")
            with col5:
                st.write(f"📅 {task.frequency}")
            with col6:
                if task.last_completed:
                    st.caption(f"Last: {task.last_completed}")
                else:
                    st.caption("Never completed")
            with col7:
                if task.next_due_date:
                    st.caption(f"Next due: {task.next_due_date}")
                else:
                    st.caption("No due date")
    else:
        st.info("No tasks match the current filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Generate schedule"):
        if st.session_state.owner is None:
            st.warning("Save an owner and pet first.")
        elif not st.session_state.pet.tasks:
            st.warning("Add at least one task before generating a schedule.")
        else:
            scheduler = Scheduler(owner=st.session_state.owner)
            st.session_state.plan = scheduler.generate_plan()

with col2:
    show_due_only = st.checkbox("Show only due tasks", value=False)

with col3:
    priority_focus = st.selectbox("Focus on priority", ["All", "High", "Medium", "Low"])

if st.session_state.plan:
    scheduler = Scheduler(owner=st.session_state.owner)
    
    # Detect conflicts
    conflicts = scheduler.detect_conflicts(st.session_state.plan)
    
    # Display conflicts as warnings
    if conflicts:
        st.warning("⚠️ **Time Conflicts Detected:**")
        for conflict in conflicts:
            st.write(f"  • {conflict}")
    else:
        st.success("✓ All tasks fit within available time!")
    
    st.divider()
    
    # Display Plan
    st.text(st.session_state.plan.display())
    
    st.divider()
    
    # Explanation
    st.markdown("#### 📋 Scheduling Reasoning")
    st.text(scheduler.explain_plan(st.session_state.plan))
    
    st.divider()
    
    # Task Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tasks Scheduled", len(st.session_state.plan.scheduled_tasks))
    with col2:
        st.metric("Total Time", f"{st.session_state.plan.total_time} min")
    with col3:
        remaining = st.session_state.owner.time_available - st.session_state.plan.total_time
        st.metric("Time Remaining", f"{remaining} min")
    with col4:
        due_tasks = scheduler.get_due_tasks()
        st.metric("Due Tasks", len(due_tasks))
