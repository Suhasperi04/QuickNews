from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from news_fetcher import get_top_headlines, NewsHistory
from slide_generator import generate_all_slides
from insta_poster import post_carousel
import os

def clear_history():
    """Clear news history every 3 days at midnight"""
    try:
        if os.path.exists("news_history.json"):
            os.remove("news_history.json")
        print("🗑️ Cleared news history")
        
        # Create empty history file
        history = NewsHistory()
        history.save()
    except Exception as e:
        print(f"❌ Error clearing history: {e}")

def post_news_job():
    try:
        print("\n" + "="*50)
        print(f"📅 Starting post job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        headlines = get_top_headlines()
        if not headlines:
            print("❌ No headlines available. Skipping post.")
            return
            
        print(f"📰 Got {len(headlines)} headlines")
        print("\n🎨 Generating slides...")
        generate_all_slides(headlines)
        
        print("\n📤 Posting to Instagram...")
        post_carousel(headlines)
        
    except Exception as e:
        print(f"❌ Post job failed: {e}")



if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    
    # Schedule posts at fixed times (10 AM, 6 PM) - reduced frequency to avoid Instagram restrictions
    scheduler.add_job(
        post_news_job,
        CronTrigger(hour='10,18', minute='01'),
        id='post_news'
    )
    
    # Clear history every 3 days at midnight
    scheduler.add_job(
        clear_history,
        CronTrigger(day_of_week='0,3', hour=0, minute=0),
        id='clear_history'
    )
    
    scheduler.start()
    print("⏰ Scheduler started (posts at 10 AM and 6 PM)")
    
    # Run first post immediately if within posting hours
    current_hour = datetime.now().hour
    if current_hour in [9, 13, 17, 21]:
        print("📝 First post will start momentarily...")
        post_news_job()
    else:
        next_run = scheduler.get_job('post_news').next_run_time
        print(f"📅 Next post scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Keep the script running
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()