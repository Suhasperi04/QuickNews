import os
from gnews import GNews
from dotenv import load_dotenv
from utils.news_history import NewsHistory
import json
import random
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

def get_news_by_category(google_news, category, count=5):
    try:
        if category == "trending":
            news = google_news.get_top_news()
        elif category == "india":
            news = google_news.get_news("India")
        else:
            news = google_news.get_news_by_topic(category)
        
        headlines_with_urls = []
        seen_titles = set()
        
        def add_article(article):
            title = clean_title(article.get('title', ''))
            if not title:  # Skip incomplete titles
                return False
                
            if (title not in seen_titles and 
                is_safe_news(title) and 
                not NewsHistory().is_duplicate(title)):
                headlines_with_urls.append({
                    'title': title,
                    'url': article.get('url', ''),
                    'category': category
                })
                seen_titles.add(title)
                NewsHistory().add_headline(title)
                print(f"✅ Added ({category}): {title}")
                return True
            else:
                print(f"⚠️ Skipped ({category}): {title}")
                return False

        for article in news:
            title = article.get('title', '')
            if not title:
                continue
                
            title = clean_title(title)
            
            if len(headlines_with_urls) >= count:
                break
            add_article(article)
                
        return headlines_with_urls
    except Exception as e:
        print(f"❌ Error fetching {category} news: {str(e)}")
        return []

def get_top_headlines():
    news_history = NewsHistory()
    google_news = GNews(language='en', country='IN', max_results=30)  # Increased max results
    
    # Categories to fetch news from with target counts
    categories = [
        ('trending', 3),
        ('india', 2),
        ('business', 2),
        ('technology', 1),
        ('sports', 1),
        ('entertainment', 1)
    ]
    backup_categories = ['world', 'science', 'health']
    
    headlines_with_urls = []
    seen_titles = set()
    target_count = 10  # Need 10 news items + 1 title slide = 11 total
    
    def add_article(article, category):
        title = clean_title(article.get('title', ''))
        if not title:  # Skip incomplete titles
            return False
            
        if title not in seen_titles and is_safe_news(title):
            # Extract full URL and description
            url = article.get('url', '')
            if not url.startswith('http'):
                return False
                
            description = article.get('description', '')
            if description:
                description = clean_title(description)  # Clean description too
                
            headlines_with_urls.append({
                'title': title,
                'url': url,
                'category': category,
                'description': description
            })
            seen_titles.add(title)
            print(f"✅ Added ({category}): {title}")
            return True
        else:
            print(f"⚠️ Skipped ({category}): {title}")
            return False

    # Fetch news from primary categories
    for category, target in categories:
        print(f"\n📰 Fetching {category} news...")
        try:
            if category == "trending":
                articles = google_news.get_top_news()
            elif category == "india":
                articles = google_news.get_news("India")
            else:
                articles = google_news.get_news_by_topic(category)
            
            # Try to get the target number for this category
            added = 0
            for article in articles:
                if added >= target:
                    break
                if add_article(article, category):
                    added += 1
                if len(headlines_with_urls) >= target_count:
                    break
                    
            if len(headlines_with_urls) >= target_count:
                break
                
        except Exception as e:
            print(f"❌ Error fetching {category} news: {str(e)}")
            continue

    # If we don't have enough headlines, try backup categories
    if len(headlines_with_urls) < target_count:
        remaining = target_count - len(headlines_with_urls)
        for category in backup_categories:
            if len(headlines_with_urls) >= target_count:
                break
                
            print(f"\n📰 Fetching {category} news (backup)...")
            try:
                articles = google_news.get_news_by_topic(category)
                added = 0
                for article in articles:
                    if added >= remaining:
                        break
                    if add_article(article, category):
                        added += 1
                    if len(headlines_with_urls) >= target_count:
                        break
            except Exception as e:
                print(f"❌ Error fetching {category} news: {str(e)}")
                continue

    print(f"\n📰 Final headlines count: {len(headlines_with_urls)}")
    return headlines_with_urls

class NewsHistory:
    def __init__(self):
        self.history_file = "news_history.json"
        self.headlines = set()
        # Clear history by initializing empty set
        self.save()  # Save empty history
        
    def is_duplicate(self, headline):
        return False  # Always return False during testing
        
    def add_headline(self, headline):
        self.headlines.add(headline)
        self.save()
        
    def save(self):
        with open(self.history_file, 'w') as f:
            json.dump(list(self.headlines), f)

if __name__ == "__main__":
    headlines = get_top_headlines()
    print("\nFinal Headlines:")
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline['title']} - {headline['url']}")
