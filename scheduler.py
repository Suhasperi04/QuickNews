from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from news_fetcher import get_top_headlines, NewsHistory
from slide_generator import generate_all_slides
from insta_poster import post_carousel
import os

def clear_history():
    """Clear news history daily at midnight"""
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
        
        # Update Linktree
        update_linktree(headlines)
        
    except Exception as e:
        print(f"❌ Post job failed: {e}")

def update_linktree(headlines):
    """Update Linktree HTML with today's news links"""
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%I:%M %p')
        
        # Create links directory if not exists
        os.makedirs("links", exist_ok=True)
        
        # Create daily links file
        links_file = f"links/{date_str}.html"
        
        # Read existing content or create new
        links_content = {}
        if os.path.exists(links_file):
            with open(links_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse existing content (basic parsing)
                for line in content.split('\n'):
                    if ' | ' in line:
                        t, urls = line.split(' | ', 1)
                        links_content[t] = urls
        
        # Add new links
        links_content[time_str] = '\n'.join([
            f'<p><a href="{news["url"]}" target="_blank">{news["title"]}</a></p>'
            for news in headlines
        ])
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>News Links - {date_str}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1, h2 {{
            color: #333;
            border-bottom: 2px solid #ddd;
            padding-bottom: 10px;
        }}
        .time-block {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        a {{
            color: #2196F3;
            text-decoration: none;
            line-height: 1.6;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .time {{
            font-weight: bold;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>News Links - {date_str}</h1>
"""
        
        # Add each time block
        for time, links in sorted(links_content.items(), reverse=True):
            html += f"""
    <div class="time-block">
        <h2 class="time">{time}</h2>
        {links}
    </div>"""
        
        html += """
</body>
</html>"""
        
        # Save file
        with open(links_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"✅ Updated Linktree for {date_str} at {time_str}")
        
    except Exception as e:
        print(f"❌ Error updating Linktree: {e}")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    
    # Schedule posts at fixed times (9 AM, 1 PM, 5 PM, 9 PM)
    scheduler.add_job(
        post_news_job,
        CronTrigger(hour='4,5,7,8', minute='17'),
        id='post_news'
    )
    
    # Clear history daily at midnight
    scheduler.add_job(
        clear_history,
        CronTrigger(hour=0, minute=0),
        id='clear_history'
    )
    
    scheduler.start()
    print("⏰ Scheduler started (posts at 9 AM, 1 PM, 5 PM, 9 PM)")
    
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