from instagrapi import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = "creds/session.json"

def get_client():
    cl = Client()

    if os.path.exists(SESSION_FILE):
        try:
            print("🔐 Loading saved session...")
            with open(SESSION_FILE, "r") as f:
                session = json.load(f)
            cl.set_settings(session)
            cl.get_timeline_feed()  # checks if session is still valid
            print("✅ Session is valid.")
            return cl
        except Exception as e:
            print("⚠️ Session invalid, re-login required:", e)

    try:
        cl.login(USERNAME, PASSWORD)
        print("🔓 Logged in successfully.")
        session = cl.get_settings()
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        with open(SESSION_FILE, "w") as f:
            json.dump(session, f)
        print("💾 New session saved.")
    except Exception as e:
        print("❌ Login failed:", e)
        raise

    return cl

def delete_all_except_first():
    cl = get_client()
    user_id = cl.user_id_from_username(USERNAME)
    medias = cl.user_medias(user_id, amount=50)

    print(f"📸 Total posts found: {len(medias)}")

    for i, media in enumerate(medias):
        if i == 0:
            print(f"✅ Keeping first post: {media.pk}")
            continue
        try:
            cl.media_delete(media.pk)
            print(f"🗑️ Deleted post {i+1}: {media.pk}")
        except Exception as e:
            print(f"❌ Error deleting post {i+1}: {e}")

if __name__ == "__main__":
    delete_all_except_first()
