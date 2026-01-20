"""Enhanced Polish language checker with expanded vocabulary from internet sources."""
from polish_data import NOUNS, ADJECTIVES, VERBS, get_all_word_forms
from vocabulary_builder import get_expanded_vocabulary


# Initialize expanded vocabulary
_expanded_vocab = None

def get_expanded_words():
    """Get expanded vocabulary set."""
    global _expanded_vocab
    if _expanded_vocab is None:
        builder = get_expanded_vocabulary()
        # Get all words from builder
        _expanded_vocab = set(builder.words.keys())
    return _expanded_vocab


def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def find_closest_word(word, max_distance=3):
    """Find closest matching word using Levenshtein distance from both dictionaries."""
    # Check original forms first
    all_forms = get_all_word_forms()
    
    # Then check expanded vocabulary
    expanded_words = get_expanded_words()
    all_words = list(all_forms) + list(expanded_words)
    
    closest_word = None
    min_distance = float('inf')
    
    for form in all_words:
        distance = levenshtein_distance(word.lower(), form.lower())
        if distance < min_distance and distance <= max_distance:
            min_distance = distance
            closest_word = form
    
    return closest_word, min_distance if closest_word else None


def get_autocomplete_suggestions(partial_word, max_suggestions=5):
    """Get autocomplete suggestions from both original and expanded vocabulary."""
    if not partial_word:
        return []
    
    # Get original forms
    all_forms = get_all_word_forms()
    
    # Get expanded vocabulary
    expanded_words = get_expanded_words()
    
    # Combine both
    all_words = set(list(all_forms) + list(expanded_words))
    
    partial_lower = partial_word.lower()
    
    # Exact prefix matches from both sources
    suggestions = [word for word in all_words if word.lower().startswith(partial_lower)]
    
    # If not enough, add fuzzy matches
    if len(suggestions) < max_suggestions:
        fuzzy = []
        for word in all_words:
            if word.lower() not in [s.lower() for s in suggestions]:
                distance = levenshtein_distance(partial_lower, word.lower()[:len(partial_lower)])
                if distance <= 2:
                    fuzzy.append((word, distance))
        
        fuzzy.sort(key=lambda x: x[1])
        suggestions.extend([word for word, _ in fuzzy[:max_suggestions - len(suggestions)]])
    
    return sorted(suggestions[:max_suggestions])


def check_word_exists(word):
    """Check if word exists in original vocabulary or expanded vocabulary."""
    # Check original forms
    all_forms = get_all_word_forms()
    if word.lower() in [w.lower() for w in all_forms]:
        return True
    
    # Check expanded vocabulary
    expanded_words = get_expanded_words()
    return word.lower() in [w.lower() for w in expanded_words]


def analyze_sentence_structure(words):
    """Analyze SVO sentence structure."""
    if len(words) < 3:
        return False, ["Zdanie musi mieć co najmniej 3 słowa (Podmiot Czasownik Dopełnienie)"], []
    
    errors = []
    suggestions = []
    word_info = []
    
    for i, word in enumerate(words):
        word_type = classify_word(word)
        word_info.append({
            'word': word,
            'position': i,
            'type': word_type,
            'exists': check_word_exists(word)
        })
        
        if not word_info[-1]['exists']:
            closest, dist = find_closest_word(word)
            if closest:
                errors.append(f"Słowo '{word}' nie istnieje")
                suggestions.append(f"Czy chodziło o: {closest}?")
            else:
                errors.append(f"Nieznane słowo: '{word}'")
    
    has_verb = any(info['type'] == 'verb' for info in word_info)
    
    if not has_verb:
        errors.append("Brak czasownika w zdaniu")
    
    return len(errors) == 0, errors, suggestions


def classify_word(word):
    """Classify word type."""
    word_lower = word.lower()
    
    # Check verbs
    for verb_data in VERBS.values():
        if word_lower in [v.lower() for v in verb_data.values() if isinstance(v, str)]:
            return 'verb'
    
    # Check nouns
    for noun, noun_data in NOUNS.items():
        for case_forms in noun_data.values():
            if isinstance(case_forms, dict):
                if word_lower in [v.lower() for v in case_forms.values()]:
                    return 'noun'
    
    # Check adjectives
    for adj_data in ADJECTIVES.values():
        for case_forms in adj_data.values():
            if isinstance(case_forms, dict):
                if word_lower in [v.lower() for v in case_forms.values()]:
                    return 'adjective'
    
    # Check in expanded vocabulary
    if check_word_exists(word):
        return 'word'  # Generic word from expanded vocabulary
    
    return 'unknown'


def validate_declension(sentence):
    """Validate declension in sentence."""
    words = sentence.split()
    errors = []
    
    for i, word in enumerate(words):
        if not check_word_exists(word):
            closest, dist = find_closest_word(word)
            if closest and dist is not None:
                word_type = classify_word(closest)
                if word_type in ['noun', 'adjective']:
                    errors.append({
                        'word': word,
                        'position': i,
                        'type': 'declension',
                        'suggestion': closest
                    })
                else:
                    errors.append({
                        'word': word,
                        'position': i,
                        'type': 'unknown',
                        'suggestion': closest
                    })
            else:
                errors.append({
                    'word': word,
                    'position': i,
                    'type': 'not_found',
                    'suggestion': None
                })
    
    return errors


def get_sentence_feedback(sentence, hint_mode=True):
    """Get feedback for sentence with expanded vocabulary support."""
    if not sentence.strip():
        return {
            'valid': False,
            'message': 'Wprowadź zdanie',
            'errors': [],
            'suggestions': []
        }
    
    words = sentence.strip().split()
    
    if hint_mode:
        last_word = words[-1] if words else ''
        suggestions = get_autocomplete_suggestions(last_word)
        
        return {
            'valid': None,
            'message': 'Podpowiedzi słów',
            'errors': [],
            'suggestions': suggestions
        }
    else:
        errors = validate_declension(sentence)
        is_valid, struct_errors, struct_suggestions = analyze_sentence_structure(words)
        
        return {
            'valid': is_valid and len(errors) == 0,
            'message': 'Poprawne!' if (is_valid and len(errors) == 0) else 'Znaleziono błędy',
            'errors': errors,
            'structure_errors': struct_errors,
            'suggestions': struct_suggestions
        }
