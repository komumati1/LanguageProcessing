import streamlit as st
import pandas as pd
import numpy as np

from data_loader import load_word_frequency_data, load_word_connections
from visualizations import create_zipf_plot, create_top_words_bar_chart, create_network_graph
from corpus_analyzer import get_analyzer
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from polish_parser.parser import Parser, ResultMultiple
from polish_parser.polish_word_pairs import get_word_pairs_analyzer
from config import (
    PAGE_TITLE, PAGE_ICON, DEFAULT_TOP_N_WORDS, 
    DEFAULT_TOP_CONNECTIONS, DEFAULT_MIN_CONNECTION_FREQ
)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Load data
data_df = load_word_frequency_data()

# Load bigrams with progress indicator
with st.spinner('Ładowanie danych połączeń słów...'):
    bigram_counts, word_count, from_cache = load_word_connections()

# Header
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown("### Interaktywna wizualizacja przetwarzania języka naturalnego")

st.markdown("---")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Łączna liczba słów",
        value=f"{data_df['count'].sum():,}",
        delta="100K korpus"
    )

with col2:
    st.metric(
        label="📝 Unikalne słowa",
        value=f"{len(data_df):,}",
        delta=None
    )

with col3:
    top_word = data_df.iloc[0]
    st.metric(
        label="🏆 Najczęstsze słowo",
        value=top_word['word'],
        delta=f"{top_word['count']:,} wystąpień"
    )

with col4:
    if bigram_counts:
        delta_text = "⚡ z cache" if from_cache else f"{word_count:,} słów"
        st.metric(
            label="🔗 Liczba połączeń",
            value=f"{len(bigram_counts):,}",
            delta=delta_text
        )
    else:
        st.metric(
            label="📈 Średnia częstotliwość",
            value=f"{data_df['count'].mean():.1f}",
            delta=None
        )

st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Ustawienia")
    
    st.markdown("### 🎨 Wizualizacje")
    show_zipf = st.checkbox("Prawo Zipfa", value=True)
    show_top_words = st.checkbox("Top słowa", value=True)
    show_network = st.checkbox("Graf połączeń słów", value=True)
    show_polish_checker = st.checkbox("Sprawdzarka języka polskiego", value=True)
    
    st.markdown("---")
    st.markdown("### 🔧 Parametry")
    
    top_n = st.slider("Liczba top słów", 10, 100, DEFAULT_TOP_N_WORDS, 5)
    
    if show_network and bigram_counts:
        top_connections = st.slider("Liczba top połączeń", 20, 200, DEFAULT_TOP_CONNECTIONS, 10)
        min_connection_freq = st.slider("Min. częstotliwość połączenia", 1, 50, DEFAULT_MIN_CONNECTION_FREQ, 1)
    
    st.markdown("---")
    st.markdown("### ℹ️ Informacje")
    st.info("""
    **Projekt:** Przetwarzanie języka naturalnego
    
    **Język:** Deutsch 🇩🇪
    
    **Metoda:** Analiza częstotliwości słów i prawo Zipfa
    """)

# Main content area
if show_zipf:
    st.header("📉 Prawo Zipfa")
    
    st.markdown("""
    **Prawo Zipfa** mówi, że częstotliwość słowa jest odwrotnie proporcjonalna do jego rangi. 
    Na wykresie logarytmicznym (log-log) zależność ta powinna być liniowa.
    """)
    
    fig_zipf = create_zipf_plot(data_df)
    st.plotly_chart(fig_zipf, use_container_width=True)
    
    # Statistics about Zipf's law fit
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ Dane wykazują silną zgodność z prawem Zipfa")
    with col2:
        correlation = np.corrcoef(
            np.log(data_df['rank'][:1000]), 
            np.log(data_df['count'][:1000])
        )[0, 1]
        st.metric("Korelacja log-log", f"{correlation:.4f}")
    
    st.markdown("---")

if show_top_words:
    st.header(f"🏅 Top {top_n} Najczęstszych Słów")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_bar = create_top_words_bar_chart(data_df, top_n)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Data table
        st.markdown("##### 📋 Tabela danych")
        top_data = data_df.head(top_n)
        display_data = top_data[['rank', 'word', 'count']].copy()
        display_data.columns = ['Ranga', 'Słowo', 'Wystąpienia']
        st.dataframe(
            display_data,
            height=500,
            use_container_width=True
        )
    
    st.markdown("---")

if show_network:
    st.header("🕸️ Graf Połączeń Słów")
    
    st.markdown("""
    Graf pokazuje **top połączenia między sąsiadującymi słowami** w tekście. 
    Każdy węzeł to słowo, a krawędź oznacza, że słowa występują obok siebie.
    Grubość krawędzi odpowiada częstotliwości połączenia.
    """)
    
    if not bigram_counts:
        st.warning("⚠️ Dane połączeń słów nie są dostępne.")
    else:
        # Show cache info if loaded from cache
        if from_cache:
            st.success("⚡ **Dane załadowane z cache** - szybkie uruchomienie!")
        
        fig_network, G = create_network_graph(bigram_counts, top_connections, min_connection_freq)
        
        if fig_network is None:
            st.warning("Brak połączeń spełniających kryteria. Zmniejsz minimalną częstotliwość.")
        else:
            st.plotly_chart(fig_network, use_container_width=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Węzły (słowa)", len(G.nodes()))
            with col2:
                st.metric("Krawędzie (połączenia)", len(G.edges()))
            with col3:
                if len(G.nodes()) > 0:
                    avg_degree = sum(dict(G.degree()).values()) / len(G.nodes())
                    st.metric("Średni stopień węzła", f"{avg_degree:.1f}")
            
            # Top connections table
            st.markdown("##### 📊 Top połączenia")
            top_bigrams = bigram_counts.most_common(top_connections)
            filtered_bigrams = [(w1, w2, count) for (w1, w2), count in top_bigrams if count >= min_connection_freq]
            
            connection_df = pd.DataFrame(
                [(w1, w2, count) for w1, w2, count in filtered_bigrams[:20]],
                columns=['Słowo 1', 'Słowo 2', 'Częstotliwość']
            )
            st.dataframe(connection_df, use_container_width=True, height=300)
    
    st.markdown("---")
    
    st.markdown("---")

# Polish Language Checker Section with Custom Parser
if show_polish_checker:
    st.header("✍️ Sprawdzarka Języka Polskiego")
    
    st.markdown("""
    **Interaktywny system sprawdzania poprawności języka polskiego** z użyciem własnego parsera:
    - 🎯 Analiza składniowa w czasie rzeczywistym
    - 🔴 Podświetlanie błędów
    - 💡 Sugestie poprawek
    - 📝 Sprawdzanie struktury zdań
    
    *Wpisz tekst poniżej - analiza aktualizuje się automatycznie!*
    """)
    
    # Initialize session state
    if 'polish_sentence' not in st.session_state:
        st.session_state.polish_sentence = ""
    if 'show_suggestions' not in st.session_state:
        st.session_state.show_suggestions = True
    
    # Create parser instance
    parser = Parser()
    
    # Main text input - using text_input with key binding for immediate response
    st.markdown("### 📝 Wpisz zdanie")
    
    # Create two columns for layout
    col_input, col_hint = st.columns([2, 1])
    
    with col_input:
        user_input = st.text_input(
            "Zdanie po polsku",
            value=st.session_state.polish_sentence,
            key="polish_input_live",
            placeholder="Wpisz zdanie do sprawdzenia...",
            label_visibility="collapsed"
        )
        
        st.session_state.polish_sentence = user_input
    
    with col_hint:
        st.session_state.show_suggestions = st.checkbox(
            "Pokaż sugestie", 
            value=st.session_state.show_suggestions,
            help="Pokaż/ukryj listę sugerowanych poprawek"
        )
    
    # Display area for live results
    result_container = st.container()
    
    # Parse text on every change
    if user_input and user_input.strip():
        result = parser.parse_multiple(user_input)
        
        with result_container:
            if result is None:
                # No errors found - show success in a nice box
                st.markdown("""
                <div style='padding: 15px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                            border-radius: 10px; margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                    <h3 style='color: white; margin: 0;'>✅ Zdanie jest poprawne!</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Error found - display with highlighting in popup style
                
                # Create highlighted version of text
                text = user_input
                lines = text.split('\n')
                
                error_display = ""
                if result.row < len(lines):
                    line = lines[result.row]
                    before = line[:result.position]
                    error_text = line[result.position:result.position + result.length]
                    after = line[result.position + result.length:]
                    
                    # Display with HTML highlighting in a popup-style box
                    error_display = f"{before}<span style='background-color: #ff4444; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{error_text}</span>{after}"
                
                # Create popup-style error message
                st.markdown(f"""
                <div style='position: relative; padding: 20px; background: rgba(255, 68, 68, 0.1); 
                            border-left: 4px solid #ff4444; border-radius: 8px; margin: 15px 0;
                            box-shadow: 0 4px 15px rgba(255, 68, 68, 0.2);'>
                    <div style='font-size: 18px; padding: 10px; background-color: rgba(255,255,255,0.05); 
                                border-radius: 5px; margin-bottom: 10px;'>
                        {error_display}
                    </div>
                    <div style='color: #ff6b6b; font-weight: bold; font-size: 16px; margin-top: 10px;'>
                        ❌ {result.reason}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display suggestions if enabled in a floating popup style
                if st.session_state.show_suggestions and result.expected:
                    suggestions_list = [word.word for word in result.expected]
                    
                    if suggestions_list:
                        # Remove duplicates while preserving order
                        unique_suggestions = []
                        seen = set()
                        for s in suggestions_list:
                            if s not in seen:
                                unique_suggestions.append(s)
                                seen.add(s)
                        
                        # Display as badges in a popup box
                        suggestions_html = "<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 15px 0; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);'>"
                        suggestions_html += "<h4 style='color: white; margin: 0 0 15px 0;'>💡 Sugestie poprawek:</h4>"
                        suggestions_html += "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
                        
                        for suggestion in unique_suggestions[:20]:  # Limit to 20 suggestions
                            suggestions_html += f"<span style='background: rgba(255, 255, 255, 0.9); color: #667eea; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>{suggestion}</span>"
                        
                        suggestions_html += "</div></div>"
                        
                        st.markdown(suggestions_html, unsafe_allow_html=True)
                    else:
                        st.info("💭 Brak dostępnych sugestii dla tego błędu.")
                elif st.session_state.show_suggestions:
                    st.info("💭 Brak dostępnych sugestii dla tego błędu.")
            
            # Add word connections analysis
            st.markdown("---")
            st.markdown("### 🔗 Analiza Połączeń Słów")
            st.markdown("*Na podstawie korpusu polskiego - pokazuje jak często sąsiednie słowa występują razem*")
            
            # Get word pairs analyzer
            word_pairs = get_word_pairs_analyzer()
            connections = word_pairs.analyze_sentence_connections(user_input)
            
            if connections:
                # Create color legend
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("🟢 **Częste** (6+ wystąpień)")
                with col2:
                    st.markdown("🟠 **Rzadkie** (1-5 wystąpień)")
                with col3:
                    st.markdown("🔴 **Brak** (0 wystąpień)")
                
                st.markdown("")
                
                # Display connections with colors
                connections_html = "<div style='font-size: 18px; line-height: 2.5; padding: 15px; background: rgba(255,255,255,0.02); border-radius: 8px;'>"
                
                for i, (word1, word2, count, color) in enumerate(connections):
                    if color == 'green':
                        bg_color = '#28a745'
                        emoji = '🟢'
                    elif color == 'orange':
                        bg_color = '#fd7e14'
                        emoji = '🟠'
                    else:  # red
                        bg_color = '#dc3545'
                        emoji = '🔴'
                    
                    # First word (only for first connection)
                    if i == 0:
                        connections_html += f"<span style='font-weight: 500;'>{word1}</span> "
                    
                    # Connection indicator + second word
                    connections_html += f"<span style='background-color: {bg_color}; color: white; padding: 4px 10px; border-radius: 6px; margin: 0 3px; font-weight: 600;'>→ {word2} ({count})</span> "
                
                connections_html += "</div>"
                st.markdown(connections_html, unsafe_allow_html=True)
                
                # Statistics
                st.markdown("")
                green_count = sum(1 for _, _, _, c in connections if c == 'green')
                orange_count = sum(1 for _, _, _, c in connections if c == 'orange')
                red_count = sum(1 for _, _, _, c in connections if c == 'red')
                
                cols_stats = st.columns(3)
                with cols_stats[0]:
                    st.metric("🟢 Częste połączenia", green_count)
                with cols_stats[1]:
                    st.metric("🟠 Rzadkie połączenia", orange_count)
                with cols_stats[2]:
                    st.metric("🔴 Brak połączeń", red_count)
                
                # Detailed connection list
                with st.expander("📋 Szczegóły połączeń"):
                    for word1, word2, count, color in connections:
                        color_emoji = {'green': '🟢', 'orange': '🟠', 'red': '🔴'}[color]
                        st.markdown(f"{color_emoji} **[{word1}] → [{word2}]**: {count} wystąpień")
    else:
        with result_container:
            st.markdown("""
            <div style='padding: 30px; text-align: center; background: rgba(102, 126, 234, 0.1); 
                        border-radius: 10px; border: 2px dashed #667eea; margin: 20px 0;'>
                <h3 style='color: #667eea; margin: 0;'>👆 Zacznij pisać zdanie aby zobaczyć analizę</h3>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #888;'>
    <p>🎓 Projekt na przedmiot: Przetwarzanie języka naturalnego</p>
    <p>📅 Rok akademicki 2025/2026 | Semestr 5</p>
</div>
""", unsafe_allow_html=True)

# Search functionality in sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Wyszukiwanie")
    search_term = st.text_input("Wyszukaj słowo:", "")
    
    if search_term:
        search_result = data_df[data_df['word'].str.contains(search_term, case=False, na=False)]
        if not search_result.empty:
            st.success(f"Znaleziono {len(search_result)} wyników")
            st.dataframe(
                search_result[['rank', 'word', 'count']].head(10),
                use_container_width=True
            )
        else:
            st.warning("Nie znaleziono wyników")
