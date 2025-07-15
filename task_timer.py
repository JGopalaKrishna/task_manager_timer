import streamlit as st
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import uuid
from streamlit_autorefresh import st_autorefresh

# ========== Firebase Setup ==========
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # 👈 Place your key here 
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://taskmanager-fb5cb-default-rtdb.firebaseio.com/'  # 👈 Replace with your actual DB URL
    })

ref = db.reference("tasks")

# ========== Functions ==========
def save_task_to_firebase(task):
    task_id = str(uuid.uuid4())
    ref.child(task_id).set({
        "id": task_id,
        "name": task["name"],
        "due": task["due"].strftime("%Y-%m-%d %H:%M:%S")
    })

def load_tasks_from_firebase():
    data = ref.get()
    tasks = []
    if data:
        for task_id, task in data.items():
            tasks.append({
                "id": task["id"],
                "name": task["name"],
                "due": datetime.strptime(task["due"], "%Y-%m-%d %H:%M:%S")
            })
    return tasks

def delete_task_from_firebase(task_id):
    ref.child(task_id).delete()

def time_left(due):
    now = datetime.now()
    remaining = due - now
    return remaining if remaining.total_seconds() > 0 else timedelta(seconds=0)

# ========== Streamlit UI ==========
st.title("📝 Firebase Task Manager with Countdown ⏳")

task_name = st.text_input("Enter Task Name:")
task_date = st.date_input("Enter Date:")
task_time = st.time_input("Enter Time:")
if st.button("Add Task"):
    due_datetime = datetime.combine(task_date, task_time)
    save_task_to_firebase({"name": task_name, "due": due_datetime})
    st.success("✅ Task added!")

st.markdown("---")
st.subheader("📆 Upcoming Tasks")

tasks = load_tasks_from_firebase()
if not tasks:
    st.info("No tasks added yet.")
else:
    for task in tasks:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{task['name']}**")
            st.caption(f"Due: {task['due'].strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            remaining = time_left(task["due"])
            if remaining.total_seconds() == 0:
                st.error("⏰ Time's up!")
            else:
                hrs, rem = divmod(remaining.seconds, 3600)
                mins, secs = divmod(rem, 60)
                st.success(f"{remaining.days}d {hrs:02}h:{mins:02}m:{secs:02}s")
        with col3:
            if st.button("❌", key=task['id']):
                delete_task_from_firebase(task['id'])
                st.experimental_rerun()

st_autorefresh(interval=30000, key="firebase-refresh")
