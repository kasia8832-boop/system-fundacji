import sqlite3
from datetime import date

DB_FILE = "fundacja.db"

def wykonaj_pelna_migracje():
    print("🚀 Rozpoczynam KOMPLETNĄ migrację bazy danych...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    try:
        # ==========================================
        # 1. TABELA UZYTKOWNIK (Dawniej SYSTEM_USER_APP)
        # ==========================================
        print("🛠️  1/5 Migracja tabeli UZYTKOWNIK...")
        c.execute("""
        CREATE TABLE IF NOT EXISTS UZYTKOWNIK_NEW (
            ID_User INTEGER PRIMARY KEY AUTOINCREMENT,
            LoginName TEXT UNIQUE NOT NULL, -- Dawniej Email (kopiujemy)
            Email TEXT NOT NULL,
            HasloHash TEXT NOT NULL,        -- Dawniej PasswordHash
            Rola TEXT NOT NULL,             -- Dawniej Role
            CzyAktywny INTEGER DEFAULT 1,   -- Dawniej IsActive
            ID_Osoba INTEGER,               -- Nowe pole (FK)
            FOREIGN KEY(ID_Osoba) REFERENCES OSOBA(ID_Osoba)
        )
        """)
        
        # Sprawdzamy czy stara tabela istnieje, żeby skopiować dane
        try:
            c.execute("SELECT count(*) FROM SYSTEM_USER_APP")
            # Kopiujemy dane: Email trafia do LoginName ORAZ Email
            c.execute("""
            INSERT INTO UZYTKOWNIK_NEW (ID_User, LoginName, Email, HasloHash, Rola, CzyAktywny)
            SELECT ID, Email, Email, PasswordHash, Role, IsActive FROM SYSTEM_USER_APP
            """)
            c.execute("DROP TABLE SYSTEM_USER_APP")
            print("    -> Przeniesiono dane użytkowników.")
        except sqlite3.OperationalError:
            print("    -> Tabela SYSTEM_USER_APP nie istnieje (pusta baza?), pomijam kopiowanie.")

        c.execute("ALTER TABLE UZYTKOWNIK_NEW RENAME TO UZYTKOWNIK")


        # ==========================================
        # 2. TABELA ZWIERZE (Zmiana struktury)
        # ==========================================
        print("🛠️  2/5 Restrukturyzacja tabeli ZWIERZE...")
        
        # Tworzymy tabelę w DOCELOWYM kształcie
        # - Dodano: DataPrzyjecia, DaneAdoptujacego (TEXT), DataAdopcji
        # - Usunięto: YouTubeURL, ID_Adoptujacy (stary klucz obcy)
        c.execute("""
        CREATE TABLE IF NOT EXISTS ZWIERZE_NEW (
            ID_Zwierze INTEGER PRIMARY KEY AUTOINCREMENT,
            Imie TEXT NOT NULL,
            Gatunek TEXT,
            Rasa TEXT,
            Plec TEXT,
            DataUrodzenia DATE,
            WiekOpisowy TEXT,
            DataPrzyjecia DATE,           -- NOWE
            StatusZwierzecia TEXT,
            NrChip TEXT,
            Opis TEXT,
            Zdjecie BLOB,
            DaneAdoptujacego TEXT,        -- NOWE (String z danymi osoby)
            DataAdopcji DATE,             -- NOWE
            ID_OpiekunTymczasowy INTEGER, -- Zostawiamy, jeśli chcesz mieć historię DT
            ZrodloFinansowania TEXT,      -- Zostawiamy (opcjonalnie)
            CzyOgloszenieOLX INTEGER,     -- Zostawiamy (opcjonalnie)
            CzyOgloszenieWWW INTEGER      -- Zostawiamy (opcjonalnie)
        )
        """)
        
        # Kopiujemy dane ze starej tabeli
        try:
            # Pobieramy kolumny, które fizycznie istnieją w starej tabeli
            c.execute("PRAGMA table_info(ZWIERZE)")
            old_cols = [row[1] for row in c.fetchall()]
            
            # Budujemy zapytanie dynamicznie, bo nie wiem czy masz wszystkie kolumny
            cols_to_copy = ['ID_Zwierze', 'Imie', 'Gatunek', 'Plec', 'NrChip', 'DataUrodzenia', 'StatusZwierzecia', 'ID_OpiekunTymczasowy']
            # Dodajemy te, które mogą istnieć
            if 'Rasa' in old_cols: cols_to_copy.append('Rasa')
            if 'WiekOpisowy' in old_cols: cols_to_copy.append('WiekOpisowy')
            if 'Opis' in old_cols: cols_to_copy.append('Opis')
            if 'Zdjecie' in old_cols: cols_to_copy.append('Zdjecie')

            cols_str = ", ".join(cols_to_copy)
            
            c.execute(f"""
            INSERT INTO ZWIERZE_NEW ({cols_str})
            SELECT {cols_str} FROM ZWIERZE
            """)
            
            # Ustawiamy domyślną datę przyjęcia na dziś dla starych rekordów
            today = date.today().strftime("%Y-%m-%d")
            c.execute(f"UPDATE ZWIERZE_NEW SET DataPrzyjecia = '{today}' WHERE DataPrzyjecia IS NULL")
            
            c.execute("DROP TABLE ZWIERZE")
            print("    -> Przebudowano tabelę zwierząt.")
        except sqlite3.OperationalError:
             print("    -> Tabela ZWIERZE nie istnieje, tworzę nową pustą.")

        c.execute("ALTER TABLE ZWIERZE_NEW RENAME TO ZWIERZE")


        # ==========================================
        # 3. TABELA OSOBA (Dodatki)
        # ==========================================
        print("🛠️  3/5 Aktualizacja tabeli OSOBA...")
        try:
            c.execute("ALTER TABLE OSOBA ADD COLUMN DataRejestracji DATE")
        except sqlite3.OperationalError:
            pass # Kolumna już istnieje


        # ==========================================
        # 4. PROFIL MEDYCZNY (Kleszcze)
        # ==========================================
        print("🛠️  4/5 Aktualizacja PROFIL_MEDYCZNY...")
        try:
            c.execute("ALTER TABLE PROFIL_MEDYCZNY ADD COLUMN OchronaKleszczeDo DATE")
        except sqlite3.OperationalError:
            pass # Kolumna już istnieje
        
        # Zmiana nazwy kolumny UwagiMedyczne -> OpisZdrowia (SQLite nie wspiera rename column łatwo w starszych wersjach)
        # Tutaj zakładamy, że zostawiamy jak jest lub robimy to przy okazji, 
        # ale Twój nowy CRUD używa "OpisZdrowia". Żeby nie komplikować skryptu,
        # dodamy OpisZdrowia jako nową kolumnę i przepiszemy dane.
        try:
            c.execute("ALTER TABLE PROFIL_MEDYCZNY ADD COLUMN OpisZdrowia TEXT")
            c.execute("UPDATE PROFIL_MEDYCZNY SET OpisZdrowia = UwagiMedyczne")
        except sqlite3.OperationalError:
            pass


        # ==========================================
        # 5. TABELA KONFIGURACJI ALERTÓW
        # ==========================================
        print("🛠️  5/5 Tworzenie konfiguracji alertów...")
        c.execute("""
        CREATE TABLE IF NOT EXISTS KONFIGURACJA_ALERTY (
            KodPola TEXT PRIMARY KEY,
            Etykieta TEXT,
            DniWaznosci INTEGER,
            CzyAktywny INTEGER DEFAULT 1
        );
        """)

        domyslne = [
            ("SzczepienieWscieklizna", "Wścieklizna", 365, 1),
            ("SzczepienieZakazne", "Choroby Zakaźne", 365, 1),
            ("Odrobaczenie", "Odrobaczenie", 180, 1),
            ("OchronaKleszczeDo", "Ochrona p/kleszczom", 0, 1)
        ]
        c.executemany("INSERT OR REPLACE INTO KONFIGURACJA_ALERTY VALUES (?, ?, ?, ?)", domyslne)


        conn.commit()
        print("\n✅ SUKCES! Baza danych jest gotowa na wersję 2.0.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ BŁĄD KRYTYCZNY: {e}")
        print("Cofam zmiany...")
    finally:
        conn.close()

if __name__ == "__main__":
    wykonaj_pelna_migracje()