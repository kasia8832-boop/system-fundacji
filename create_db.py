import sqlite3
import os

db_file = 'fundacja.db'

# Jeśli plik istnieje, usuń go, żeby stworzyć czysty na nowo
if os.path.exists(db_file):
    os.remove(db_file)
    print("Stara baza usunięta.")

print("Tworzę nową bazę...")
conn = sqlite3.connect(db_file)
c = conn.cursor()

# TWORZENIE TABEL
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_GATUNEK (Wartosc TEXT PRIMARY KEY)''')
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_STATUS (Wartosc TEXT PRIMARY KEY)''')
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_ZRODLO (Wartosc TEXT PRIMARY KEY)''')
c.execute('''CREATE TABLE IF NOT EXISTS SLOWNIK_KATEGORIA (Wartosc TEXT PRIMARY KEY)''')

# SŁOWNIKI
c.executemany("INSERT OR IGNORE INTO SLOWNIK_GATUNEK VALUES (?)", [('Pies',), ('Kot',), ('Inne',)])
c.executemany("INSERT OR IGNORE INTO SLOWNIK_STATUS VALUES (?)", [('Do adopcji',), ('Adoptowany',), ('Kwarantanna',), ('Leczenie',)])
c.executemany("INSERT OR IGNORE INTO SLOWNIK_KATEGORIA VALUES (?)", [('Wizyta',), ('Zabieg',), ('Adopcja',), ('Inne',)])
c.executemany("INSERT OR IGNORE INTO SLOWNIK_ZRODLO VALUES (?)", [('Znaleziony',), ('Oddany',), ('Interwencja',)])

# TABELE GŁÓWNE
c.execute('''CREATE TABLE IF NOT EXISTS SYSTEM_USER_APP (
    ID INTEGER PRIMARY KEY AUTOINCREMENT, Imie TEXT, Nazwisko TEXT, Email TEXT UNIQUE, 
    PasswordHash TEXT, Role TEXT DEFAULT 'Wolontariusz', IsActive INTEGER DEFAULT 1, DataUtworzenia TEXT DEFAULT (DATE('now')))''')

c.execute('''CREATE TABLE IF NOT EXISTS OSOBA (
    ID_Osoba INTEGER PRIMARY KEY AUTOINCREMENT, Imie TEXT, Nazwisko TEXT, Telefon TEXT, 
    Email TEXT, AdresMiasto TEXT, AdresUlica TEXT, CzyJestDT INTEGER DEFAULT 0)''')

c.execute('''CREATE TABLE IF NOT EXISTS ZWIERZE (
    ID_Zwierze INTEGER PRIMARY KEY AUTOINCREMENT, Imie TEXT NOT NULL, Gatunek TEXT, Plec TEXT, 
    NrChip TEXT, DataUrodzenia TEXT, StatusZwierzecia TEXT, ZrodloFinansowania TEXT, 
    CzyOgloszenieOLX INTEGER DEFAULT 0, CzyOgloszenieWWW INTEGER DEFAULT 0, 
    ID_OpiekunTymczasowy INTEGER, ID_Adoptujacy INTEGER, DataAdopcji TEXT, 
    ZdjecieProfilowe TEXT, YouTubeURL TEXT,
    FOREIGN KEY(ID_OpiekunTymczasowy) REFERENCES OSOBA(ID_Osoba),
    FOREIGN KEY(ID_Adoptujacy) REFERENCES OSOBA(ID_Osoba))''')

c.execute('''CREATE TABLE IF NOT EXISTS PROFIL_MEDYCZNY (
    ID_Profil INTEGER PRIMARY KEY AUTOINCREMENT, ID_Zwierze INTEGER UNIQUE, CzyKastrowany INTEGER DEFAULT 0, 
    DataKastracji TEXT, SzczepienieWscieklizna TEXT, SzczepienieZakazne TEXT, Odrobaczenie TEXT, UwagiMedyczne TEXT,
    FOREIGN KEY(ID_Zwierze) REFERENCES ZWIERZE(ID_Zwierze))''')

c.execute('''CREATE TABLE IF NOT EXISTS OS_CZASU_ZDARZENIE (
    ID_Zdarzenie INTEGER PRIMARY KEY AUTOINCREMENT, ID_Zwierze INTEGER, ID_Autor INTEGER, 
    DataZdarzenia TEXT, Kategoria TEXT, Opis TEXT,
    FOREIGN KEY(ID_Zwierze) REFERENCES ZWIERZE(ID_Zwierze))''')

c.execute('''CREATE TABLE IF NOT EXISTS ZWIERZE_GALERIA (
    ID_Zdjecie INTEGER PRIMARY KEY AUTOINCREMENT, ID_Zwierze INTEGER, ZdjecieURL TEXT, 
    Opis TEXT, DataDodania TEXT DEFAULT (DATE('now')),
    FOREIGN KEY(ID_Zwierze) REFERENCES ZWIERZE(ID_Zwierze))''')

conn.commit()
conn.close()
print("✅ SUKCES! Plik 'fundacja.db' został utworzony. Możesz uruchamiać aplikację.")