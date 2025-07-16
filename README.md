# Firebase Task Manager with Countdown (IST)

## Setup Instructions

1. In your Streamlit Cloud dashboard, go to "Advanced Settings" > "Edit Secrets"
2. Paste the following secrets format (replace with your real Firebase info):

[firebase]
database_url = "https://your-project-id.firebaseio.com"
key = """<paste the entire firebase_key.json content here, escape newlines as \n>"""

## Run Locally:

pip install -r requirements.txt
streamlit run task_timer.py
