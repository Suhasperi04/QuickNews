from instagrapi import Client
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

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
        
        # Add story number and description
        caption += f"📌 Story {i}: {desc}\n\n"
    
    # Add hashtags
    caption += "#todaysnews #headlines #trending #breakingnews"
    
    # Verify final length
    if len(caption) > 2200:
        caption = caption[:2197] + "..."
    
    return caption

def post_carousel(slides, news_items):
    """Post a carousel of slides to Instagram"""
    try:
        # Login to Instagram
        cl = Client()
        cl.login(USERNAME, PASSWORD)
        
        # Create caption
        caption = create_caption(news_items)
        
        # Post carousel
        media = cl.album_upload(
            slides,
            caption=caption
        )
        
        print(f"✅ Posted carousel successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error posting to Instagram: {e}")
        return False
