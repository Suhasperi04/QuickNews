"""Instagram carousel posting module"""
from utils.instagram_auth import get_client
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Constants
MAX_CAPTION_LENGTH = 2200
HASHTAGS = "#todaysnews #headlines #trending #breakingnews"

def create_caption(news_items):
    """Create a caption with detailed explanations of each news item"""
    caption = "🌐 Today's Top Stories\n\n"
    
    # Calculate max length for news content to leave room for hashtags
    max_content_length = MAX_CAPTION_LENGTH - len(HASHTAGS) - 20  # Extra buffer
    
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
        story_text = f"📌 Story {i}: {desc}\n\n"
        
        # Check if adding this story would exceed limit
        if len(caption) + len(story_text) > max_content_length:
            break
            
        caption += story_text
    
    # Add hashtags
    caption += HASHTAGS
    
    return caption

def post_carousel(slides, news_items, max_retries=3, retry_delay=5):
    """Post a carousel of slides to Instagram
    
    Args:
        slides (list): List of paths to image files
        news_items (list): List of news items
        max_retries (int): Maximum number of retries for failed operations
        retry_delay (int): Delay in seconds between retries
    """
    retries = 0
    while retries < max_retries:
        try:
            # Get authenticated client
            cl = get_client()
            
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
            retries += 1
            if retries == max_retries:
                print(f"❌ Failed to post carousel after {max_retries} attempts: {e}")
            else:
                print(f"⚠️ Error posting carousel (attempt {retries}/{max_retries}): {e}")
                time.sleep(retry_delay)
    
    return False
