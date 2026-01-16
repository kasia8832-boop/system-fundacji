import sqlite3
import hashlib

DB_FILE = "fundacja.db"

def napraw_wszystko():
    print("🔧 Rozpoczynam naprawę systemu...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # ==========================================
    # 1. TWORZENIE TABEL SŁOWNIKOWYCH (Jeśli nie istnieją)
    # ==========================================
    slowniki = {
        "SLOWNIK_GATUNKI": ["Pies", "Kot", "Królik", "Gryzoń", "Ptak", "Inne"],
        "SLOWNIK_STATUSY": ["Do adopcji", "W trakcie leczenia", "Kwarantanna", "Adoptowany", "Za Tęczowym Mostem", "Tymczasowo niedostępny"],
        "SLOWNIK_KATEGORIE": ["Wizyta weterynaryjna", "Zabieg", "Szczepienie", "Odrobaczenie", "Incydent", "Notatka behawioralna", "Inne"],
        "SLOWNIK_ZRODLO": ["Interwencja", "Znaleziony", "Zrzeczenie właściciela", "Urodzony w fundacji", "Inne"]
    }

    for tabela, wartosci in slowniki.items():
        # Tworzymy tabelę
        c.execute(f"CREATE TABLE IF NOT EXISTS {tabela} (ID INTEGER PRIMARY KEY AUTOINCREMENT, Wartosc TEXT UNIQUE)")
        
        # Czyścimy ją (opcjonalnie, żeby nie dublować przy wielokrotnym uruchomieniu, ale insert ignore jest bezpieczniejszy)
        # Tutaj po prostu uzupełniamy braki
        print(f"📚 Uzupełniam słownik: {tabela}...")
        for val in wartosci:
            try:
                c.execute(f"INSERT INTO {tabela} (Wartosc) VALUES (?)", (val,))
            except sqlite3.IntegrityError:
                pass # Już istnieje, ignorujemy

    # ==========================================
    # 2. NAPRAWA KONTA ADMINA
    # ==========================================
    login = "admin@fundacja.pl"
    haslo_jawne = "admin123"
    
    # Generujemy hash nowego typu (z solą 'salt_fundacja' jak w crud.py)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        haslo_jawne.encode('utf-8'), 
        b'salt_fundacja', 
        100000
    ).hex()

    print(f"👤 Naprawiam konto admina ({login})...")
    
    # Sprawdzamy czy user istnieje
    c.execute("SELECT ID_User FROM UZYTKOWNIK WHERE LoginName = ?", (login,))
    exists = c.fetchone()

    if exists:
        # Aktualizujemy hasło istniejącego admina
        c.execute("UPDATE UZYTKOWNIK SET HasloHash = ?, Rola = 'Administrator', CzyAktywny = 1 WHERE LoginName = ?", (password_hash, login))
        print("✅ Zaktualizowano hasło dla istniejącego Admina.")
    else:
        # Tworzymy nowego admina
        c.execute("""
            INSERT INTO UZYTKOWNIK (LoginName, Email, HasloHash, Rola, CzyAktywny)
            VALUES (?, ?, ?, 'Administrator', 1)
        """, (login, login, password_hash))
        print("✅ Utworzono nowe konto Admina.")

    conn.commit()
    conn.close()
    print("\n🚀 GOTOWE! Możesz uruchomić aplikację.")
    print(f"👉 Login: {login}")
    print(f"👉 Hasło: {haslo_jawne}")

if __name__ == "__main__":
    napraw_wszystko()