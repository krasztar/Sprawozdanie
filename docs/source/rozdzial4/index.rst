Analiza bazy danych oraz optymalizacja zapytań
==============================================

Autor: Kacper Rasztar

Wstęp
-----

W tym rozdziale przeprowadzono analizę wydajności zapytań SQL oraz ocenę struktury bazy danych dla dwóch środowisk: SQLite oraz PostgreSQL. Analiza ta obejmuje ocenę szybkości działania zapytań, wykorzystania indeksów oraz potencjalnych możliwości optymalizacji.

Migracja danych między SQLite a PostgreSQL
------------------------------------------

Proces migracji między bazami wymaga odpowiedniego przekształcenia typów danych oraz dostosowania ograniczeń i struktur tabel.

**Z SQLite do PostgreSQL:**

- TEXT → VARCHAR, INTEGER → SERIAL, REAL → DECIMAL
- Eksport danych do plików CSV
- Import danych do PostgreSQL za pomocą `COPY` lub pgloader
- Wprowadzenie kluczy obcych i ograniczeń

**Z PostgreSQL do SQLite:**

- SERIAL → INTEGER PRIMARY KEY AUTOINCREMENT
- VARCHAR → TEXT, DECIMAL → REAL
- Eksport do CSV i import poprzez `.import`
- Upraszczanie schematu (mniej restrykcyjne klucze)

Wnioski:

- PostgreSQL zapewnia większą kontrolę nad typami i relacjami
- SQLite pozwala na szybsze prototypowanie, ale wymaga dodatkowej walidacji

Analiza zapytania SQLuser_price
-------------------------------

Poniżej zaprezentowano zapytanie SQL, które oblicza sumę zakupów dla każdego użytkownika:

.. code-block:: sql

    SELECT
        u.imie || ' ' || u.nazwisko AS nazwa_uzytkownika,
        SUM(p.cena * pz.ilosc) AS suma_zakupow
    FROM Uzytkownicy u
    JOIN Zamowienia z ON u.id_uzytkownika = z.id_uzytkownika
    JOIN PozycjeZamowienia pz ON z.id_zamowienia = pz.id_zamowienia
    JOIN Produkty p ON pz.id_produktu = p.id_produktu
    GROUP BY u.id_uzytkownika
    ORDER BY suma_zakupow DESC;

**Opis działania:**

- Łączy tabele użytkowników, zamówień, pozycji zamówień i produktów
- Wylicza sumę wydatków każdego użytkownika
- Sortuje wyniki malejąco

**Wnioski z analizy EXPLAIN ANALYZE:**

- Zapytanie może działać wolno na dużych zbiorach danych bez indeksów
- Zalecane utworzenie indeksów na kolumnach: `id_uzytkownika`, `id_zamowienia`, `id_produktu`

**Przykład indeksów (PostgreSQL):**

.. code-block:: sql

    CREATE INDEX idx_zamowienia_id_uzytkownika ON Zamowienia(id_uzytkownika);
    CREATE INDEX idx_pozycje_id_zamowienia ON PozycjeZamowienia(id_zamowienia);
    CREATE INDEX idx_pozycje_id_produktu ON PozycjeZamowienia(id_produktu);

Wydajność zapytania można porównać przy użyciu `EXPLAIN ANALYZE`:

.. code-block:: sql

    EXPLAIN ANALYZE SELECT * FROM Produkty WHERE cena > 100;

    EXPLAIN ANALYZE SELECT * FROM Produkty WHERE nazwa LIKE 'A%';

Monitorowanie i optymalizacja
------------------------------

- Regularne stosowanie `EXPLAIN` i `EXPLAIN ANALYZE` umożliwia analizę planów zapytań
- Indeksy na kolumnach wykorzystywanych w filtrach (`WHERE`, `JOIN`, `ORDER BY`) znacząco poprawiają wydajność
- W PostgreSQL zaleca się również wykonywanie `ANALYZE` i `VACUUM` w celu utrzymania aktualnych statystyk

Przykład użycia EXPLAIN:

.. code-block:: sql

    EXPLAIN SELECT * FROM Zamowienia WHERE status = 'zrealizowane';

    EXPLAIN ANALYZE SELECT * FROM PozycjeZamowienia WHERE ilosc > 10;

Podsumowanie
------------

Analiza pokazała, że baza danych może być skutecznie przenoszona pomiędzy środowiskami SQLite i PostgreSQL z zachowaniem spójności danych. Kluczowym elementem zapewnienia wydajności jest stosowanie indeksów oraz testowanie zapytań przy pomocy narzędzi takich jak `EXPLAIN`. Dobrze zaprojektowane zapytania oraz utrzymana struktura bazy danych pozwalają uniknąć opóźnień i przeciążeń w działaniu systemu sklepu internetowego.

