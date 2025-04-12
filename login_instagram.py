# login_instagram.py
from instagrapi import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = "creds/session.json"

cl = Client()

try:
    cl.login(USERNAME, PASSWORD)
    print("✅ Logged in successfully!")

    # Save session to file
    session = cl.get_settings()
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)
    print("💾 Session saved to", SESSION_FILE)

except Exception as e:
    print("❌ Login failed:", e)
