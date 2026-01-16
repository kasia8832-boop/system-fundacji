import sqlite3

DB_FILE = "fundacja.db"

def dodaj_konfiguracje_alertow():
    print(f"🔌 Łączę się z bazą {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 1. Tworzymy tabelę konfiguracyjną
    # KodPola musi odpowiadać dokładnie nazwie kolumny w tabeli PROFIL_MEDYCZNY!
    c.execute("""
    CREATE TABLE IF NOT EXISTS KONFIGURACJA_ALERTY (
        KodPola TEXT PRIMARY KEY,  -- np. 'SzczepienieWscieklizna'
        Etykieta TEXT,             -- np. 'Szczepienie na Wściekliznę' (do wyświetlania)
        DniWaznosci INTEGER,       -- np. 365
        CzyAktywny INTEGER DEFAULT 1
    );
    """)

    # 2. Wstawiamy domyślne wartości (żeby system od razu działał)
    # Używamy INSERT OR REPLACE, żebyś mógł uruchamiać ten skrypt wielokrotnie bez błędów
    domyslne = [
        ("SzczepienieWscieklizna", "Wścieklizna", 365, 1),
        ("SzczepienieZakazne", "Choroby Zakaźne", 365, 1),
        ("Odrobaczenie", "Odrobaczenie", 180, 1),
        ("DataKastracji", "Kastracja (Kontrola po)", 14, 0) # Domyślnie wyłączone
    ]

    c.executemany("INSERT OR REPLACE INTO KONFIGURACJA_ALERTY VALUES (?, ?, ?, ?)", domyslne)

    conn.commit()
    conn.close()
    print("✅ Tabela KONFIGURACJA_ALERTY została utworzona i uzupełniona.")

if __name__ == "__main__":
    dodaj_konfiguracje_alertow()