"""Polish corpus analyzer - downloads and analyzes Polish texts for word connections."""
import os
import pickle
import re
from collections import Counter
import requests
from bs4 import BeautifulSoup


class PolishCorpusAnalyzer:
    """Analyzes Polish text corpus for word pair frequencies."""
    
    def __init__(self, cache_file='polish_corpus_cache.pkl'):
        """Initialize analyzer with cache file path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        self.cache_path = os.path.join(parent_dir, cache_file)
        self.bigrams = Counter()
        self.total_bigrams = 0
        
    def download_polish_wikipedia_texts(self, num_articles=15):
        """Download sample Polish Wikipedia articles."""
        texts = []
        
        # Polish Wikipedia API - get random articles
        api_url = "https://pl.wikipedia.org/w/api.php"
        
        try:
            # Get random article titles
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnnamespace': 0,
                'rnlimit': num_articles
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
            
            # Get content for each article
            for article in data['query']['random']:
                title = article['title']
                
                # Get article content
                content_params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': title,
                    'prop': 'extracts',
                    'explaintext': True,
                    'exsectionformat': 'plain'
                }
                
                content_response = requests.get(api_url, params=content_params, timeout=10)
                content_data = content_response.json()
                
                pages = content_data['query']['pages']
                for page_id, page_data in pages.items():
                    if 'extract' in page_data:
                        texts.append(page_data['extract'])
            
            return texts
            
        except Exception as e:
            print(f"Error downloading Wikipedia texts: {e}")
            # Fallback to sample Polish texts
            return self._get_fallback_texts()
    
    def _get_fallback_texts(self):
        """Fallback Polish texts if download fails."""
        return [
            "Polska jest krajem w Europie Środkowej. Warszawa jest stolicą Polski.",
            "Język polski należy do grupy języków zachodniosłowiańskich. Polski alfabet ma trzydzieści dwie litery.",
            "Polska ma bogatą historię i kulturę. Polscy naukowcy wnieśli wielki wkład do nauki.",
            "Polska kuchnia jest znana na całym świecie. Pierogi i bigos to typowe polskie potrawy.",
            "Polskie miasta są pełne zabytków. Kraków i Gdańsk to piękne miasta.",
            "Polska literatura ma długą tradycję. Adam Mickiewicz to wielki polski poeta.",
            "Polska gospodarka rozwija się dynamicznie. Polski rynek jest atrakcyjny dla inwestorów.",
            "Polskie góry są popularne wśród turystów. Tatry to najwyższe góry w Polsce.",
            "Polska ma dostęp do Morza Bałtyckiego. Polskie plaże są piękne latem.",
            "Polski system edukacji jest dobry. Polskie uniwersytety kształcą wielu studentów."
        ]
    
    def clean_text(self, text):
        """Clean and normalize text."""
        # Remove special characters, keep only letters and spaces
        text = re.sub(r'[^a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s]', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.lower()
    
    def analyze_corpus(self, texts):
        """Analyze texts and build bigram frequency dictionary."""
        all_bigrams = []
        
        for text in texts:
            cleaned = self.clean_text(text)
            words = cleaned.split()
            
            # Create bigrams
            for i in range(len(words) - 1):
                bigram = (words[i], words[i + 1])
                all_bigrams.append(bigram)
        
        self.bigrams = Counter(all_bigrams)
        self.total_bigrams = len(all_bigrams)
        
        return self.bigrams
    
    def get_connection_strength(self, word1, word2):
        """
        Get connection strength between two words.
        Returns: (strength, color)
        - strength: frequency count
        - color: 'green' (frequent), 'orange' (rare), 'red' (none)
        """
        bigram = (word1.lower(), word2.lower())
        count = self.bigrams.get(bigram, 0)
        
        if count == 0:
            return 0, 'red'
        elif count >= 3:  # Frequent connection
            return count, 'green'
        else:  # Rare connection (1-2 occurrences)
            return count, 'orange'
    
    def save_to_cache(self):
        """Save analyzed corpus to cache file."""
        try:
            with open(self.cache_path, 'wb') as f:
                pickle.dump({
                    'bigrams': self.bigrams,
                    'total_bigrams': self.total_bigrams
                }, f)
            return True
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False
    
    def load_from_cache(self):
        """Load analyzed corpus from cache file."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'rb') as f:
                    data = pickle.load(f)
                    self.bigrams = data['bigrams']
                    self.total_bigrams = data['total_bigrams']
                return True
            except Exception:
                return False
        return False
    
    def analyze_sentence(self, sentence):
        """
        Analyze sentence and return word connections with colors.
        Returns: list of (word1, word2, count, color)
        """
        words = self.clean_text(sentence).split()
        connections = []
        
        for i in range(len(words) - 1):
            count, color = self.get_connection_strength(words[i], words[i + 1])
            connections.append((words[i], words[i + 1], count, color))
        
        return connections


# Global analyzer instance
_analyzer = None

def get_analyzer():
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = PolishCorpusAnalyzer()
        
        # Try to load from cache
        if not _analyzer.load_from_cache():
            # Download and analyze if cache doesn't exist
            print("Downloading Polish texts...")
            texts = _analyzer.download_polish_wikipedia_texts(15)
            print(f"Analyzing {len(texts)} texts...")
            _analyzer.analyze_corpus(texts)
            _analyzer.save_to_cache()
            print("Analysis complete and cached!")
    
    return _analyzer
