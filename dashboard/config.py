"""Configuration and constants for the dashboard."""

# Data processing settings
MAX_WORDS_TO_PROCESS = 100000  # Limit for bigram processing
BIGRAM_UPDATE_FREQUENCY = 5000  # Update progress every N words

# UI Settings
PAGE_TITLE = "Analiza Języka Niemieckiego"
PAGE_ICON = "🇩🇪"
DEFAULT_TOP_N_WORDS = 30
DEFAULT_TOP_CONNECTIONS = 100
DEFAULT_MIN_CONNECTION_FREQ = 10

# Color schemes
GRADIENT_COLORS = {
    'primary': ['#667eea', '#764ba2'],
    'secondary': ['#1e3a8a', '#3b82f6']
}

# Chart templates
PLOTLY_TEMPLATE = 'plotly_dark'
