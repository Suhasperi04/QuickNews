import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime, timedelta

load_dotenv()

def clean_title(title):
    """Clean and format news headline"""
    if not title:
        return ""
        
    # Remove source attribution at the end
    if " - " in title:
        title = title.split(" - ")[0]
        
    # Remove unwanted phrases
    unwanted = [
        "LIVE Updates", "Live Updates", "Latest News",
        "Latest Updates", "In Pics", "Watch Video",
        "See Pics", "Full Story"
    ]
    for phrase in unwanted:
        if phrase in title:
            title = title.replace(phrase, "").strip()
            
    # Fix common abbreviations
    abbr = {
        "PM ": "Prime Minister ",
        "FM ": "Finance Minister ",
        "CM ": "Chief Minister ",
        "GDP ": "Gross Domestic Product ",
        "CEO ": "Chief Executive Officer ",
        "AI ": "Artificial Intelligence ",
        "ML ": "Machine Learning ",
        "EV ": "Electric Vehicle ",
        "IPO ": "Initial Public Offering "
    }
    for short, full in abbr.items():
        if short in title:
            title = title.replace(short, full)
            
    # Ensure proper sentence case
    title = title.strip()
    if title and title[0].islower():
        title = title[0].upper() + title[1:]
        
    # Add period if missing
    if title and not title.endswith(('.', '!', '?')):
        title += "."
        
    return title

def is_safe_news(title):
    """Check if news is safe and appropriate"""
    # Skip sensitive topics
    sensitive = [
        "murder", "killed", "death", "dead", "suicide",
        "accident", "crash", "disaster", "tragedy",
        "explicit", "nude", "adult"
    ]
    title_lower = title.lower()
    return not any(word in title_lower for word in sensitive)

def get_category(title):
    """Determine category based on title"""
    categories = {
        "business": ["business", "market", "economy", "stock"],
        "technology": ["tech", "technology", "gadget", "software"],
        "sports": ["sports", "cricket", "football", "tennis"],
        "entertainment": ["entertainment", "movie", "music", "celebrity"]
    }
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in title.lower():
                return category
    return "general"

def get_top_headlines():
    """Fetch top headlines using NewsAPI"""
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        raise ValueError("NEWS_API_KEY environment variable is not set")

    url = 'https://newsapi.org/v2/top-headlines'
    
    params = {
        'country': 'in',
        'apiKey': api_key,
        'pageSize': 10,
        'language': 'en'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        news_data = response.json()
        
        # Load existing history
        history_file = 'news_history.json'
        history = []
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
                if not isinstance(history, list):
                    print("Warning: Corrupted history file, starting fresh")
                    history = []
        except json.JSONDecodeError:
            print("Warning: Corrupted history file, starting fresh")
            history = []
        
        # Process articles
        processed_news = []
        for article in news_data.get('articles', []):
            title = clean_title(article.get('title', ''))
            if not title or title in [h['title'] for h in history]:
                continue
                
            news_item = {
                'title': title,
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'category': get_category(title),
                'timestamp': datetime.now().isoformat()
            }
            processed_news.append(news_item)
            history.append(news_item)
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history[-100:], f)  # Keep last 100 articles
            
        return processed_news[:10]  # Return top 10 articles
        
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

if __name__ == "__main__":
    headlines = get_top_headlines()
    print("\nFinal Headlines:")
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline['title']} - {headline['url']}")
