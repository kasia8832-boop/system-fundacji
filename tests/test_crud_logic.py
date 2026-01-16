import pytest
import os
import sqlite3
import sys
from datetime import date

# Dodajemy katalog główny do ścieżki, żeby widzieć plik crud.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import crud

# Nazwa tymczasowej bazy do testów
TEST_DB = "testowa_baza_unit.db"

@pytest.fixture(scope="module")
def setup_database():
    """
    To uruchamia się RAZ przed wszystkimi testami.
    1. Podmienia plik bazy w crud.py na testowy.
    2. Tworzy tabele.
    3. Po testach usuwa plik.
    """
    # Podmieniamy bazę na testową
    crud.DB_FILE = TEST_DB
    
    # Jeśli plik istniał po poprzednim błędzie - usuń go
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Tworzymy strukturę tabel (uproszczoną, ale zgodną z Twoim CRUD)
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()
    
    # Tabela UZYTKOWNIK
    c.execute("""
        CREATE TABLE UZYTKOWNIK (
            ID_User INTEGER PRIMARY KEY AUTOINCREMENT,
            LoginName TEXT UNIQUE,
            Email TEXT,
            HasloHash TEXT,
            Rola TEXT,
            CzyAktywny INTEGER DEFAULT 1,
            ResetToken TEXT
        )
    """)
    
    # Tabela ZWIERZE
    c.execute("""
        CREATE TABLE ZWIERZE (
            ID_Zwierze INTEGER PRIMARY KEY AUTOINCREMENT,
            Imie TEXT,
            Gatunek TEXT,
            Rasa TEXT,
            Plec TEXT,
            StatusZwierzecia TEXT,
            DataPrzyjecia DATE,
            NrChip TEXT,
            DaneAdoptujacego TEXT,
            DataAdopcji DATE,
            Zdjecie BLOB,
            DataUrodzenia DATE,
            WiekOpisowy TEXT,
            Opis TEXT
        )
    """)
    
    # Tabela PROFIL_MEDYCZNY
    c.execute("""
        CREATE TABLE PROFIL_MEDYCZNY (
            ID_Profil INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_Zwierze INTEGER,
            SzczepienieWscieklizna DATE,
            SzczepienieZakazne DATE,
            Odrobaczenie DATE,
            DataKastracji DATE,
            OchronaKleszczeDo DATE,
            OpisZdrowia TEXT
        )
    """)

    # Tabela OSOBA (z nowymi polami, o które walczyliśmy)
    c.execute("""
        CREATE TABLE OSOBA (
            ID_Osoba INTEGER PRIMARY KEY AUTOINCREMENT,
            Imie TEXT,
            Nazwisko TEXT,
            Rola TEXT,
            Telefon TEXT,
            Email TEXT,
            Miasto TEXT,
            DataRejestracji DATE
        )
    """)

    conn.commit()
    conn.close()

    yield # Tu dzieją się testy...

    # Sprzątanie po testach
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            pass

# ==========================================
# TESTY LOGOWANIA I UŻYTKOWNIKÓW
# ==========================================

def test_create_and_verify_user(setup_database):
    """Testuje tworzenie użytkownika i logowanie."""
    login = "tester"
    email = "test@example.com"
    haslo = "Haslo123!"
    rola = "Administrator"

    # 1. Tworzenie
    assert crud.create_user(login, email, haslo, rola) == True
    
    # 2. Próba utworzenia dubla (powinna zwrócić False)
    assert crud.create_user(login, "inny@email.com", "inne", "User") == False

    # 3. Logowanie poprawne
    role_db, name_db = crud.verify_user(login, haslo)
    assert role_db == rola
    assert name_db == login

    # 4. Logowanie błędne
    role_wrong, _ = crud.verify_user(login, "ZleHaslo")
    assert role_wrong is None

# ==========================================
# TESTY REJESTRU ZWIERZĄT
# ==========================================

def test_animal_lifecycle(setup_database):
    """Testuje dodanie zwierzaka, edycję i adopcję."""
    # 1. Dodanie
    id_zw = crud.add_animal("Burek", "Pies", "Samiec", "Do adopcji")
    assert id_zw is not None
    assert isinstance(id_zw, int)

    # 2. Pobranie szczegółów
    details = crud.get_animal_details(id_zw)
    assert details['Imie'] == "Burek"
    assert details['StatusZwierzecia'] == "Do adopcji"

    # 3. Edycja (Dodanie Chipa)
    # update_animal_basic wymaga wielu argumentów, podajemy przykładowe
    crud.update_animal_basic(
        id_zw, "Burek", "Pies", "Kundel", "Samiec", 
        "2020-01-01", "4 lata", "Do adopcji", "CHIP-999", "Opis", "2024-01-01"
    )
    
    details_after = crud.get_animal_details(id_zw)
    assert details_after['NrChip'] == "CHIP-999"

    # 4. Adopcja
    sukces = crud.adoptuj_zwierze(id_zw, "Jan Kowalski, Tel: 123", "2025-05-01")
    assert sukces == True
    
    # Sprawdzenie czy status się zmienił
    details_adopted = crud.get_animal_details(id_zw)
    assert details_adopted['StatusZwierzecia'] == "Adoptowany"
    assert "Jan Kowalski" in details_adopted['DaneAdoptujacego']

# ==========================================
# TESTY BAZY OSÓB (Nowe pola)
# ==========================================

def test_people_database(setup_database):
    """Testuje dodawanie osób z nowymi polami (Miasto, Rola)."""
    crud.add_person("Anna", "Nowak", "Wolontariusz", "123", "a@n.pl", "Warszawa")
    
    df = crud.get_all_people()
    assert not df.empty
    
    # Pobieramy ostatni wiersz
    osoba = df.iloc[-1]
    assert osoba['Imie'] == "Anna"
    assert osoba['Miasto'] == "Warszawa"
    assert osoba['Rola'] == "Wolontariusz"
    # Sprawdzamy czy data rejestracji się dodała automatycznie
    assert str(date.today()) in str(osoba['DataRejestracji'])

# ==========================================
# TESTY MEDYCZNE (Kleszcze)
# ==========================================

def test_medical_update(setup_database):
    id_zw = crud.add_animal("Mruczek", "Kot", "Samiec", "Kwarantanna")
    
    # Aktualizacja kleszczy
    crud.update_medical_profile(id_zw, None, None, None, None, "2025-12-31", "Zdrowy")
    
    profile = crud.get_medical_profile(id_zw)
    assert profile['OchronaKleszczeDo'] == "2025-12-31"