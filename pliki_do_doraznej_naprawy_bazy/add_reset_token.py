import sqlite3

DB_FILE = "fundacja.db"

def dodaj_token_resetu():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        # Dodajemy kolumnę na kod resetujący (np. 6 cyfr)
        c.execute("ALTER TABLE UZYTKOWNIK ADD COLUMN ResetToken TEXT")
        print("✅ Dodano kolumnę ResetToken do tabeli UZYTKOWNIK.")
    except sqlite3.OperationalError:
        print("ℹ️ Kolumna ResetToken już istnieje.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    dodaj_token_resetu()