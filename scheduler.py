from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from news_fetcher import get_top_headlines
from slide_generator import generate_all_slides
from insta_poster import post_carousel
import os
import atexit
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🔐 Optional token for securing health route
HEALTH_TOKEN = os.getenv("HEALTH_TOKEN", "news123")

# 🧹 Clear history at midnight
def clear_history():
    try:
        if os.path.exists('news_history.json'):
            os.remove('news_history.json')
            print(f"🧹 Cleared news history at {datetime.now()}")
    except Exception as e:
        print(f"❌ Error clearing history: {e}")

# 📢 Post news job
def post_news_job():
    print(f"📢 Posting news job started at {datetime.now()}")
    try:
        headlines = get_top_headlines()
        if not headlines:
            print("❌ No headlines to post")
            return
        
        slides = generate_all_slides(headlines)
        if not slides:
            print("❌ No slides generated")
            return
        
        post_carousel(slides, headlines)
        print("✅ Post job completed")

    except Exception as e:
        print(f"❌ Error in post_news_job: {e}")

# ✅ Home route
@app.route('/')
def home():
    return '''
        <h2>👋 AI Insta News Bot</h2>
        <p>This bot posts top 10 news to Instagram every morning automatically.</p>
        <a href="/health">🔍 Health Check</a>
    '''

# ✅ Health check route
@app.route('/health')
def health_check():
    token = request.args.get('token')
    if token != HEALTH_TOKEN:
        return {"error": "unauthorized"}, 403

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

# 🔁 Graceful shutdown
scheduler = BackgroundScheduler()

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler shut down gracefully")

if __name__ == "__main__":
    atexit.register(shutdown_scheduler)

    # 🕔 Post every hour between 5–8 AM
    scheduler.add_job(
        post_news_job,
        CronTrigger(hour='5,6,7,8', minute='4'),
        id='post_news'
    )

    # 🧹 Clean history daily at midnight
    scheduler.add_job(
        clear_history,
        CronTrigger(hour=0, minute=0),
        id='clear_history'
    )

    # 🚀 Start the scheduler
    scheduler.start()
    print("⏰ Scheduler started (posts at 5 AM, 6 AM, 7 AM, 8 AM)")

    # Show next run
    if scheduler.get_jobs():
        next_run = scheduler.get_job('post_news').next_run_time
        print(f"📅 Next post scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

    # 🌐 Run Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
