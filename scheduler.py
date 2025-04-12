from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from news_fetcher import get_top_headlines
from slide_generator import generate_all_slides
from insta_poster import post_carousel
import os
import atexit

app = Flask(__name__)

def clear_history():
    """Clear news history daily at midnight"""
    try:
        if os.path.exists('news_history.json'):
            os.remove('news_history.json')
            print("🗑️ Cleared news history")
    except Exception as e:
        print(f"❌ Error clearing history: {e}")

def post_news_job():
    """Post news to Instagram"""
    try:
        # Get headlines
        headlines = get_top_headlines()
        if not headlines:
            print("❌ No headlines to post")
            return
            
        # Generate slides
        slides = generate_all_slides(headlines)
        if not slides:
            print("❌ No slides generated")
            return
            
        # Post to Instagram
        post_carousel(slides, headlines)
        
    except Exception as e:
        print(f"❌ Error in post_news_job: {e}")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        jobs = scheduler.get_jobs()
        next_run = None
        if jobs:
            next_job = min(jobs, key=lambda x: x.next_run_time if x.next_run_time else datetime.max)
            next_run = next_job.next_run_time.isoformat() if next_job.next_run_time else None
        
        return {
            'status': 'healthy',
            'last_check': datetime.now().isoformat(),
            'next_post': next_run,
            'active_jobs': len(jobs)
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }, 500

# Global scheduler instance
scheduler = BackgroundScheduler()

def shutdown_scheduler():
    """Shut down the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler shut down gracefully")

if __name__ == "__main__":
    # Register shutdown function
    atexit.register(shutdown_scheduler)
    
    # Schedule posts at fixed times (5 AM, 6 AM, 7 AM, 8 AM)
    scheduler.add_job(
        post_news_job,
        CronTrigger(hour='5,6,7,8', minute='4'),
        id='post_news'
    )
    
    # Schedule daily history clear at midnight
    scheduler.add_job(
        clear_history,
        CronTrigger(hour=0, minute=0),
        id='clear_history'
    )
    
    # Start the scheduler
    scheduler.start()
    print("⏰ Scheduler started (posts at 5 AM, 6 AM, 7 AM, 8 AM)")
    
    # Get next post time
    if scheduler.get_jobs():
        next_run = scheduler.get_job('post_news').next_run_time
        print(f"📅 Next post scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)