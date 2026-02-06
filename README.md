# Projekt: Analiza języka naturalnego i sprawdzarka gramatyczna

## Opis projektu

Projekt dotyczy analizy języka naturalnego oraz prostych metod przetwarzania tekstu. Składa się z trzech głównych części:

1. **Analiza prawa Zipfa dla języka niemieckiego**  
   Badanie rozkładu częstości występowania słów na podstawie korpusu 100 000 słów pochodzących z niemieckiej Wikipedii, wraz z wykresem dopasowania do prawa Zipfa.

2. **Graf częstotliwości połączeń słów**  
   Wizualizacja relacji pomiędzy najczęściej występującymi po sobie słowami w analizowanym tekście, umożliwiająca identyfikację charakterystycznych fraz encyklopedycznych.

3. **Sprawdzarka języka polskiego**  
   Prosta sprawdzarka gramatyczna oparta na parserze LL(1) oraz ręcznie przygotowanej bazie słów (rzeczowniki, czasowniki, przymiotniki, przysłówki), wykrywająca podstawowe błędy fleksyjne i składniowe oraz generująca komunikaty diagnostyczne.

## Struktura projektu

Projekt składa się z kilku katalogów odpowiadających poszczególnym częściom zadania. Kluczowym elementem jest katalog `dashboard`, który zawiera aplikację uruchomieniową oraz szczegółową instrukcję startu.


> **Uwaga:**  
> Szczegóły dotyczące konfiguracji środowiska, wymaganych zależności oraz sposobu uruchomienia aplikacji znajdują się w osobnym pliku README w katalogu `dashboard`.

## Uruchomienie projektu

Aby uruchomić projekt:

1. Przejdź do katalogu `dashboard`
2. Zapoznaj się z instrukcją zawartą w pliku `dashboard/README.md`
3. Postępuj zgodnie z opisanymi tam krokami

```bash
cd dashboard
