import json
import os
import re
from datetime import datetime, timedelta

class NewsHistory:
    def __init__(self):
        # Fix path to make it consistent with root project dir
        self.history_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "news_history.json")
        self.history = self._load_history()
    
    def _load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    # Clean old entries (older than 7 days)
                    self.history = self._clean_old_entries(history)
                    return self.history
            except Exception as e:
                print(f"Error loading news history: {str(e)}")
                return []
        return []
    
    def _clean_old_entries(self, history):
        """Remove entries older than 3 days"""
        cutoff = (datetime.now() - timedelta(days=3)).timestamp()
        return [h for h in history if h.get('timestamp', 0) > cutoff]
    
    def _clean_for_comparison(self, text):
        """Clean text for better comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove articles and common filler words
        filler_words = ["the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "by"]
        text = ' '.join([word for word in text.split() if word not in filler_words])
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _similarity_score(self, text1, text2):
        """Calculate similarity between two texts"""
        clean1 = self._clean_for_comparison(text1)
        clean2 = self._clean_for_comparison(text2)
        
        # If either string is empty, return 0
        if not clean1 or not clean2:
            return 0
            
        # Get common words
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        common_words = words1.intersection(words2)
        
        # Calculate Jaccard similarity
        if not words1 or not words2:
            return 0
            
        similarity = len(common_words) / len(words1.union(words2))
        return similarity
    
    def is_duplicate(self, headline, similarity_threshold=0.6):
        """Check if headline is similar to any previously stored headline"""
        clean_headline = headline.strip()
        
        # First check for exact matches after normalization
        normalized_headline = self._clean_for_comparison(clean_headline)
        
        for entry in self.history:
            stored_headline = entry['headline']
            
            # Exact match after normalization
            if self._clean_for_comparison(stored_headline) == normalized_headline:
                print(f"🔄 Exact duplicate found: {stored_headline}")
                return True
                
            # Check similarity score for fuzzy matching
            similarity = self._similarity_score(stored_headline, clean_headline)
            if similarity >= similarity_threshold:
                print(f"🔄 Similar headline found ({similarity:.2f}): {stored_headline}")
                return True
                
        return False
    
    def add_headline(self, headline):
        """Add a new headline to history"""
        self.history.append({
            'headline': headline.strip(),
            'timestamp': datetime.now().timestamp()
        })
        # Save immediately to ensure other processes see this headline
        self.save()
    
    def save(self):
        """Save history to file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        # Clean old entries before saving
        self.history = self._clean_old_entries(self.history)
        
        # Save to file
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
