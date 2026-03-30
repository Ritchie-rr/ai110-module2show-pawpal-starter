import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan, Priority, Frequency
from datetime import date
import pandas as pd

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
        sort_by = st.radio("Sort by", ["Priority", "Duration", "Time Scheduled"], horizontal=True)
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
    
    # Sort tasks using scheduler methods where applicable
    if sort_by == "Duration":
        filtered_tasks = sorted(filtered_tasks, key=lambda t: t.duration, reverse=True)
    elif sort_by == "Priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered_tasks = sorted(filtered_tasks, key=lambda t: priority_order.get(t.priority, 3))
    elif sort_by == "Time Scheduled":
        scheduler = Scheduler(owner=st.session_state.owner)
        filtered_tasks = scheduler.sort_by_time(filtered_tasks)
    
    # Display tasks with toggle for completion
    if filtered_tasks:
        st.success(f"✓ Found {len(filtered_tasks)} task(s)")
        
        # Create professional dataframe display
        task_data = []
        for task in filtered_tasks:
            priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            status_badge = "✅" if task.completion_status else "⭕"
            last_completed = str(task.last_completed) if task.last_completed else "Never"
            next_due = str(task.next_due_date) if task.next_due_date else "No due date"
            
            task_data.append({
                "Status": status_badge,
                "Task": task.title,
                "Duration (min)": task.duration,
                "Priority": f"{priority_badge} {task.priority.upper()}",
                "Frequency": task.frequency.upper(),
                "Last Completed": last_completed,
                "Next Due": next_due
            })
        
        df = pd.DataFrame(task_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Completion toggle section (collapsible for cleaner UI)
        with st.expander("🔄 Update Task Status"):
            st.caption("Toggle completion status for any task:")
            for task in filtered_tasks:
                col1, col2 = st.columns([1, 4])
                with col1:
                    new_status = st.checkbox(
                        "Done",
                        value=task.completion_status,
                        key=f"task_status_{id(task)}"
                    )
                    if new_status != task.completion_status:
                        if new_status:
                            task.mark_complete()
                            st.session_state.plan = None
                        else:
                            task.mark_incomplete()
                            st.session_state.plan = None
                with col2:
                    st.write(f"**{task.title}** ({task.duration}min)")
    else:
        st.info("No tasks match the current filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("🔧 Build Schedule")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.button("▶️ Generate Daily Schedule", use_container_width=True):
        if st.session_state.owner is None:
            st.warning("Save an owner and pet first.")
        elif not st.session_state.pet.tasks:
            st.warning("Add at least one task before generating a schedule.")
        else:
            scheduler = Scheduler(owner=st.session_state.owner)
            st.session_state.plan = scheduler.generate_plan()
            st.success("✅ Schedule generated successfully!")

with col2:
    if st.session_state.owner:
        scheduler = Scheduler(owner=st.session_state.owner)
        due_tasks = scheduler.get_due_tasks()
        st.metric("Tasks Due", len(due_tasks))
    else:
        st.write("*Set owner*")

with col3:
    if st.session_state.owner:
        time_remaining = st.session_state.owner.time_available
        if st.session_state.plan:
            time_remaining -= st.session_state.plan.total_time
        color = "normal" if time_remaining >= 0 else "off"
        st.metric("Available", f"{time_remaining}m", delta_color=color)
    else:
        st.write("*Set owner*")

if st.session_state.plan:
    scheduler = Scheduler(owner=st.session_state.owner)
    
    # Detect time conflicts in the plan
    conflicts = scheduler.detect_conflicts(st.session_state.plan)
    time_conflicts = scheduler.detect_time_conflicts(st.session_state.plan.scheduled_tasks)
    
    # Professional conflict display with detailed information
    if conflicts or time_conflicts:
        st.warning("⚠️ **Scheduling Issues Detected**", icon="⚠️")
        
        # Create conflict summary
        issue_data = []
        if time_conflicts:
            for conflict in time_conflicts:
                issue_data.append({"Severity": "High - Time Overlap", "Issue": conflict})
        if conflicts:
            for conflict in conflicts:
                issue_data.append({"Severity": "Medium - Time Exceeded", "Issue": conflict})
        
        conflict_df = pd.DataFrame(issue_data)
        st.dataframe(conflict_df, use_container_width=True, hide_index=True)
        
        # Helpful suggestions
        with st.expander("💡 How to resolve these issues"):
            if conflicts:
                st.write("**Time Capacity Exceeded:**")
                st.write(f"- Your owner has {st.session_state.owner.time_available} min available")
                st.write(f"- Current plan requires {st.session_state.plan.total_time} min")
                st.write(f"- **Action:** Remove or defer lower-priority tasks")
            
            if time_conflicts:
                st.write("**Tasks Scheduled at Same Time:**")
                st.write("- Multiple tasks are assigned to the same time slot")
                st.write("- **Action:** Reschedule tasks to different time slots")
    else:
        st.success("✅ All tasks fit within available time!", icon="✅")
    
    st.divider()
    
    # Display Plan as Professional Table
    st.subheader("📅 Your Daily Pet Care Plan")
    if st.session_state.plan.scheduled_tasks:
        plan_data = []
        cumulative_time = 0
        for idx, task in enumerate(st.session_state.plan.scheduled_tasks, 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            cumulative_time += task.duration
            plan_data.append({
                "#": idx,
                "Task": task.title,
                "Duration (min)": task.duration,
                "Priority": f"{priority_icon} {task.priority.upper()}",
                "Frequency": task.frequency.upper(),
                "Cumulative Time": cumulative_time
            })
        
        plan_df = pd.DataFrame(plan_data)
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
    else:
        st.info("No tasks scheduled for today.")
    
    st.divider()
    
    # Explanation with visual formatting
    st.markdown("### 📋 Scheduling Reasoning")
    explanation = scheduler.explain_plan(st.session_state.plan)
    st.info(explanation)
    
    st.divider()
    
    # Task Statistics using Scheduler methods with enhanced display
    st.subheader("📊 Schedule Summary")
    scheduler = Scheduler(owner=st.session_state.owner)
    due_tasks = scheduler.get_due_tasks()
    high_priority = scheduler.filter_by_priority("high")
    remaining_time = st.session_state.owner.time_available - st.session_state.plan.total_time
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Tasks Scheduled",
            len(st.session_state.plan.scheduled_tasks),
            delta=f"of {len(st.session_state.pet.tasks)} total"
        )
    
    with col2:
        st.metric(
            "⏱️ Total Time",
            f"{st.session_state.plan.total_time} min",
            delta=f"of {st.session_state.owner.time_available} available"
        )
    
    with col3:
        status_color = "normal" if remaining_time >= 0 else "off"
        delta_text = f"{remaining_time} min" if remaining_time >= 0 else f"⚠️ Over by {abs(remaining_time)} min"
        st.metric(
            "⏳ Time Remaining",
            f"{remaining_time} min",
            delta=delta_text,
            delta_color=status_color
        )
    
    with col4:
        st.metric(
            "🔴 High Priority Due",
            len(high_priority),
            delta="tasks to prioritize" if high_priority else "no urgent tasks"
        )
    
    # Quick action summary
    st.divider()
    st.caption("💡 **Quick Summary:**")
    summary_metrics = []
    summary_metrics.append(f"✓ {len(st.session_state.plan.scheduled_tasks)} tasks scheduled")
    summary_metrics.append(f"📅 {len(due_tasks)} tasks due today total")
    summary_metrics.append(f"🔴 {len(high_priority)} high-priority tasks")
    
    col_summary = st.columns(len(summary_metrics))
    for col, metric in zip(col_summary, summary_metrics):
        col.write(metric)
