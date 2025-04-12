"""Instagram authentication utilities"""
from instagrapi import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = os.path.join("creds", "session.json")

def validate_credentials():
    """Validate that credentials are present"""
    if not USERNAME or not PASSWORD:
        raise ValueError("Instagram credentials (IG_USERNAME, IG_PASSWORD) are not set in environment variables")

def get_client(force_login=False):
    """Get an authenticated Instagram client
    
    Args:
        force_login (bool): If True, forces a new login even if a session exists
    
    Returns:
        Client: Authenticated Instagram client
    """
    validate_credentials()
    cl = Client()

    if not force_login and os.path.exists(SESSION_FILE):
        try:
            print("🔐 Loading saved session...")
            with open(SESSION_FILE, "r") as f:
                session = json.load(f)
            cl.set_settings(session)
            cl.get_timeline_feed()  # verify session is valid
            print("✅ Session is valid")
            return cl
        except Exception as e:
            print(f"⚠️ Session invalid, re-login required: {e}")

    # Login and save new session
    try:
        cl.login(USERNAME, PASSWORD)
        print("🔓 Logged in successfully")
        
        # Save session
        session = cl.get_settings()
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        with open(SESSION_FILE, "w") as f:
            json.dump(session, f)
        print("💾 Session saved to", SESSION_FILE)
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        raise

    return cl
