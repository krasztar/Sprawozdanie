 import sqlite3
import pandas as pd
import json
import random
from datetime import datetime, timedelta

class SklepWedkarskiSQLite:
    def __init__(self):
        self.conn = None
        self.setup_connection()

    def setup_connection(self):
        """
        Ustanawia połączenie z bazą danych SQLite.
        Tworzy plik bazy danych 'sklepWedkarski.db' jeśli nie istnieje.
        """
        try:
            self.conn = sqlite3.connect('sklepWedkarski.db')
            self.conn.row_factory = sqlite3.Row # Pozwala na dostęp do kolumn po nazwie
        except sqlite3.Error as e:
            print(f"Błąd połączenia z SQLite: {e}")
            self.conn = None

    def create_tables(self):
        """
        Tworzy tabele w bazie danych SQLite, jeśli jeszcze nie istnieją.
        Definiuje schematy dla kategorii, produktów, klientów, zamówień i płatności.
        Tabela 'pozycje_zamowienia' została usunięta zgodnie z prośbą.
        """
        try:
            with self.conn:
                # Tabele istniejące
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS kategorie (
                        id INTEGER PRIMARY KEY,
                        nazwa TEXT NOT NULL,
                        opis TEXT
                    )
                ''')

                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS produkty (
                        id INTEGER PRIMARY KEY,
                        nazwa TEXT NOT NULL,
                        opis TEXT,
                        cena REAL NOT NULL,
                        stan_magazynowy INTEGER NOT NULL,
                        kategoria_id INTEGER,
                        FOREIGN KEY (kategoria_id) REFERENCES kategorie(id)
                    )
                ''')

                # Nowe tabele
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS klienci (
                        id INTEGER PRIMARY KEY,
                        imie TEXT NOT NULL,
                        nazwisko TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        telefon TEXT,
                        adres TEXT
                    )
                ''')

                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS zamowienia (
                        id INTEGER PRIMARY KEY,
                        klient_id INTEGER,
                        data_zamowienia DATE NOT NULL,
                        status TEXT CHECK(status IN ('nowe', 'w_realizacji', 'zrealizowane')),
                        FOREIGN KEY (klient_id) REFERENCES klienci(id)
                    )
                ''')

                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS platnosci (
                        id INTEGER PRIMARY KEY,
                        zamowienie_id INTEGER,
                        kwota REAL NOT NULL,
                        metoda_platnosci TEXT NOT NULL,
                        data_platnosci DATE NOT NULL,
                        FOREIGN KEY (zamowienie_id) REFERENCES zamowienia(id)
                    )
                ''')

                # Tabela 'pozycje_zamowienia' została usunięta
                # self.conn.execute('''
                #     CREATE TABLE IF NOT EXISTS pozycje_zamowienia (
                #         id INTEGER PRIMARY KEY,
                #         zamowienie_id INTEGER,
                #         produkt_id INTEGER,
                #         ilosc INTEGER NOT NULL,
                #         cena REAL NOT NULL,
                #         FOREIGN KEY (zamowienie_id) REFERENCES zamowienia(id),
                #         FOREIGN KEY (produkt_id) REFERENCES produkty(id)
                #     )
                # ''')
        except sqlite3.Error as e:
            print(f"Błąd tworzenia tabel SQLite: {e}")
            if self.conn:
                self.conn.rollback() # Wycofanie zmian w przypadku błędu

    def generate_test_data(self):
        """
        Generuje przykładowe dane dla kategorii, produktów i klientów.
        Zwiększono liczbę klientów, produktów i zamówień.
        """
        # Kategorie
        kategorie_data = [
            ("Wędki", "Wędki wędkarskie"),
            ("Przynęty", "Przynęty i zanęty"),
            ("Akcesoria", "Akcesoria wędkarskie"),
            ("Odzież", "Odzież wędkarska i obuwie"),
            ("Elektronika", "Echosondy i GPS")
        ]
        
        # Produkty (więcej produktów z opisami)
        produkty = [
            {"nazwa": "Wędka muchowa Master", "opis": "Profesjonalna wędka do muchowania", "cena": 299.99, "stan_magazynowy": 15, "kategoria_id": 1},
            {"nazwa": "Kołowrotek spinningowy", "opis": "Kołowrotek do spinningu", "cena": 149.90, "stan_magazynowy": 20, "kategoria_id": 1},
            {"nazwa": "Mocny sznurek wędkarski", "opis": "Nieprzemakalny sznurek wędkarski", "cena": 29.99, "stan_magazynowy": 30, "kategoria_id": 3},
            {"nazwa": "Żyłka fluorowa", "opis": "Żyłka fluorowa o wysokiej jakości", "cena": 39.99, "stan_magazynowy": 25, "kategoria_id": 3},
            {"nazwa": "Mucha dry", "opis": "Ręcznie wykonana mucha dry", "cena": 14.99, "stan_magazynowy": 40, "kategoria_id": 2},
            {"nazwa": "Woblery zestaw", "opis": "Zestaw woblerów na drapieżniki", "cena": 79.99, "stan_magazynowy": 50, "kategoria_id": 2},
            {"nazwa": "Podbierak teleskopowy", "opis": "Lekki podbierak z długą rączką", "cena": 89.00, "stan_magazynowy": 10, "kategoria_id": 3},
            {"nazwa": "Kurtka przeciwdeszczowa", "opis": "Wodoodporna kurtka dla wędkarzy", "cena": 199.00, "stan_magazynowy": 12, "kategoria_id": 4},
            {"nazwa": "Echosonda Deeper", "opis": "Inteligentna echosonda do smartfona", "cena": 499.00, "stan_magazynowy": 5, "kategoria_id": 5},
            {"nazwa": "Plecak wędkarski", "opis": "Pojemny plecak na akcesoria", "cena": 120.00, "stan_magazynowy": 18, "kategoria_id": 3}
        ]

        # Klienci (więcej klientów)
        klienci = [
            {"imie": "Jan", "nazwisko": "Kowalski", "email": "jan.kowalski@email.pl", "telefon": "123456789", "adres": "ul. Gdańska 1"},
            {"imie": "Anna", "nazwisko": "Wiśniewska", "email": "anna.wisniewska@email.pl", "telefon": "987654321", "adres": "ul. Krakowska 2"},
            {"imie": "Piotr", "nazwisko": "Nowak", "email": "piotr.nowak@email.pl", "telefon": "555666777", "adres": "ul. Warszawska 3"},
            {"imie": "Maria", "nazwisko": "Zając", "email": "maria.zajac@email.pl", "telefon": "111222333", "adres": "ul. Poznańska 4"},
            {"imie": "Krzysztof", "nazwisko": "Lewandowski", "email": "krzysztof.l@email.pl", "telefon": "444555666", "adres": "ul. Wrocławska 5"}
        ]

        return kategorie_data, produkty, klienci

    def export_to_json(self, kategorie, produkty, klienci):
        """
        Eksportuje wygenerowane dane do pliku JSON.
        """
        kategorie_json = [{'id': i+1, 'nazwa': k[0], 'opis': k[1]} for i, k in enumerate(kategorie)]
        produkty_json = [{'id': i+1, **p} for i, p in enumerate(produkty)]
        klienci_json = [{'id': i+1, **k} for i, k in enumerate(klienci)]

        data = {
            'kategorie': kategorie_json,
            'produkty': produkty_json,
            'klienci': klienci_json
        }

        with open('dane_testowe.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def import_from_json(self, filename):
        """
        Importuje dane z pliku JSON do bazy danych SQLite.
        Usuwa istniejące dane przed wstawieniem nowych.
        Operacje na 'pozycje_zamowienia' zostały usunięte.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Wstawianie danych
            with self.conn:
                # Usuwanie wszystkich istniejących danych (ważne dla czystego importu)
                # self.conn.execute('DELETE FROM pozycje_zamowienia') # Usunięto
                self.conn.execute('DELETE FROM platnosci')
                self.conn.execute('DELETE FROM zamowienia')
                self.conn.execute('DELETE FROM produkty')
                self.conn.execute('DELETE FROM klienci')
                self.conn.execute('DELETE FROM kategorie')

                # Kategorie
                kategorie_sqlite = [(k['id'], k['nazwa'], k['opis']) for k in data['kategorie']]
                self.conn.executemany('INSERT OR REPLACE INTO kategorie (id, nazwa, opis) VALUES (?, ?, ?)', kategorie_sqlite)

                # Produkty
                produkty_sqlite = [(p['id'], p['nazwa'], p['opis'], p['cena'], p['stan_magazynowy'], p['kategoria_id']) 
                                   for p in data['produkty']] # Usunięto ograniczenie do 5 produktów
                self.conn.executemany('INSERT OR REPLACE INTO produkty (id, nazwa, opis, cena, stan_magazynowy, kategoria_id) VALUES (?, ?, ?, ?, ?, ?)', produkty_sqlite)

                # Klienci
                klienci_sqlite = [(k['id'], k['imie'], k['nazwisko'], k['email'], k['telefon'], k['adres']) 
                                  for k in data['klienci']]
                self.conn.executemany('INSERT OR REPLACE INTO klienci (id, imie, nazwisko, email, telefon, adres) VALUES (?, ?, ?, ?, ?, ?)', klienci_sqlite)

                # Dodanie nowych zamówień i płatności (dla wszystkich klientów, więcej zamówień)
                for klient_id in range(1, len(data['klienci']) + 1): # Dla wszystkich klientów
                    num_orders = random.randint(3, 5) # Więcej zamówień na klienta
                    for _ in range(num_orders):
                        zamowienie_id = self.conn.execute('''
                            INSERT INTO zamowienia (klient_id, data_zamowienia, status)
                            VALUES (?, ?, ?)
                        ''', (klient_id, datetime.now().date().isoformat(), 'nowe')).lastrowid # Zmiana na .isoformat()
                        
                        # Płatność
                        self.conn.execute('''
                            INSERT INTO platnosci (zamowienie_id, kwota, metoda_platnosci, data_platnosci)
                            VALUES (?, ?, ?, ?)
                        ''', (zamowienie_id, random.uniform(50.0, 500.0), random.choice(['przelew', 'karta', 'gotowka']), datetime.now().date().isoformat())) # Zmiana na .isoformat()
                self.conn.commit() # Zatwierdzenie wszystkich zmian
        except sqlite3.Error as e:
            print(f"Błąd SQLite podczas importu JSON: {e}")
            if self.conn:
                self.conn.rollback() # Wycofanie zmian w przypadku błędu
        except Exception as e:
            print(f"Ogólny błąd podczas importu JSON: {e}")

    def print_all_tables(self):
        """
        Wyświetla zawartość wszystkich tabel w bazie danych.
        """
        try:
            print("\n=== Zawartość tabel SQLite ===")
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table_name in tables:
                    table = table_name[0]
                    # Pomiń tabelę 'pozycje_zamowienia' jeśli istnieje, zgodnie z prośbą
                    if table == 'pozycje_zamowienia':
                        continue

                    print(f"\nTabela: {table}")
                    print("-" * 50)
                    
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    print(" | ".join(columns))
                    print("-" * 50)
                    
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    for row in rows:
                        print(" | ".join(str(value) for value in row))
                    
                    print("-" * 50)
        except sqlite3.Error as e:
            print(f"Błąd SQLite podczas wyświetlania tabel: {e}")

    def close_connection(self):
        """
        Zamyka połączenie z bazą danych SQLite.
        """
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Błąd zamykania połączenia SQLite: {e}")

if __name__ == "__main__":
    sklep = SklepWedkarskiSQLite()
    
    # Tworzenie tabel
    print("Tworzenie tabel...")
    sklep.create_tables()
    
    # Generowanie i eksport danych
    print("Generowanie i eksport danych...")
    kategorie, produkty, klienci = sklep.generate_test_data()
    sklep.export_to_json(kategorie, produkty, klienci)
    
    # Import danych
    print("Importowanie danych...")
    sklep.import_from_json('dane_testowe.json')
    
    # Wyświetl zawartość tabel
    print("Wyświetlam zawartość tabel...")
    sklep.print_all_tables()
    
    # Zamknij połączenie
    sklep.close_connection()
    print("Zakończono pracę z bazą danych SQLite.")

