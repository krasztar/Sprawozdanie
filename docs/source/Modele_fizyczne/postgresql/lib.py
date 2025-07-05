 import psycopg
import pandas as pd
import json
import random
from datetime import datetime, timedelta

class SklepWedkarskiPostgreSQL:
    def __init__(self, creds):
        """
        Initializes the SklepWedkarskiPostgreSQL class.
        :param creds: Dictionary containing PostgreSQL database credentials.
                      Expected keys: 'db_name', 'user_name', 'password', 'host_name', 'port_number'.
        """
        self.creds = creds
        self.conn = None
        self.setup_connection()

    def setup_connection(self):
        """
        Establishes a connection to the PostgreSQL database.
        """
        try:
            self.conn = psycopg.connect(
                dbname=self.creds['db_name'],
                user=self.creds['user_name'],
                password=self.creds['password'],
                host=self.creds['host_name'],
                port=self.creds['port_number']
            )
            print("Connected to PostgreSQL database.")
        except psycopg.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            self.conn = None

    def create_tables(self):
        """
        Creates tables in the PostgreSQL database if they do not already exist.
        Uses PostgreSQL-specific data types (SERIAL, VARCHAR, DECIMAL).
        The 'pozycje_zamowienia' table has been removed.
        """
        if self.conn:
            try:
                with self.conn.cursor() as cur:
                    # KATEGORIE Table
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS kategorie (
                            id SERIAL PRIMARY KEY,
                            nazwa VARCHAR(100) NOT NULL,
                            opis TEXT
                        )
                    ''')
                    
                    # PRODUKTY Table
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS produkty (
                            id SERIAL PRIMARY KEY,
                            nazwa VARCHAR(100) NOT NULL,
                            opis TEXT,
                            cena DECIMAL(10,2) NOT NULL,
                            stan_magazynowy INTEGER NOT NULL,
                            kategoria_id INTEGER,
                            FOREIGN KEY (kategoria_id) REFERENCES kategorie(id)
                        )
                    ''')

                    # KLIENCI Table
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS klienci (
                            id SERIAL PRIMARY KEY,
                            imie VARCHAR(100) NOT NULL,
                            nazwisko VARCHAR(100) NOT NULL,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            telefon VARCHAR(20),
                            adres TEXT
                        )
                    ''')

                    # ZAMOWIENIA Table
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS zamowienia (
                            id SERIAL PRIMARY KEY,
                            klient_id INTEGER,
                            data_zamowienia DATE NOT NULL,
                            status VARCHAR(50) CHECK(status IN ('nowe', 'w_realizacji', 'zrealizowane')),
                            FOREIGN KEY (klient_id) REFERENCES klienci(id)
                        )
                    ''')

                    # PLATNOSCI Table
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS platnosci (
                            id SERIAL PRIMARY KEY,
                            zamowienie_id INTEGER,
                            kwota DECIMAL(10,2) NOT NULL,
                            metoda_platnosci VARCHAR(50) NOT NULL,
                            data_platnosci DATE NOT NULL,
                            FOREIGN KEY (zamowienie_id) REFERENCES zamowienia(id)
                        )
                    ''')
                    self.conn.commit()
                    print("Tables created successfully.")
            except psycopg.Error as e:
                print(f"Error creating PostgreSQL tables: {e}")
                if self.conn and not self.conn.closed:
                    self.conn.rollback()
        else:
            print("Skipped table creation (no database connection).")

    def generate_test_data(self):
        """
        Generates sample data for categories, products, customers, orders, and payments.
        Increased number of customers, products, and orders.
        IDs are generated sequentially to facilitate CSV export.
        """
        # Categories
        kategorie_data = [
            ("Wędki", "Wędki wędkarskie"),
            ("Przynęty", "Przynęty i zanęty"),
            ("Akcesoria", "Akcesoria wędkarskie"),
            ("Odzież", "Odzież wędkarska i obuwie"),
            ("Elektronika", "Echosondy i GPS"),
            ("Łodzie", "Łodzie i pontony wędkarskie"),
            ("Narzędzia", "Narzędzia i sprzęt do konserwacji")
        ]
        kategorie = [{'id': i + 1, 'nazwa': k[0], 'opis': k[1]} for i, k in enumerate(kategorie_data)]
        
        # Products (more products with descriptions)
        produkty_data = [
            {"nazwa": "Wędka muchowa Master", "opis": "Profesjonalna wędka do muchowania", "cena": 299.99, "stan_magazynowy": 15, "kategoria_id": 1},
            {"nazwa": "Kołowrotek spinningowy", "opis": "Kołowrotek do spinningu", "cena": 149.90, "stan_magazynowy": 20, "kategoria_id": 1},
            {"nazwa": "Mocny sznurek wędkarski", "opis": "Nieprzemakalny sznurek wędkarski", "cena": 29.99, "stan_magazynowy": 30, "kategoria_id": 3},
            {"nazwa": "Żyłka fluorowa", "opis": "Żyłka fluorowa o wysokiej jakości", "cena": 39.99, "stan_magazynowy": 25, "kategoria_id": 3},
            {"nazwa": "Mucha dry", "opis": "Ręcznie wykonana mucha dry", "cena": 14.99, "stan_magazynowy": 40, "kategoria_id": 2},
            {"nazwa": "Woblery zestaw", "opis": "Zestaw woblerów na drapieżniki", "cena": 79.99, "stan_magazynowy": 50, "kategoria_id": 2},
            {"nazwa": "Podbierak teleskopowy", "opis": "Lekki podbierak z długą rączką", "cena": 89.00, "stan_magazynowy": 10, "kategoria_id": 3},
            {"nazwa": "Kurtka przeciwdeszczowa", "opis": "Wodoodporna kurtka dla wędkarzy", "cena": 199.00, "stan_magazynowy": 12, "kategoria_id": 4},
            {"nazwa": "Echosonda Deeper", "opis": "Inteligentna echosonda do smartfona", "cena": 499.00, "stan_magazynowy": 5, "kategoria_id": 5},
            {"nazwa": "Plecak wędkarski", "opis": "Pojemny plecak na akcesoria", "cena": 120.00, "stan_magazynowy": 18, "kategoria_id": 3},
            {"nazwa": "Ponton Explorer 200", "opis": "Dwosobowy ponton z wiosłami", "cena": 750.00, "stan_magazynowy": 3, "kategoria_id": 6},
            {"nazwa": "Zestaw naprawczy wędki", "opis": "Kompletny zestaw do naprawy wędek", "cena": 45.00, "stan_magazynowy": 25, "kategoria_id": 7}
        ]
        produkty = [{'id': i + 1, **p} for i, p in enumerate(produkty_data)]

        # Customers (more customers)
        klienci_data = [
            {"imie": "Jan", "nazwisko": "Kowalski", "email": "jan.kowalski@email.pl", "telefon": "123456789", "adres": "ul. Gdańska 1"},
            {"imie": "Anna", "nazwisko": "Wiśniewska", "email": "anna.wisniewska@email.pl", "telefon": "987654321", "adres": "ul. Krakowska 2"},
            {"imie": "Piotr", "nazwisko": "Nowak", "email": "piotr.nowak@email.pl", "telefon": "555666777", "adres": "ul. Warszawska 3"},
            {"imie": "Maria", "nazwisko": "Zając", "email": "maria.zajac@email.pl", "telefon": "111222333", "adres": "ul. Poznańska 4"},
            {"imie": "Krzysztof", "nazwisko": "Lewandowski", "email": "krzysztof.l@email.pl", "telefon": "444555666", "adres": "ul. Wrocławska 5"},
            {"imie": "Ewa", "nazwisko": "Dąbrowska", "email": "ewa.d@email.pl", "telefon": "777888999", "adres": "ul. Łódzka 6"},
            {"imie": "Tomasz", "nazwisko": "Wójcik", "email": "tomasz.w@email.pl", "telefon": "222333444", "adres": "ul. Katowicka 7"}
        ]
        klienci = [{'id': i + 1, **k} for i, k in enumerate(klienci_data)]

        # Orders and Payments
        zamowienia = []
        platnosci = []
        order_id_counter = 1
        payment_id_counter = 1

        for klient in klienci:
            num_orders = random.randint(2, 4) # 2 to 4 orders per customer
            for _ in range(num_orders):
                order_date = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
                status = random.choice(['nowe', 'w_realizacji', 'zrealizowane'])
                
                zamowienia.append({
                    'id': order_id_counter,
                    'klient_id': klient['id'],
                    'data_zamowienia': order_date.isoformat(),
                    'status': status
                })

                # Generate payment for the order
                payment_amount = round(random.uniform(50.0, 1000.0), 2)
                payment_method = random.choice(['przelew', 'karta', 'gotowka'])
                payment_date = order_date + timedelta(days=random.randint(0, 7)) # Payment up to 7 days after the order
                
                platnosci.append({
                    'id': payment_id_counter,
                    'zamowienie_id': order_id_counter,
                    'kwota': payment_amount,
                    'metoda_platnosci': payment_method,
                    'data_platnosci': payment_date.isoformat()
                })
                order_id_counter += 1
                payment_id_counter += 1
        
        return kategorie, produkty, klienci, zamowienia, platnosci

    def export_data_to_csv(self, kategorie, produkty, klienci, zamowienia, platnosci):
        """
        Exports generated data to separate CSV files.
        """
        pd.DataFrame(kategorie).to_csv('kategorie.csv', index=False, header=True)
        pd.DataFrame(produkty).to_csv('produkty.csv', index=False, header=True)
        pd.DataFrame(klienci).to_csv('klienci.csv', index=False, header=True)
        pd.DataFrame(zamowienia).to_csv('zamowienia.csv', index=False, header=True)
        pd.DataFrame(platnosci).to_csv('platnosci.csv', index=False, header=True)
        print("Data exported to CSV files.")

    def import_from_csv(self):
        """
        Imports data from CSV files into the PostgreSQL database using COPY.
        Cleans tables and resets sequences beforehand.
        """
        if self.conn and not self.conn.closed:
            try:
                with self.conn.cursor() as cur:
                    # Clear tables and reset sequences
                    print("Clearing tables and resetting sequences...")
                    cur.execute("TRUNCATE TABLE platnosci RESTART IDENTITY CASCADE;")
                    cur.execute("TRUNCATE TABLE zamowienia RESTART IDENTITY CASCADE;")
                    cur.execute("TRUNCATE TABLE produkty RESTART IDENTITY CASCADE;")
                    cur.execute("TRUNCATE TABLE klienci RESTART IDENTITY CASCADE;")
                    cur.execute("TRUNCATE TABLE kategorie RESTART IDENTITY CASCADE;")
                    self.conn.commit()
                    print("Tables cleared.")

                    # Import categories
                    try:
                        print("Importing categories...")
                        with open('kategorie.csv', 'r') as f_kategorie:
                            # Use cur.copy for psycopg3 or cur.copy_from for psycopg2
                            # Assuming psycopg3, using cur.copy
                            with cur.copy("COPY kategorie (id, nazwa, opis) FROM STDIN (FORMAT CSV, HEADER TRUE)") as copy_k:
                                copy_k.write(f_kategorie.read().encode('utf-8'))
                        print(f"Imported data into 'kategorie'.")
                    except Exception as e:
                        print(f"Error during categories import: {e}")
                        raise # Re-raise to trigger rollback

                    # Import customers
                    try:
                        print("Importing customers...")
                        with open('klienci.csv', 'r') as f_klienci:
                            with cur.copy("COPY klienci (id, imie, nazwisko, email, telefon, adres) FROM STDIN (FORMAT CSV, HEADER TRUE)") as copy_kl:
                                copy_kl.write(f_klienci.read().encode('utf-8'))
                        print(f"Imported data into 'klienci'.")
                    except Exception as e:
                        print(f"Error during customers import: {e}")
                        raise

                    # Import products
                    try:
                        print("Importing products...")
                        with open('produkty.csv', 'r') as f_produkty:
                            with cur.copy("COPY produkty (id, nazwa, opis, cena, stan_magazynowy, kategoria_id) FROM STDIN (FORMAT CSV, HEADER TRUE)") as copy_p:
                                copy_p.write(f_produkty.read().encode('utf-8'))
                        print(f"Imported data into 'produkty'.")
                    except Exception as e:
                        print(f"Error during products import: {e}")
                        raise

                    # Import orders
                    try:
                        print("Importing orders...")
                        with open('zamowienia.csv', 'r') as f_zamowienia:
                            with cur.copy("COPY zamowienia (id, klient_id, data_zamowienia, status) FROM STDIN (FORMAT CSV, HEADER TRUE)") as copy_z:
                                copy_z.write(f_zamowienia.read().encode('utf-8'))
                        print(f"Imported data into 'zamowienia'.")
                    except Exception as e:
                        print(f"Error during orders import: {e}")
                        raise

                    # Import payments
                    try:
                        print("Importing payments...")
                        with open('platnosci.csv', 'r') as f_platnosci:
                            with cur.copy("COPY platnosci (id, zamowienie_id, kwota, metoda_platnosci, data_platnosci) FROM STDIN (FORMAT CSV, HEADER TRUE)") as copy_pl:
                                copy_pl.write(f_platnosci.read().encode('utf-8'))
                        print(f"Imported data into 'platnosci'.")
                    except Exception as e:
                        print(f"Error during payments import: {e}")
                        raise
                    
                    self.conn.commit()
                    print("Data imported successfully from CSV.")
            except psycopg.Error as e:
                print(f"PostgreSQL error during CSV import: {e}")
                if self.conn and not self.conn.closed:
                    self.conn.rollback()
            except FileNotFoundError as e:
                print(f"Error: CSV file not found: {e}")
                if self.conn and not self.conn.closed:
                    self.conn.rollback()
            except Exception as e: # Catch any re-raised exceptions
                print(f"General error during CSV import: {e}")
                if self.conn and not self.conn.closed:
                    self.conn.rollback()
        else:
            print("Skipped PostgreSQL import (no connection).")

    def print_all_tables(self):
        """
        Displays the content of all tables in the PostgreSQL database.
        """
        try:
            print("\n=== Content of PostgreSQL Tables ===")
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename NOT LIKE 'pg_%' AND tablename NOT LIKE 'sql_%'
                    ORDER BY tablename;
                """)
                tables = cur.fetchall()
                
                for table_name in tables:
                    table = table_name[0]
                    print(f"\nTable: {table}")
                    print("-" * 50)
                    
                    cur.execute(f"SELECT * FROM {table}")
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    print(" | ".join(columns))
                    print("-" * 50)
                    
                    for row in rows:
                        print(" | ".join(str(value) for value in row))
                    
                    print(f"\nNumber of rows in table {table}: {len(rows)}")
                    print("-" * 50)
        except psycopg.Error as e:
            print(f"PostgreSQL error when displaying tables: {e}")
        except Exception as e:
            print(f"General error when displaying tables: {e}")

    def close_connection(self):
        """
        Closes the connection to the PostgreSQL database.
        """
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
                print("Connection to PostgreSQL database closed.")
            except Exception as e:
                print(f"Error closing PostgreSQL connection: {e}")

if __name__ == "__main__":
    # Load authentication data from database_creds.json file
    # REMEMBER: This file must exist in the same location as the script
    # and contain data in JSON format, e.g.:
    # {
    #   "db_name": "your_db_name",
    #   "user_name": "your_user",
    #   "password": "your_password",
    #   "host_name": "localhost",
    #   "port_number": "5432"
    # }
    try:
        with open("database_creds.json") as db_con_file:
            creds = json.loads(db_con_file.read())
    except FileNotFoundError:
        print("Error: 'database_creds.json' file not found.")
        print("Please ensure the credentials file exists and is correctly formatted.")
        exit()
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in 'database_creds.json' file.")
        exit()
    
    sklep = SklepWedkarskiPostgreSQL(creds)
    
    # Create tables
    print("Creating tables...")
    sklep.create_tables()
    
    # Generate test data
    print("Generating test data...")
    kategorie, produkty, klienci, zamowienia, platnosci = sklep.generate_test_data()
    
    # Export data to CSV
    print("Exporting data to CSV...")
    sklep.export_data_to_csv(kategorie, produkty, klienci, zamowienia, platnosci)
    
    # Import data from CSV
    print("Importing data from CSV to PostgreSQL...")
    sklep.import_from_csv()
    
    # Display table content
    print("Displaying table content...")
    sklep.print_all_tables()
    
    # Close connection
    sklep.close_connection()
    print("Finished working with PostgreSQL database.")

