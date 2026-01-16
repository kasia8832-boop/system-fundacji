import sqlite3
import os
from werkzeug.security import generate_password_hash # Potrzebne do haszowania hasła admina

# Nazwa pliku bazy danych
db_file = 'fundacja.db'

# ==============================================================================
# 1. PRZYGOTOWANIE TERENU (CZYSTY START)
# ==============================================================================
# Sprawdzamy, czy plik bazy już istnieje. Jeśli tak - usuwamy go.
# Pozwala to na uniknięcie konfliktów przy zmianie struktury tabel.
# UWAGA: To kasuje wszystkie dane! Używać tylko w fazie developmentu.
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"⚠️ Usunięto starą wersję pliku: {db_file}")

print("🔨 Tworzę nową, pustą strukturę bazy danych...")

# Nawiązanie połączenia z bazą (plik utworzy się automatycznie)
conn = sqlite3.connect(db_file)
c = conn.cursor()

# Włączamy obsługę kluczy obcych (Foreign Keys), aby baza pilnowała relacji
# np. nie pozwoliła usunąć zwierzęcia, jeśli ma historię leczenia
c.execute("PRAGMA foreign_keys = ON;")

# ==============================================================================
# 2. TWORZENIE TABEL SŁOWNIKOWYCH
# ==============================================================================
# Słowniki trzymamy w osobnych tabelach, aby Admin mógł je edytować z poziomu aplikacji.
# Dzięki temu nie musimy zmieniać kodu Python, gdy dojdzie nowy gatunek.

print("   -> Tworzenie słowników...")

# Tabela dla gatunków (Pies, Kot...)
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_GATUNEK (Wartosc TEXT PRIMARY KEY)''')

# Tabela dla statusów (Do adopcji, W trakcie leczenia...)
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_STATUS (Wartosc TEXT PRIMARY KEY)''')

# Tabela dla źródeł finansowania (Skąd mamy zwierzę/pieniądze)
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_ZRODLO (Wartosc TEXT PRIMARY KEY)''')

# Tabela dla kategorii zdarzeń na osi czasu (Weterynarz, Behawiorysta...)
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_KATEGORIA (Wartosc TEXT PRIMARY KEY)''')

# ==============================================================================
# 3. WYPEŁNIANIE SŁOWNIKÓW (WARTOŚCI STARTOWE)
# ==============================================================================
# Wstawiamy dane ustalone w wymaganiach projektu.
# Używamy "INSERT OR IGNORE", aby nie wywołać błędu, jeśli wartość już istnieje.

print("   -> Wypełnianie słowników danymi...")

# Gatunki: tylko Pies i Kot (zgodnie z wytycznymi)
c.executemany("INSERT OR IGNORE INTO SLOWNIK_GATUNEK VALUES (?)", 
              [('Pies',), ('Kot',)])

# Statusy: kluczowe dla logiki przycisków (np. przycisk 'Adoptuj' pojawia się tylko dla 'Do adopcji')
c.executemany("INSERT OR IGNORE INTO SLOWNIK_STATUS VALUES (?)", 
              [('Do adopcji',), ('Adoptowany',), ('Dom Tymczasowy',), ('Za Tęczowym Mostem',), ('Kwarantanna',)])

# Kategorie: co może się wydarzyć w życiu zwierzęcia
c.executemany("INSERT OR IGNORE INTO SLOWNIK_KATEGORIA VALUES (?)", 
              [('Weterynarz',), ('Adopcja',), ('Inne',), ('Bytowe',)])

# Źródła: skąd pochodzi zwierzę
c.executemany("INSERT OR IGNORE INTO SLOWNIK_ZRODLO VALUES (?)", 
              [('Fundacja',), ('Schronisko',), ('Dom tymczasowy',), ('Osoba z zewnątrz',)])

# ==============================================================================
# 4. TWORZENIE TABEL GŁÓWNYCH
# ==============================================================================
print("   -> Tworzenie tabel głównych...")

# 1. SYSTEM_USER_APP: Użytkownicy, którzy logują się do systemu (Admin, Wolontariusze)
c.execute('''CREATE TABLE IF NOT EXISTS SYSTEM_USER_APP (
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    Imie TEXT, 
    Nazwisko TEXT, 
    Email TEXT UNIQUE NOT NULL,       
    PasswordHash TEXT NOT NULL,       
    Role TEXT DEFAULT 'Wolontariusz', 
    IsActive INTEGER DEFAULT 1,       
    ResetToken TEXT DEFAULT NULL,    -- <--- NOWE POLE: Tutaj trafi kod resetujący
    DataUtworzenia DATE DEFAULT CURRENT_DATE
)''')

# 2. OSOBA: Baza kontaktów (Domy Tymczasowe, Adoptujący)
# Rozdzielamy to od użytkowników systemu, bo adoptujący nie loguje się do apki.
c.execute('''CREATE TABLE IF NOT EXISTS OSOBA (
    ID_Osoba INTEGER PRIMARY KEY AUTOINCREMENT, 
    Imie TEXT NOT NULL, 
    Nazwisko TEXT NOT NULL, 
    Telefon TEXT, 
    Email TEXT, 
    AdresMiasto TEXT, 
    AdresUlica TEXT, 
    CzyJestDT INTEGER DEFAULT 0       -- Flaga: 1 jeśli ta osoba jest Domem Tymczasowym
)''')

# 3. ZWIERZE: Centralna tabela systemu
c.execute('''CREATE TABLE IF NOT EXISTS ZWIERZE (
    ID_Zwierze INTEGER PRIMARY KEY AUTOINCREMENT, 
    Imie TEXT NOT NULL, 
    Gatunek TEXT,                     -- Powiązane logicznie ze SLOWNIK_GATUNEK
    Plec TEXT,                        -- Wartości: 'M' lub 'K'
    NrChip TEXT, 
    DataUrodzenia DATE, 
    StatusZwierzecia TEXT,            -- Powiązane ze SLOWNIK_STATUS
    ZrodloFinansowania TEXT,          -- Powiązane ze SLOWNIK_ZRODLO
    CzyOgloszenieOLX INTEGER DEFAULT 0, 
    CzyOgloszenieWWW INTEGER DEFAULT 0, 
    ID_OpiekunTymczasowy INTEGER,     -- Klucz obcy do OSOBA (kto się opiekuje?)
    ID_Adoptujacy INTEGER,            -- Klucz obcy do OSOBA (kto adoptował?)
    DataAdopcji DATE, 
    ZdjecieProfilowe TEXT,            -- Przechowujemy URL lub ścieżkę do pliku
    YouTubeURL TEXT,
    
    -- Definicja relacji (klucze obce)
    FOREIGN KEY(ID_OpiekunTymczasowy) REFERENCES OSOBA(ID_Osoba),
    FOREIGN KEY(ID_Adoptujacy) REFERENCES OSOBA(ID_Osoba)
)''')

# 4. PROFIL_MEDYCZNY: Szczegóły zdrowotne (Relacja 1:1 ze Zwierzęciem)
# Trzymamy to osobno, żeby nie zaśmiecać głównej tabeli ZWIERZE.
c.execute('''CREATE TABLE IF NOT EXISTS PROFIL_MEDYCZNY (
    ID_Zwierze INTEGER PRIMARY KEY,   -- ID_Zwierze jest jednocześnie kluczem głównym tej tabeli (Relacja 1:1)
    CzyKastrowany INTEGER DEFAULT 0, 
    DataKastracji DATE, 
    SzczepienieWscieklizna DATE, 
    SzczepienieZakazne DATE, 
    Odrobaczenie DATE, 
    UwagiMedyczne TEXT,
    FOREIGN KEY(ID_Zwierze) REFERENCES ZWIERZE(ID_Zwierze)
)''')

# 5. HISTORIA_ZDARZEN: Oś czasu (Logi)
# Zmieniono nazwę z OS_CZASU_ZDARZENIE na HISTORIA_ZDARZEN dla zgodności z crud.py
c.execute('''CREATE TABLE IF NOT EXISTS HISTORIA_ZDARZEN (
    ID_Historia INTEGER PRIMARY KEY AUTOINCREMENT, 
    ID_Zwierze INTEGER NOT NULL, 
    ID_Osoba INTEGER,                 -- Kto dodał wpis (powiązanie z OSOBA)
    DataZdarzenia DATE, 
    Kategoria TEXT,                   -- Ze słownika SLOWNIK_KATEGORIA
    Opis TEXT,
    FOREIGN KEY(ID_Zwierze) REFERENCES ZWIERZE(ID_Zwierze),
    FOREIGN KEY(ID_Osoba) REFERENCES OSOBA(ID_Osoba)
)''')

# 6. ZALACZNIKI: Pliki (PDF, JPG) podpinane pod historię
# Przechowujemy pliki binarnie (BLOB) bezpośrednio w bazie SQLite.
c.execute('''CREATE TABLE IF NOT EXISTS ZALACZNIKI (
    ID_Zalacznik INTEGER PRIMARY KEY AUTOINCREMENT, 
    ID_Historia INTEGER NOT NULL,     -- Podpięcie pod konkretne zdarzenie
    NazwaPliku TEXT, 
    TypPliku TEXT,                    -- np. 'application/pdf'
    DaneBLOB BLOB,                    -- Binary Large Object (sam plik)
    DataDodania DATE,
    FOREIGN KEY(ID_Historia) REFERENCES HISTORIA_ZDARZEN(ID_Historia)
)''')

# 7. ZWIERZE_GALERIA: Dodatkowe zdjęcia (poza profilowym)
c.execute('''CREATE TABLE IF NOT EXISTS ZWIERZE_GALERIA (
    ID_Zdjecie INTEGER PRIMARY KEY AUTOINCREMENT, 
    ID_Zwierze INTEGER NOT NULL, 
    ZdjecieURL TEXT, 
    Opis TEXT, 
    FOREIGN KEY(ID_Zwierze) REFERENCES ZWIERZE(ID_Zwierze)
)''')

# ==============================================================================
# 5. TWORZENIE KONTA ADMINISTRATORA
# ==============================================================================
print("   -> Tworzenie konta Administratora...")

# Generujemy bezpieczny hash hasła 'admin123'. 
# Nigdy nie wpisujemy hasła na sztywno w INSERT w czystym tekście!
admin_password_hash = generate_password_hash("admin123")

# Rola musi być "Administrator" (wielką literą), bo tak sprawdza to kod w app.py
c.execute('''
    INSERT INTO SYSTEM_USER_APP (Imie, Nazwisko, Email, PasswordHash, Role) 
    VALUES (?, ?, ?, ?, ?)
''', ('Admin', 'Systemowy', 'admin@fundacja.pl', admin_password_hash, 'Administrator'))

# Zatwierdzenie zmian (commit) i zamknięcie połączenia
conn.commit()
conn.close()

print("\n✅ SUKCES! Baza danych 'fundacja.db' została utworzona od nowa.")
print("   -> Login: admin@fundacja.pl")
print("   -> Hasło: admin123")
print("   -> Możesz uruchomić aplikację komendą: streamlit run app.py")