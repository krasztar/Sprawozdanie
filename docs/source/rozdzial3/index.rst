Modele Bazy Danych
==================

Author: Kacper Rasztar

Wprowadzenie
------------

W tym rozdziale przedstawiono modele bazy danych zaprojektowane i zaimplementowane w dwóch środowiskach: **SQLite** oraz **PostgreSQL**. Projekt dotyczy systemu sklepu wędkarskiego i obejmuje strukturę logiczną i fizyczną bazy danych, której celem jest zarządzanie produktami, klientami, zamówieniami oraz płatnościami.

Model Konceptualny
------------------

Baza danych składa się z 5 głównych tabel:

- **klienci** – zawiera dane użytkowników sklepu,
- **produkty** – przechowuje informacje o dostępnych towarach,
- **zamówienia** – reprezentuje zakupy klientów,
- **płatności** – powiązane z zamówieniami,
- **kategorie** – grupuje produkty według typów.

Relacje:

- Jeden klient może mieć wiele zamówień (relacja jeden-do-wielu),
- Każde zamówienie ma jedną płatność (relacja jeden-do-jednego),
- Produkty należą do jednej kategorii (relacja wiele-do-jednego).

Model Logiczny
--------------

**Tabela klienci**:

- `id` – liczba całkowita, klucz główny,
- `imie` – tekst,
- `nazwisko` – tekst,
- `email` – tekst (unikalny),
- `telefon` – tekst,
- `adres` – tekst.

**Tabela produkty**:

- `id` – liczba całkowita, klucz główny,
- `nazwa` – tekst,
- `opis` – tekst,
- `cena` – liczba zmiennoprzecinkowa,
- `stan_magazynowy` – liczba całkowita,
- `kategoria_id` – liczba całkowita, klucz obcy.

**Tabela zamówienia**:

- `id` – liczba całkowita, klucz główny,
- `klient_id` – liczba całkowita, klucz obcy,
- `data_zamowienia` – data,
- `status` – tekst (np. 'nowe', 'w_realizacji', 'zrealizowane').

**Tabela płatności**:

- `id` – liczba całkowita, klucz główny,
- `zamowienie_id` – liczba całkowita, klucz obcy,
- `kwota` – liczba zmiennoprzecinkowa,
- `metoda_platnosci` – tekst,
- `data_platnosci` – data.

**Tabela kategorie**:

- `id` – liczba całkowita, klucz główny,
- `nazwa` – tekst,
- `opis` – tekst.

Model Fizyczny
--------------

**Implementacja w SQLite**:

- `TEXT` używany dla danych tekstowych (np. imie, nazwisko, email),
- `INTEGER` dla identyfikatorów i wartości liczbowych,
- `REAL` dla cen i kwot,
- `DATE` dla dat (przechowywane jako tekst w formacie ISO).

**Implementacja w PostgreSQL**:

- `VARCHAR` dla tekstów (np. VARCHAR(100) dla nazw i emaili),
- `INTEGER` dla kluczy głównych i liczbowych pól,
- `DECIMAL(10,2)` dla cen i kwot,
- `DATE` dla dat,
- `TEXT` dla dłuższych opisów i adresów.

Relacje między tabelami zostały zaimplementowane przy użyciu kluczy obcych (FOREIGN KEY) oraz ograniczeń spójności.

Podsumowanie
------------

Zaprojektowana baza danych jest znormalizowana i zapewnia integralność danych oraz możliwość łatwego rozszerzania funkcjonalności sklepu internetowego. Obsługuje zarówno zapisywanie danych testowych, jak i ich import/eksport w różnych formatach (CSV, JSON).
