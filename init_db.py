# init_db.py
from database import engine, Base
# Importujemy modele. Zauważ, że usunąłem ProfilMedyczny z tej listy
from models import Osoba, Uzytkownik, Zwierze, HistoriaZdarzen, Zalacznik

print("--- TWORZENIE NOWEJ BAZY (Zintegrowany Profil) ---")
Base.metadata.create_all(bind=engine)
print("✅ Gotowe! Baza fundacja.db została zaktualizowana.")