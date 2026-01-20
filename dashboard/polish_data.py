"""Polish language data for the checker system."""

# Basic Polish vocabulary with declensions
# Format: {base_word: {case: {gender_number: form}}}

NOUNS = {
    # Feminine nouns
    'Ala': {
        'nominative': {'sg': 'Ala', 'pl': 'Ale'},
        'genitive': {'sg': 'Ali', 'pl': 'Al'},
        'dative': {'sg': 'Ali', 'pl': 'Alom'},
        'accusative': {'sg': 'Alę', 'pl': 'Ale'},
        'instrumental': {'sg': 'Alą', 'pl': 'Alami'},
        'locative': {'sg': 'Ali', 'pl': 'Alach'},
        'gender': 'f'
    },
    'kobieta': {
        'nominative': {'sg': 'kobieta', 'pl': 'kobiety'},
        'genitive': {'sg': 'kobiety', 'pl': 'kobiet'},
        'dative': {'sg': 'kobiecie', 'pl': 'kobietom'},
        'accusative': {'sg': 'kobietę', 'pl': 'kobiety'},
        'instrumental': {'sg': 'kobietą', 'pl': 'kobietami'},
        'locative': {'sg': 'kobiecie', 'pl': 'kobietach'},
        'gender': 'f'
    },
    # Masculine nouns
    'kot': {
        'nominative': {'sg': 'kot', 'pl': 'koty'},
        'genitive': {'sg': 'kota', 'pl': 'kotów'},
        'dative': {'sg': 'kotu', 'pl': 'kotom'},
        'accusative': {'sg': 'kota', 'pl': 'koty'},
        'instrumental': {'sg': 'kotem', 'pl': 'kotami'},
        'locative': {'sg': 'kocie', 'pl': 'kotach'},
        'gender': 'm'
    },
    'pies': {
        'nominative': {'sg': 'pies', 'pl': 'psy'},
        'genitive': {'sg': 'psa', 'pl': 'psów'},
        'dative': {'sg': 'psu', 'pl': 'psom'},
        'accusative': {'sg': 'psa', 'pl': 'psy'},
        'instrumental': {'sg': 'psem', 'pl': 'psami'},
        'locative': {'sg': 'psie', 'pl': 'psach'},
        'gender': 'm'
    },
    'dom': {
        'nominative': {'sg': 'dom', 'pl': 'domy'},
        'genitive': {'sg': 'domu', 'pl': 'domów'},
        'dative': {'sg': 'domowi', 'pl': 'domom'},
        'accusative': {'sg': 'dom', 'pl': 'domy'},
        'instrumental': {'sg': 'domem', 'pl': 'domami'},
        'locative': {'sg': 'domu', 'pl': 'domach'},
        'gender': 'm'
    },
    # Neuter nouns
    'dziecko': {
        'nominative': {'sg': 'dziecko', 'pl': 'dzieci'},
        'genitive': {'sg': 'dziecka', 'pl': 'dzieci'},
        'dative': {'sg': 'dziecku', 'pl': 'dzieciom'},
        'accusative': {'sg': 'dziecko', 'pl': 'dzieci'},
        'instrumental': {'sg': 'dzieckiem', 'pl': 'dziećmi'},
        'locative': {'sg': 'dziecku', 'pl': 'dzieciach'},
        'gender': 'n'
    }
}

# Adjectives with declensions
ADJECTIVES = {
    'duży': {
        'nominative': {'m': 'duży', 'f': 'duża', 'n': 'duże', 'pl': 'duże'},
        'genitive': {'m': 'dużego', 'f': 'dużej', 'n': 'dużego', 'pl': 'dużych'},
        'dative': {'m': 'dużemu', 'f': 'dużej', 'n': 'dużemu', 'pl': 'dużym'},
        'accusative': {'m': 'dużego', 'f': 'dużą', 'n': 'duże', 'pl': 'duże'},
        'instrumental': {'m': 'dużym', 'f': 'dużą', 'n': 'dużym', 'pl': 'dużymi'},
        'locative': {'m': 'dużym', 'f': 'dużej', 'n': 'dużym', 'pl': 'dużych'}
    },
    'mały': {
        'nominative': {'m': 'mały', 'f': 'mała', 'n': 'małe', 'pl': 'małe'},
        'genitive': {'m': 'małego', 'f': 'małej', 'n': 'małego', 'pl': 'małych'},
        'dative': {'m': 'małemu', 'f': 'małej', 'n': 'małemu', 'pl': 'małym'},
        'accusative': {'m': 'małego', 'f': 'małą', 'n': 'małe', 'pl': 'małe'},
        'instrumental': {'m': 'małym', 'f': 'małą', 'n': 'małym', 'pl': 'małymi'},
        'locative': {'m': 'małym', 'f': 'małej', 'n': 'małym', 'pl': 'małych'}
    },
    'ładny': {
        'nominative': {'m': 'ładny', 'f': 'ładna', 'n': 'ładne', 'pl': 'ładne'},
        'genitive': {'m': 'ładnego', 'f': 'ładnej', 'n': 'ładnego', 'pl': 'ładnych'},
        'dative': {'m': 'ładnemu', 'f': 'ładnej', 'n': 'ładnemu', 'pl': 'ładnym'},
        'accusative': {'m': 'ładnego', 'f': 'ładną', 'n': 'ładne', 'pl': 'ładne'},
        'instrumental': {'m': 'ładnym', 'f': 'ładną', 'n': 'ładnym', 'pl': 'ładnymi'},
        'locative': {'m': 'ładnym', 'f': 'ładnej', 'n': 'ładnym', 'pl': 'ładnych'}
    },
    'dobry': {
        'nominative': {'m': 'dobry', 'f': 'dobra', 'n': 'dobre', 'pl': 'dobre'},
        'genitive': {'m': 'dobrego', 'f': 'dobrej', 'n': 'dobrego', 'pl': 'dobrych'},
        'dative': {'m': 'dobremu', 'f': 'dobrej', 'n': 'dobremu', 'pl': 'dobrym'},
        'accusative': {'m': 'dobrego', 'f': 'dobrą', 'n': 'dobre', 'pl': 'dobre'},
        'instrumental': {'m': 'dobrym', 'f': 'dobrą', 'n': 'dobrym', 'pl': 'dobrymi'},
        'locative': {'m': 'dobrym', 'f': 'dobrej', 'n': 'dobrym', 'pl': 'dobrych'}
    }
}

# Verbs (simplified - present tense)
VERBS = {
    'mieć': {
        'ja': 'mam',
        'ty': 'masz',
        'on/ona/ono': 'ma',
        'my': 'mamy',
        'wy': 'macie',
        'oni/one': 'mają',
        'type': 'transitive'
    },
    'być': {
        'ja': 'jestem',
        'ty': 'jesteś',
        'on/ona/ono': 'jest',
        'my': 'jesteśmy',
        'wy': 'jesteście',
        'oni/one': 'są',
        'type': 'linking'
    },
    'widzieć': {
        'ja': 'widzę',
        'ty': 'widzisz',
        'on/ona/ono': 'widzi',
        'my': 'widzimy',
        'wy': 'widzicie',
        'oni/one': 'widzą',
        'type': 'transitive'
    },
    'lubić': {
        'ja': 'lubię',
        'ty': 'lubisz',
        'on/ona/ono': 'lubi',
        'my': 'lubimy',
        'wy': 'lubicie',
        'oni/one': 'lubią',
        'type': 'transitive'
    }
}

def get_all_word_forms():
    """Get all possible word forms for autocomplete."""
    all_forms = set()
    
    # Add all noun forms
    for noun_data in NOUNS.values():
        for case_forms in noun_data.values():
            if isinstance(case_forms, dict):
                all_forms.update(case_forms.values())
    
    # Add all adjective forms
    for adj_data in ADJECTIVES.values():
        for case_forms in adj_data.values():
            if isinstance(case_forms, dict):
                all_forms.update(case_forms.values())
    
    # Add all verb forms
    for verb_data in VERBS.values():
        for form in verb_data.values():
            if isinstance(form, str):
                all_forms.add(form)
    
    return sorted(all_forms)
