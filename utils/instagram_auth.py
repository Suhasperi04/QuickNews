"""Instagram authentication utilities"""
from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
import os
import json
from dotenv import load_dotenv
import time
import random

load_dotenv()

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = os.path.join("creds", "session.json")

# Global client instance
_client = None

def get_random_user_agent():
    """Get a random user agent to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]
    return random.choice(user_agents)

def validate_credentials():
    """Validate that credentials are present"""
    if not USERNAME or not PASSWORD:
        raise ValueError("Instagram credentials (IG_USERNAME, IG_PASSWORD) are not set in environment variables")

def handle_challenge(client):
    """Handle Instagram verification challenge"""
    try:
        print("📱 Challenge required. Sending verification code...")
        challenge_type = client.last_json.get("step_name", "")
        
        if challenge_type == "verify_email":
            client.challenge_send_code(ChallengeChoice.EMAIL)
            print("✉️ Verification code sent to your email.")
        else:
            client.challenge_send_code(ChallengeChoice.SMS)
            print("📱 Verification code sent to your phone.")
            
        code = input("Enter the verification code: ")
        client.challenge_code(code)
        print("✅ Challenge completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Challenge failed: {e}")
        return False

def configure_client(cl):
    """Configure client with optimal settings"""
    # Set custom user agent
    cl.set_user_agent(get_random_user_agent())
    
    # Set request timeout
    cl.request_timeout = 30
    
    # Set custom connection settings
    cl.set_settings({
        "connection_timeout": 30,
        "max_connection_attempts": 3,
        "connection_attempts_delay": 5,
    })
    
    # Set device settings
    cl.set_device({
        "app_version": "269.0.0.18.75",
        "android_version": 26,
        "android_release": "8.0.0",
        "dpi": "480dpi",
        "resolution": "1080x1920",
        "manufacturer": "OnePlus",
        "device": "OnePlus5",
        "model": "ONEPLUS A5000",
        "cpu": "qcom"
    })
    
    return cl

def get_client(force_login=False):
    """Get an authenticated Instagram client
    
    Args:
        force_login (bool): If True, forces a new login even if a session exists
    
    Returns:
        Client: Authenticated Instagram client
    """
    global _client
    
    # Return existing client if available and not forcing login
    if not force_login and _client is not None:
        try:
            _client.get_timeline_feed()  # verify session is valid
            return _client
        except Exception:
            _client = None  # Reset if invalid
    
    validate_credentials()
    cl = Client()
    cl = configure_client(cl)
    
    # Try loading existing session
    if not force_login and os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session = json.load(f)
            cl.set_settings(session)
            cl.get_timeline_feed()  # verify session
            _client = cl
            return cl
        except Exception as e:
            print(f"⚠️ Session invalid: {e}")
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)  # Remove invalid session file
    
    # Login with exponential backoff
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            time.sleep(attempt * 2)  # Exponential backoff
            cl.login(USERNAME, PASSWORD)
            
            # Save session
            session = cl.get_settings()
            os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
            with open(SESSION_FILE, 'w') as f:
                json.dump(session, f)
                
            _client = cl
            return cl
            
        except Exception as e:
            print(f"❌ Login attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise
    
    raise Exception("Failed to login after multiple attempts")

def logout():
    """Logout and clear session"""
    global _client
    try:
        if _client:
            _client.logout()
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception:
        pass
    finally:
        _client = None
