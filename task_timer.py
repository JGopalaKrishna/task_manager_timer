import streamlit as st
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import uuid
import pytz
from streamlit_autorefresh import st_autorefresh
import json

# ========== Timezone ==========
IST = pytz.timezone("Asia/Kolkata")

# ========== Firebase Setup ==========
if not firebase_admin._apps:
    firebase_key_dict = json.loads(st.secrets["firebase"]["firebase_key"])
    db_url = st.secrets["firebase"]["database_url"]
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': db_url
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
            due_utc = datetime.strptime(task["due"], "%Y-%m-%d %H:%M:%S")
            due_ist = pytz.utc.localize(due_utc).astimezone(IST)
            tasks.append({
                "id": task["id"],
                "name": task["name"],
                "due": due_ist
            })
    return tasks

def delete_task_from_firebase(task_id):
    ref.child(task_id).delete()

def time_left(due):
    now = datetime.now(IST)
    remaining = due - now
    return remaining if remaining.total_seconds() > 0 else timedelta(seconds=0)

# ========== Streamlit UI ==========
st.title("📝 Firebase Task Manager with Countdown (IST) ⏳")

task_name = st.text_input("Enter Task Name:")
task_date = st.date_input("Enter Date:")
task_time = st.time_input("Enter Time:")
if st.button("Add Task"):
    due_datetime = datetime.combine(task_date, task_time)
    due_datetime = IST.localize(due_datetime)
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
            st.caption(f"Due: {task['due'].strftime('%Y-%m-%d %I:%M %p')} IST")
        with col2:
            remaining = time_left(task["due"])
            if remaining.total_seconds() == 0:
                st.error("⏰ Time's up!")
            else:
                hrs, rem = divmod(remaining.seconds, 3600)
                mins, secs = divmod(rem, 60)
                st.success(f"{remaining.days}days 🔸 {hrs:02}hrs 🔹 {mins:02}mins 🔻")
        with col3:
            if st.button("❌", key=task['id']):
                delete_task_from_firebase(task['id'])
                st.rerun()

st_autorefresh(interval=60000, key="firebase-refresh")
