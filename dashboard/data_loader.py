"""Data loading utilities for the dashboard."""
import os
import pickle
import streamlit as st
import pandas as pd
from collections import Counter


def get_project_paths():
    """Get paths to data files."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    return {
        'data_csv': os.path.join(parent_dir, 'data.csv'),
        'input_txt': os.path.join(parent_dir, 'input.txt'),
        'cache_file': os.path.join(parent_dir, 'bigram_cache.pkl')
    }


@st.cache_data
def load_word_frequency_data():
    """Load main word frequency data from CSV."""
    paths = get_project_paths()
    data_df = pd.read_csv(paths['data_csv'])
    return data_df


@st.cache_data
def load_word_connections():
    """Load or generate word connections (bigrams) with caching."""
    paths = get_project_paths()
    cache_path = paths['cache_file']
    input_path = paths['input_txt']
    
    # Try to load from cache first
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            return cached_data['bigram_counts'], cached_data['word_count'], True
        except Exception:
            pass  # Cache invalid, will regenerate
    
    # Generate from input.txt
    if not os.path.exists(input_path):
        return None, 0, False
    
    bigrams = []
    word_count = 0
    max_words = 100000  # Limit to 100k words
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                words = line.strip().split()
                
                # Stop if we've processed enough words
                if word_count + len(words) > max_words:
                    remaining = max_words - word_count
                    words = words[:remaining]
                    
                    for i in range(len(words) - 1):
                        bigrams.append((words[i], words[i + 1]))
                    word_count += len(words)
                    break
                
                # Create bigrams
                for i in range(len(words) - 1):
                    bigrams.append((words[i], words[i + 1]))
                
                word_count += len(words)
        
        # Count bigram frequencies
        bigram_counts = Counter(bigrams)
        
        # Save to cache
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'bigram_counts': bigram_counts,
                    'word_count': word_count
                }, f)
        except Exception:
            pass  # Cache save failed, but we have the data
        
        return bigram_counts, word_count, False
        
    except Exception as e:
        st.error(f"Błąd podczas ładowania danych: {str(e)}")
        return None, 0, False
