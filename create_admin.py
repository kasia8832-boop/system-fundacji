from database import SessionLocal
from models import Uzytkownik, Osoba, SlownikGatunek, SlownikStatus, SlownikKategoria
import hashlib

def create_initial_data():
    db = SessionLocal()
    print("--- INICJALIZACJA DANYCH STARTOWYCH ---")

    # ==========================================
    # 1. TWORZENIE ADMINA
    # ==========================================
    # Sprawdź czy admin już istnieje
    existing_admin = db.query(Uzytkownik).filter(Uzytkownik.LoginName == "admin").first()
    
    if not existing_admin:
        print("Tworzenie konta Administratora...")
        
        # Najpierw tworzymy Osobę (bo Użytkownik musi być połączony z Osobą)
        admin_osoba = Osoba(
            Imie="Super",
            Nazwisko="Administrator",
            Email="admin@fundacja.pl",
            AdresMiasto="Centrala",
            AdresUlica="Internetowa 1"
        )
        db.add(admin_osoba)
        db.flush() # Wykonujemy flush, aby baza nadała IDOsoba, zanim zrobimy commit
        
        # Generujemy hash hasła
        haslo_plain = "admin123"
        haslo_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            haslo_plain.encode('utf-8'), 
            b'salt_fundacja', 
            100000
        ).hex()
        
        # Tworzymy Użytkownika
        admin_user = Uzytkownik(
            LoginName="admin",
            Email="admin@fundacja.pl",
            HasloHash=haslo_hash,
            Rola="Admin",
            IDOsoba=admin_osoba.IDOsoba, # Łączymy z utworzoną wyżej osobą
            CzyAktywny=True
        )
        db.add(admin_user)
        print(f"✅ Dodano użytkownika: admin / hasło: {haslo_plain}")
    else:
        print("ℹ️ Konto admina już istnieje.")

    # ==========================================
    # 2. UZUPEŁNIANIE SŁOWNIKÓW
    # ==========================================
    print("Uzupełnianie słowników...")

    # Gatunki
    gatunki = ["Pies", "Kot", "Królik", "Inne"]
    for g in gatunki:
        if not db.query(SlownikGatunek).filter_by(Wartosc=g).first():
            db.add(SlownikGatunek(Wartosc=g))

    # Statusy
    statusy = ["Do Adopcji", "W trakcie leczenia", "Kwarantanna", "Rezerwacja", "Adoptowany", "Za Tęczowym Mostem"]
    for s in statusy:
        if not db.query(SlownikStatus).filter_by(Wartosc=s).first():
            db.add(SlownikStatus(Wartosc=s))

    # Kategorie zdarzeń (Historia)
    kategorie = ["Wizyta Weterynaryjna", "Szczepienie", "Zabieg", "Behawiorysta", "Notatka Wolontariusza", "Adopcja"]
    for k in kategorie:
        if not db.query(SlownikKategoria).filter_by(Wartosc=k).first():
            db.add(SlownikKategoria(Wartosc=k))

    try:
        db.commit()
        print("✅ Słowniki uzupełnione pomyślnie!")
    except Exception as e:
        db.rollback()
        print(f"❌ Błąd podczas zapisu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()