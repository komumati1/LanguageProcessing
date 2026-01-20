"""
Polish Word Pairs Analyzer
Analyzes bigrams (word pairs) from Polish corpus to determine connection quality
"""

import os
import json
import re
from collections import Counter
from typing import Dict, Tuple, Optional
import requests
from bs4 import BeautifulSoup

class PolishWordPairs:
    def __init__(self):
        self.bigrams: Counter = Counter()
        self.cache_file = os.path.join(os.path.dirname(__file__), "polish_bigrams.json")
        
    def build_from_text(self, text: str):
        """Build bigram dictionary from text"""
        # Clean and tokenize text
        text = text.lower()
        # Remove punctuation except spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split into words
        words = text.split()
        
        # Count bigrams
        for i in range(len(words) - 1):
            word1 = words[i].strip()
            word2 = words[i + 1].strip()
            if word1 and word2:  # Skip empty strings
                pair_key = f"{word1}|{word2}"
                self.bigrams[pair_key] += 1
    
    
    def build_from_wikipedia(self, num_articles=20):
        """
        Build bigram dictionary from Polish Wikipedia articles
        Requires: pip install wikipedia-api
        """
        try:
            import wikipediaapi
            
            print(f"Fetching {num_articles} Polish Wikipedia articles...")
            wiki = wikipediaapi.Wikipedia(
                user_agent='PolishLanguageChecker/1.0 (Educational Project; Python)',
                language='pl'
            )
            
            # Popular Polish topics to fetch
            topics = [
                'Polska', 'Warszawa', 'Kraków', 'Historia Polski', 'Kultura Polski',
                'Język polski', 'Literatura polska', 'Muzyka polska', 'Sport w Polsce',
                'Geografia Polski', 'Przyroda Polski', 'Gospodarka Polski',
                'Polska kuchnia', 'Polskie święta', 'Polacy', 'Wisła (rzeka)',
                'Tatry', 'Morze Bałtyckie', 'Poznań', 'Wrocław', 'Gdańsk',
                'Adam Mickiewicz', 'Fryderyk Chopin', 'Maria Skłodowska-Curie',
                'Jan Paweł II', 'Lech Wałęsa'
            ]
            
            for topic in topics[:num_articles]:
                try:
                    page = wiki.page(topic)
                    if page.exists():
                        print(f"  Fetching: {topic}")
                        text = page.text
                        self.build_from_text(text)
                except Exception as e:
                    print(f"  Error fetching {topic}: {e}")
            
            print(f"Successfully built bigrams from Wikipedia articles!")
            return True
            
        except ImportError:
            print("Wikipedia-API not installed. Install with: pip install wikipedia-api")
            print("Falling back to sample corpus...")
            return False
    
    def build_from_file(self, filepath: str):
        """
        Build bigram dictionary from a text file
        
        Usage:
            analyzer = PolishWordPairs()
            analyzer.build_from_file("polish_corpus.txt")
            analyzer.save_to_file()
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            self.build_from_text(text)
            print(f"Built bigrams from file: {filepath}")
            return True
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def build_from_wikipedia_sample(self):
        """
        Build bigram dictionary from sample Polish text
        This is a fallback method when Wikipedia API is not available
        
        RECOMMENDED: Use build_from_wikipedia() or build_from_file() for better results
        
        To use real corpus:
        1. Install Wikipedia API: pip install wikipedia-api
        2. Or download Polish corpus from:
           - NKJP: http://nkjp.pl/
           - Polish Wikipedia dump: https://dumps.wikimedia.org/plwiki/
           - PolEval datasets: http://poleval.pl/
        """
        print("Using sample corpus (limited). For better results:")
        print("  1. Run: pip install wikipedia-api")
        print("  2. Or download corpus from http://nkjp.pl/")
        
        # Sample Polish text (fallback only)
        sample_texts = [
            """
            Polska jest krajem w Europie Środkowej. Warszawa jest stolicą Polski.
            Polski język jest językiem słowiańskim. Wiele osób mówi po polsku.
            Polska historia jest bardzo ciekawa. Polscy ludzie są gościnni.
            Warszawa ma wiele zabytków. Kraków jest starym miastem.
            Polskie jedzenie jest smaczne. Pierogi są popularne w Polsce.
            Polska literatura jest bogata. Adam Mickiewicz pisał wiersze.
            Polska przyroda jest piękna. Tatry są górami w Polsce.
            Polska muzyka jest znana. Chopin był polskim kompozytorem.
            Polska kultura jest różnorodna. Polskie tradycje są ważne.
            Polska gospodarka się rozwija. Polskie miasta rosną.
            Pies szczeka głośno. Kot miauczy cicho. Ptak śpiewa rano.
            Mały pies biega szybko. Duży kot śpi długo. Ładny ptak leci wysoko.
            Czerwony dom stoi tutaj. Niebieskie auto jedzie tam. Zielone drzewo rośnie wolno.
            Dobry człowiek pomaga innym. Mądra osoba uczy się dużo. Silny mężczyzna pracuje ciężko.
            Młoda kobieta czyta książkę. Stary dziadek opowiada historię. Małe dziecko bawi się zabawką.
            Pan ma psa. Pani ma kota. Dziecko ma piłkę.
            Pies lubi kości. Kot lubi mleko. Ptak lubi ziarno.
            Dom jest duży. Pokój jest mały. Okno jest szerokie.
            Słońce świeci jasno. Księżyc świeci nocą. Gwiazdy błyszczą pięknie.
            Woda jest czysta. Powietrze jest świeże. Ziemia jest okrągła.
            """,
            """
            Polski pies szczeka na kota. Kot ucieka przed psem. Ptak obserwuje wszystko z góry.
            Mały chłopiec bawi się z psem. Mała dziewczynka głaszcze kota. Rodzice patrzą na dzieci.
            W Polsce jest dużo lasów. Las jest zielony i gęsty. Drzewa rosną wysoko.
            Polska zima jest mroźna. Śnieg pada często. Dzieci lubią zimę.
            Polskie lato jest ciepłe. Słońce świeci długo. Ludzie jeżdżą nad morze.
            Polska wiosna jest piękna. Kwiaty zaczynają kwitnąć. Ptaki wracają z ciepłych krajów.
            Polska jesień jest kolorowa. Liście spadają z drzew. Pogoda jest zmienna.
            """,
            """
            Dobry pies słucha pana. Mądry kot poluje na myszy. Śpiewający ptak budzi rano.
            Polski student uczy się pilnie. Polska studentka czyta dużo książek. Profesor wykłada interesująco.
            Stary zamek stoi na wzgórzu. Nowy budynek wyrasta w centrum. Piękna katedra dominuje w mieście.
            Polska flaga ma białe i czerwone kolory. Godło Polski to orzeł biały. Hymn polski jest podniosły.
            Polskie góry są wysokie. Polskie rzeki są długie. Polskie jeziora są czyste.
            """
        ]
        
        # Build bigrams from all sample texts
        for text in sample_texts:
            self.build_from_text(text)
    
    def save_to_file(self):
        """Save bigram dictionary to JSON file"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(dict(self.bigrams), f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.bigrams)} bigrams to {self.cache_file}")
    
    def load_from_file(self) -> bool:
        """Load bigram dictionary from JSON file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bigrams = Counter(data)
                print(f"Loaded {len(self.bigrams)} bigrams from cache")
                return True
            except Exception as e:
                print(f"Error loading cache: {e}")
                return False
        return False
    
    def get_pair_frequency(self, word1: str, word2: str) -> int:
        """Get frequency count for a word pair"""
        word1 = word1.lower().strip()
        word2 = word2.lower().strip()
        pair_key = f"{word1}|{word2}"
        return self.bigrams.get(pair_key, 0)
    
    def analyze_sentence_connections(self, sentence: str) -> list:
        """
        Analyze all word pair connections in a sentence
        Returns list of tuples: (word1, word2, count, color)
        """
        # Clean and tokenize
        sentence = sentence.lower()
        sentence = re.sub(r'[^\w\s]', ' ', sentence)
        words = [w.strip() for w in sentence.split() if w.strip()]
        
        connections = []
        for i in range(len(words) - 1):
            word1 = words[i]
            word2 = words[i + 1]
            count = self.get_pair_frequency(word1, word2)
            
            # Determine color based on frequency
            if count == 0:
                color = 'red'
            elif count <= 5:
                color = 'orange'
            else:
                color = 'green'
            
            connections.append((word1, word2, count, color))
        
        return connections

# Global instance
_word_pairs_instance: Optional[PolishWordPairs] = None

def get_word_pairs_analyzer() -> PolishWordPairs:
    """Get or create the global word pairs analyzer instance"""
    global _word_pairs_instance
    if _word_pairs_instance is None:
        _word_pairs_instance = PolishWordPairs()
        # Try to load from cache first
        if not _word_pairs_instance.load_from_file():
            # Try to build from Wikipedia
            print("No cache found. Attempting to build from Wikipedia...")
            if not _word_pairs_instance.build_from_wikipedia(num_articles=25):
                # Fall back to sample if Wikipedia fails
                _word_pairs_instance.build_from_wikipedia_sample()
            _word_pairs_instance.save_to_file()
    return _word_pairs_instance

if __name__ == "__main__":
    """
    Example usage:
    
    # Option 1: Build from Wikipedia (recommended)
    analyzer = PolishWordPairs()
    if analyzer.build_from_wikipedia(num_articles=25):
        analyzer.save_to_file()
    
    # Option 2: Build from your own text file
    analyzer = PolishWordPairs()
    analyzer.build_from_file("path/to/polish_corpus.txt")
    analyzer.save_to_file()
    
    # Option 3: Use sample (fallback)
    analyzer = PolishWordPairs()
    analyzer.build_from_wikipedia_sample()
    analyzer.save_to_file()
    """
    
    # Try Wikipedia first, fall back to sample
    analyzer = PolishWordPairs()
    if not analyzer.build_from_wikipedia(num_articles=25):
        analyzer.build_from_wikipedia_sample()
    analyzer.save_to_file()
    
    # Test queries
    print(f"\n'pies szczeka': {analyzer.get_pair_frequency('pies', 'szczeka')}")
    print(f"'kot miauczy': {analyzer.get_pair_frequency('kot', 'miauczy')}")
    
    # Test sentence analysis
    test_sentence = "mały pies szczeka głośno"
    connections = analyzer.analyze_sentence_connections(test_sentence)
    print(f"\nConnections in '{test_sentence}':")
    for w1, w2, count, color in connections:
        print(f"  [{w1}] → [{w2}]: {count} ({color})")
