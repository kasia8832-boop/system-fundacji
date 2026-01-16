import sqlite3
from datetime import date

DB_FILE = "fundacja.db"

def napraw_tabele_osoba_kompleksowo():
    print("🔧 Rozpoczynam kompleksową naprawę tabeli OSOBA...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Lista kolumn, których Twój nowy kod wymaga w tabeli OSOBA
    # (Nazwa kolumny, Typ danych, Domyślna wartość przy aktualizacji)
    brakujace_kolumny = [
        ("Rola", "TEXT", "Wolontariusz"),
        ("Miasto", "TEXT", "Nieznane"),
        ("DataRejestracji", "DATE", date.today().strftime("%Y-%m-%d"))
    ]

    for kolumna, typ, domyslna in brakujace_kolumny:
        try:
            print(f"👉 Sprawdzam kolumnę '{kolumna}'...")
            c.execute(f"ALTER TABLE OSOBA ADD COLUMN {kolumna} {typ}")
            print(f"   ✅ Dodano kolumnę '{kolumna}'.")
            
            # Uzupełniamy stare rekordy, żeby nie było NULL
            c.execute(f"UPDATE OSOBA SET {kolumna} = ? WHERE {kolumna} IS NULL", (domyslna,))
            print(f"   ✅ Uzupełniono stare wpisy wartością: '{domyslna}'.")
            
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"   ℹ️ Kolumna '{kolumna}' już istnieje. Pomijam.")
            else:
                print(f"   ❌ Błąd przy kolumnie {kolumna}: {e}")

    conn.commit()
    conn.close()
    print("\n🚀 Tabela OSOBA naprawiona. Możesz uruchomić aplikację.")

if __name__ == "__main__":
    napraw_tabele_osoba_kompleksowo()