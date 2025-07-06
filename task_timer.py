import streamlit as st
from datetime import datetime, timedelta
import time
import json
import os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Task Timer ⏳", layout="centered")

# File to save tasks
TASK_FILE = "tasks.json"

# Load tasks from JSON file
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            raw = json.load(f)
            return [
                {"name": task["name"], "due": datetime.strptime(task["due"], "%Y-%m-%d %H:%M:%S")}
                for task in raw
            ]
    return []

# Save tasks to JSON file
def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(
            [{"name": task["name"], "due": task["due"].strftime("%Y-%m-%d %H:%M:%S")} for task in tasks],
            f, indent=2
        )

# Initialize tasks in session_state
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# Title
st.title("📝 Task Manager with Countdown Timer ⏳")

# Task Input
with st.form("task_form"):
    task_name = st.text_input("Enter Task Name:")
    task_date = st.date_input("Enter Date:")
    task_time = st.time_input("Enter Time:")
    submitted = st.form_submit_button("Add Task")

    if submitted:
        due_datetime = datetime.combine(task_date, task_time)
        new_task = {"name": task_name, "due": due_datetime}
        st.session_state.tasks.append(new_task)
        save_tasks(st.session_state.tasks)
        st.success(f"✅ Task '{task_name}' added!")

st.markdown("---")

# Function to calculate time left
def time_left(due):
    now = datetime.now()
    remaining = due - now
    return remaining if remaining.total_seconds() > 0 else timedelta(seconds=0)

# Display tasks
st.subheader("🕒 Upcoming Tasks")

if not st.session_state.tasks:
    st.info("No tasks yet. Add one above!")
else:
    for i, task in enumerate(st.session_state.tasks):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{task['name']}**")
            st.text(f"Due: {task['due'].strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            remaining = time_left(task["due"])
            if remaining.total_seconds() == 0:
                st.error("⏰ Time's up!")
            else:
                hrs, rem = divmod(remaining.seconds, 3600)
                mins, secs = divmod(rem, 60)
                # st.success(f"{remaining.days}d {hrs:02}h:{mins:02}m:{secs:02}s")
                st.success(f"{remaining.days} Days 🔸 {hrs:02} Hr 🔹 {mins:02} Min")
        with col3:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.tasks.pop(i)
                save_tasks(st.session_state.tasks)
                st.rerun()

# Auto-refresh every 1 second
# time.sleep(10)
# print("hi")
# st.rerun()
# Auto-refresh every 10 second
st_autorefresh(interval=60000, key="refresh")
