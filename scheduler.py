from flask import Flask, render_template, request, redirect, url_for, session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from news_fetcher import get_top_headlines
from slide_generator import generate_all_slides
from insta_poster import post_carousel
from utils.instagram_auth import get_client
import os
import atexit
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

# Global scheduler instance
scheduler = BackgroundScheduler()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def post_news_job():
    """Post news to Instagram"""
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

@app.route('/')
@login_required
def dashboard():
    status = "Running" if scheduler.running else "Stopped"
    return render_template('dashboard.html', status=status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        verification_code = request.form.get('verification_code')
        
        try:
            if 'challenge_required' in session:
                # Handle verification code submission
                client = session['client']
                if client.challenge_code(verification_code):
                    session['logged_in'] = True
                    session.pop('challenge_required', None)
                    session.pop('client', None)
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('login.html', error="Invalid verification code", show_verification=True)
            else:
                # Initial login attempt
                client = get_client(force_login=True)
                if getattr(client, 'challenge_required', False):
                    session['challenge_required'] = True
                    session['client'] = client
                    return render_template('login.html', error="Verification required", show_verification=True)
                
                session['logged_in'] = True
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            error_msg = str(e)
            if "challenge_required" in error_msg.lower():
                session['challenge_required'] = True
                return render_template('login.html', error="Verification required", show_verification=True)
            return render_template('login.html', error=f"Login failed: {error_msg}")
            
    return render_template('login.html', show_verification='challenge_required' in session)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/start', methods=['POST'])
@login_required
def start_posting():
    if not scheduler.running:
        # Schedule posts every hour between 5-8 AM
        scheduler.add_job(
            post_news_job,
            CronTrigger(hour='5,6,7,8', minute='4'),
            id='post_news'
        )
        scheduler.start()
        print("⏰ Scheduler started")
    return redirect(url_for('dashboard'))

@app.route('/stop', methods=['POST'])
@login_required
def stop_posting():
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler stopped")
    return redirect(url_for('dashboard'))

def shutdown_scheduler():
    """Shut down the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler shut down gracefully")

if __name__ == "__main__":
    # Register shutdown function
    atexit.register(shutdown_scheduler)
    
    # Run Flask app
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
