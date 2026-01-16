"""
SKRYPT KONFIGURACYJNY: AKTUALIZACJA MODUŁU HISTORII
---------------------------------------------------
Ten skrypt automatyzuje proces wdrażania załączników:
1. Tworzy brakujący plik 'event_details.py' z odpowiednim nagłówkiem.
2. Łączy się z bazą danych i dodaje tabelę ZALACZNIKI (jeśli nie istnieje).
"""

import os
import sqlite3

# KONFIGURACJA
DB_FILE = "fundacja.db"
TARGET_DIR = "views/registry_modules/details_components"
NEW_FILE = "event_details.py"

# TREŚĆ NAGŁÓWKA DLA NOWEGO PLIKU
FILE_HEADER = '''"""
KOMPONENT: SZCZEGÓŁY ZDARZENIA (HISTORIA)
-----------------------------------------
Wyświetla pełne informacje o jednym zdarzeniu z historii.
Pozwala przeglądać, pobierać i dodawać załączniki (pliki).
"""
import streamlit as st
import pandas as pd
import crud

# ... (WKLEJ TUTAJ RESZTĘ KODU Z CZATU) ...
'''

def create_structure():
    print(f"📂 Sprawdzam folder: {TARGET_DIR}...")
    if not os.path.exists(TARGET_DIR):
        print("❌ Błąd: Nie znaleziono folderu details_components! Najpierw wykonaj poprzednią refaktoryzację.")
        return False
    
    file_path = os.path.join(TARGET_DIR, NEW_FILE)
    
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(FILE_HEADER)
        print(f"✅ Utworzono plik: {file_path}")
    else:
        print(f"ℹ️  Plik {NEW_FILE} już istnieje. Pomijam tworzenie.")
    return True

def update_database():
    print(f"🗄️  Aktualizuję bazę danych: {DB_FILE}...")
    
    if not os.path.exists(DB_FILE):
        print("❌ Błąd: Nie znaleziono pliku bazy danych!")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # SQL do utworzenia tabeli załączników
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS ZALACZNIKI (
            ID_Zalacznik INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_Historia INTEGER,
            NazwaPliku TEXT,
            TypPliku TEXT,
            DaneBLOB BLOB,
            DataDodania DATE,
            FOREIGN KEY(ID_Historia) REFERENCES HISTORIA_ZDARZEN(ID_Historia)
        );
        """
        c.execute(sql_create_table)
        conn.commit()
        conn.close()
        print("✅ Tabela 'ZALACZNIKI' została utworzona (lub już istniała).")
        
    except Exception as e:
        print(f"❌ Błąd SQL: {e}")

if __name__ == "__main__":
    print("--- ROZPOCZYNAM AKTUALIZACJĘ SYSTEMU ---")
    if create_structure():
        update_database()
    print("\n--- ZAKOŃCZONO ---")
    print("TERAZ TWOJE ZADANIE:")
    print("1. Otwórz 'views/registry_modules/details_components/event_details.py' i wklej kod logiki.")
    print("2. Zaktualizuj 'crud.py' o nowe funkcje (dodaj_zalacznik, itp.).")
    print("3. Podmień kod w 'views/registry_modules/details_components/tab_history.py'.")