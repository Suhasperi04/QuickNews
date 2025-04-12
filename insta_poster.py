from instagrapi import Client
import os
import json
import time
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = "creds/session.json"

def ensure_creds_dir():
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)

def verify_image(path):
    """Verify and fix image if needed"""
    try:
        with Image.open(path) as img:
            # Must be RGB for Instagram
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Instagram requires 1:1 ratio for carousel
            if img.size != (1080, 1080):
                img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
            
            # Save with correct format and quality
            img.save(path, format='JPEG', quality=95, optimize=True)
            
            # Verify the saved image
            with Image.open(path) as saved_img:
                if saved_img.mode != 'RGB' or saved_img.size != (1080, 1080):
                    return False
            return True
    except Exception as e:
        print(f"❌ Error processing image {path}: {e}")
        return False

def get_client():
    cl = Client()
    ensure_creds_dir()

    # Load saved session
    if os.path.exists(SESSION_FILE):
        print("🔐 Loading session from file...")
        try:
            with open(SESSION_FILE, "r") as f:
                session = json.load(f)
            cl.set_settings(session)
            cl.get_timeline_feed()
            print("✅ Session valid")
            return cl
        except Exception as e:
            print(f"⚠️ Session invalid: {e}")
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
                print("🗑️ Deleted invalid session")

    # Login with credentials
    if not USERNAME or not PASSWORD:
        raise Exception("❌ Instagram credentials not found in .env")

    print("🔑 Logging in...")
    cl.login(USERNAME, PASSWORD)
    print("✅ Login successful")
    
    # Save session
    with open(SESSION_FILE, "w") as f:
        json.dump(cl.get_settings(), f)
    print("💾 Session saved")
    
    return cl

def shorten_url(url):
    """Shorten URL to fit in caption"""
    if len(url) > 25:  # Make URLs even shorter
        return url[:22] + "..."
    return url

def create_caption(news_items):
    """Create a caption with detailed explanations of each news item"""
    caption = "🌐 Today's Top Stories\n\n"
    
    # Add detailed explanations for each news item
    for i, news in enumerate(news_items, 1):
        # Get or generate detailed description
        desc = news.get('description', '').strip()
        if not desc:
            continue
            
        # Format the description into ~6 sentences
        sentences = desc.split('. ')
        if len(sentences) > 6:
            desc = '. '.join(sentences[:6]) + '.'
        elif len(sentences) < 6 and len(desc) > 100:
            # If description is long but not properly split into sentences
            words = desc.split()
            chunks = []
            chunk = []
            for word in words:
                chunk.append(word)
                if len(' '.join(chunk)) > 40:
                    chunks.append(' '.join(chunk))
                    chunk = []
            if chunk:
                chunks.append(' '.join(chunk))
            desc = '. '.join(chunks[:6])
            if not desc.endswith('.'):
                desc += '.'
        
        # Add story number and description
        caption += f"📌 Story {i}: {desc}\n\n"
    
    # Add hashtags
    caption += "#todaysnews #headlines #trending #breakingnews"
    
    # Verify final length
    if len(caption) > 2200:
        # Emergency truncation if still too long
        caption = caption[:2197] + "..."
    
    return caption

def post_carousel(news_items):
    # Get list of slides
    try:
        slides_path = sorted([
            os.path.join("slides", f)
            for f in os.listdir("slides")
            if f.endswith(".jpg")
        ])
        print(f"📸 Found {len(slides_path)} slides")
    except Exception as e:
        print(f"❌ Error reading slides: {e}")
        return

    if len(slides_path) < 2:
        print("⚠️ Not enough slides (need ≥2)")
        return

    # Verify and fix images
    verified_paths = []
    for path in slides_path:
        print(f"🔍 Verifying {os.path.basename(path)}...")
        if verify_image(path):
            verified_paths.append(path)
            print(f"✅ Verified {os.path.basename(path)}")
        else:
            print(f"❌ Invalid image: {os.path.basename(path)}")

    if len(verified_paths) < 2:
        print("❌ Not enough valid images")
        return

    # Create caption within Instagram's limits
    caption = create_caption(news_items)
    print(f"\n📝 Caption length: {len(caption)} chars")

    # Post to Instagram
    try:
        cl = get_client()
        result = cl.album_upload(
            verified_paths,
            caption=caption,
            extra_data={
                "custom_accessibility_caption": "News Headlines Carousel"
            }
        )
        print("✅ Posted successfully!")
        print(f"🔗 Post URL: {result.dict()['code']}")
    except Exception as e:
        print(f"❌ Post failed: {str(e)}")
        if "login_required" in str(e).lower():
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
                print("🗑️ Deleted invalid session")
