import json
import os
from datetime import datetime, timedelta

class NewsHistory:
    def __init__(self):
        self.history_file = "utils/news_history.json"
        self.history = self._load_history()
    
    def _load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    # Clean old entries (older than 7 days)
                    self._clean_old_entries(history)
                    return history
            except:
                return []
        return []
    
    def _clean_old_entries(self, history):
        """Remove entries older than 7 days"""
        cutoff = (datetime.now() - timedelta(days=7)).timestamp()
        return [h for h in history if h.get('timestamp', 0) > cutoff]
    
    def is_duplicate(self, headline):
        """Check if headline was posted in the last 7 days"""
        clean_headline = headline.strip().lower()
        for entry in self.history:
            if entry['headline'].strip().lower() == clean_headline:
                return True
        return False
    
    def add_headline(self, headline):
        """Add a new headline to history"""
        self.history.append({
            'headline': headline.strip(),
            'timestamp': datetime.now().timestamp()
        })
    
    def save(self):
        """Save history to file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        # Clean old entries before saving
        self.history = self._clean_old_entries(self.history)
        
        # Save to file
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
