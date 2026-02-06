# 🇩🇪 Dashboard Analizy Języka Niemieckiego

Interaktywna aplikacja Streamlit do wizualizacji wyników analizy języka niemieckiego.

## 📋 Funkcje

- **Prawo Zipfa**: Interaktywny wykres log-log pokazujący rozkład częstotliwości słów
- **Top słowa**: Wizualizacja najczęstszych słów w korpusie
- **Rozkład częstotliwości**: Histogram częstotliwości występowania słów
- **Analiza gramatyczna**: Przegląd rzeczowników i czasowników (jeśli dostępne)
- **Wyszukiwanie**: Możliwość wyszukiwania konkretnych słów

## 🚀 Instalacja

1. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## ▶️ Uruchomienie

Uruchom aplikację z katalogu `dashboard`:

```bash
streamlit run app.py
```

Aplikacja otworzy się automatycznie w przeglądarce pod adresem `http://localhost:8501`

## 📊 Dane

Aplikacja automatycznie wczytuje dane z katalogu nadrzędnego:
- `data.csv` - główne dane o częstotliwości słów
- `nouns.csv` - dane o rzeczownikach (opcjonalne)
- `verbs.csv` - dane o czasownikach (opcjonalne)

## 🎨 Technologie

- **Streamlit**: Framework do tworzenia interaktywnych aplikacji
- **Plotly**: Zaawansowane wykresy interaktywne
- **Pandas**: Analiza i przetwarzanie danych
- **NumPy**: Operacje numeryczne

## 👨‍💻 Autor

Projekt na przedmiot: Przetwarzanie języka naturalnego
