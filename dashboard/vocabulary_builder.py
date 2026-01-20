"""Vocabulary builder - downloads Polish texts and builds expanded vocabulary."""
import os
import re
import pickle
import requests
from collections import Counter, defaultdict


class PolishVocabularyBuilder:
    """Downloads Polish texts and builds vocabulary database."""
    
    def __init__(self, cache_file='polish_vocabulary_expanded.pkl'):
        """Initialize builder with cache file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        self.cache_path = os.path.join(parent_dir, cache_file)
        
        self.words = Counter()
        self.word_contexts = defaultdict(list)
    
    def download_polish_gutenberg_texts(self):
        """Download Polish texts from Project Gutenberg."""
        polish_books = [
            "https://www.gutenberg.org/cache/epub/28515/pg28515.txt",  # Pan Tadeusz
            "https://www.gutenberg.org/files/63105/63105-0.txt",  # Polish fairy tales
        ]
        
        texts = []
        for url in polish_books:
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    texts.append(response.text)
                    print(f"Downloaded: {url}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")
        
        return texts
    
    def download_polish_wikipedia_sample(self):
        """Download sample Polish Wikipedia content."""
        # Wikipedia API for Polish articles
        api_url = "https://pl.wikipedia.org/w/api.php"
        
        # Get popular Polish articles
        popular_titles = [
            "Polska", "Warszawa", "Kraków", "Historia_Polski",
            "Język_polski", "Literatura_polska", "Kultura_polska",
            "Geografia_Polski", "Polska_kuchnia", "Sport_w_Polsce"
        ]
        
        texts = []
        for title in popular_titles:
            try:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': title,
                    'prop': 'extracts',
                    'explaintext': True
                }
                
                response = requests.get(api_url, params=params, timeout=10)
                data = response.json()
                
                pages = data.get('query', {}).get('pages', {})
                for page_data in pages.values():
                    if 'extract' in page_data:
                        texts.append(page_data['extract'])
                        print(f"Downloaded Wikipedia: {title}")
                
            except Exception as e:
                print(f"Error downloading {title}: {e}")
        
        return texts
    
    def get_fallback_polish_texts(self):
        """Fallback Polish texts for offline use."""
        return [
            """
            Polska jest krajem w Europie Środkowej. Stolica Polski to Warszawa.
            Język polski należy do grupy języków słowiańskich. Polacy są dumni
            ze swojej historii i kultury. Polska ma piękne góry, morze i jeziora.
            Polska kuchnia jest znana z pierogów, bigosu i żurku.
            """,
            """
            Kraków to jedno z najstarszych miast w Polsce. Wawel jest symbolem
            Krakowa. Stare miasto w Krakowie jest na liście UNESCO. Kraków był
            stolicą Polski przez wiele lat. Uniwersytet Jagielloński to najstarsza
            uczelnia w Polsce.
            """,
            """
            Morze Bałtyckie jest zimne ale piękne. Polska ma długie wybrzeże.
            Plaże nad Bałtykiem są popularne latem. Gdańsk, Gdynia i Sopot
            tworzą Trójmiasto. Nad morzem można spotkać wiele turystów.
            """,
            """
            Tatry to najwyższe góry w Polsce. Zakopane to stolica Tatr.
            W Tatrach można wędrować i jeździć na nartach. Morskie Oko to
            piękne jezioro górskie. Tatry są częścią Karpat.
            """,
            """
            Polski system edukacji jest dobry. Polskie szkoły uczą wiele przedmiotów.
            Studenci mogą studiować na uniwersytetach. Nauka jest ważna dla rozwoju.
            Polska nauka ma wielkie tradycje.
            """
        ]
    
    def clean_and_tokenize(self, text):
        """Clean text and extract words."""
        # Remove special characters, keep Polish letters
        text = re.sub(r'[^a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s]', ' ', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        # Convert to lowercase and split
        words = text.lower().split()
        return words
    
    def analyze_texts(self, texts):
        """Analyze texts and extract vocabulary."""
        all_words = []
        
        for text in texts:
            words = self.clean_and_tokenize(text)
            all_words.extend(words)
            
            # Store some context for each word
            for i, word in enumerate(words):
                context_start = max(0, i - 2)
                context_end = min(len(words), i + 3)
                context = ' '.join(words[context_start:context_end])
                self.word_contexts[word].append(context)
        
        self.words = Counter(all_words)
        return self.words
    
    def get_most_common_words(self, n=500):
        """Get N most common words."""
        return self.words.most_common(n)
    
    def save_to_cache(self):
        """Save vocabulary to cache."""
        try:
            data = {
                'words': self.words,
                'word_contexts': dict(self.word_contexts)
            }
            with open(self.cache_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"Vocabulary saved to cache: {len(self.words)} unique words")
            return True
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False
    
    def load_from_cache(self):
        """Load vocabulary from cache."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'rb') as f:
                    data = pickle.load(f)
                    self.words = data['words']
                    self.word_contexts = defaultdict(list, data['word_contexts'])
                print(f"Loaded vocabulary from cache: {len(self.words)} unique words")
                return True
            except Exception:
                return False
        return False
    
    def build_vocabulary(self, force_download=False):
        """Build vocabulary from internet sources."""
        if not force_download and self.load_from_cache():
            return self.words
        
        print("Building Polish vocabulary from internet sources...")
        
        all_texts = []
        
        # Try to download from various sources
        print("\n1. Downloading from Project Gutenberg...")
        gutenberg_texts = self.download_polish_gutenberg_texts()
        all_texts.extend(gutenberg_texts)
        
        print("\n2. Downloading from Wikipedia...")
        wiki_texts = self.download_polish_wikipedia_sample()
        all_texts.extend(wiki_texts)
        
        # Use fallback if nothing downloaded
        if not all_texts:
            print("\n3. Using fallback texts...")
            all_texts = self.get_fallback_polish_texts()
        
        print(f"\nTotal texts collected: {len(all_texts)}")
        print("Analyzing vocabulary...")
        
        self.analyze_texts(all_texts)
        self.save_to_cache()
        
        return self.words


def get_expanded_vocabulary():
    """Get or build expanded Polish vocabulary."""
    builder = PolishVocabularyBuilder()
    words = builder.build_vocabulary()
    return builder


if __name__ == "__main__":
    # Test the builder
    print("Testing Polish Vocabulary Builder...")
    builder = get_expanded_vocabulary()
    
    print(f"\nTotal unique words: {len(builder.words)}")
    print("\nTop 20 most common words:")
    for word, count in builder.get_most_common_words(20):
        print(f"  {word}: {count}")
