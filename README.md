# 🤖 AI News Instagram Bot

Automatically fetch trending news headlines and post them as beautiful Instagram carousels.

## 🌟 Features

- 🔎 Fetches trending news from NewsAPI
- 🖼️ Generates visually appealing carousel slides
- 📤 Posts to Instagram automatically every 5 hours
- 🖥️ Web dashboard to control the bot
- 🔐 Secure session-based Instagram login
- ⚙️ Reliable background scheduling

## 🚀 Setup

1. Create a `.env` file with your credentials:
```
NEWS_API_KEY=your_newsapi_key
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask dashboard:
```bash
python dashboard/app.py
```

4. Start the scheduler:
```bash
python scheduler.py
```

## 🔧 Components

- `news_fetcher.py`: Fetches and filters news headlines
- `slide_generator.py`: Creates Instagram-ready carousel slides
- `insta_poster.py`: Handles Instagram authentication and posting
- `scheduler.py`: Manages automated posting schedule
- `dashboard/`: Web interface to control the bot

## 📝 Notes

- The bot will pause if less than 2 headlines are available
- Content is filtered for safe, family-friendly news
- Instagram session is saved to avoid frequent logins
- Default posting interval is 5 hours

## 🔒 Security

- Credentials are stored in `.env` file (not in git)
- Instagram session is stored securely in `creds/session.json`
- Web dashboard requires authentication

## ⚠️ Important

1. Get your NewsAPI key from: https://newsapi.org
2. Use a test Instagram account first
3. Keep your credentials secure
4. Monitor the bot's activity regularly
