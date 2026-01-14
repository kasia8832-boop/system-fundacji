import sqlite3
import random
from datetime import date, timedelta, datetime

DB_FILE = 'fundacja.db'

# --- BAZA DANYCH DO GENERATORA ---
IMIONA_PSY = ["Reksio", "Azor", "Burek", "Fafik", "Luna", "Saba", "Maks", "Bella", "Rocky", "Daisy", "Simba", "Nela", "Koko", "Dora", "Gucio", "Maja", "Piorun", "Łatka", "Czarek", "Bruno", "Sonia", "Kajtek", "Pusia", "Borys", "Ares", "Fiona", "Dżeki", "Tosia", "Odi", "Mela", "Szaman", "Wera", "Zulus", "Hera", "Tytus", "Kora", "Ciapek", "Figa", "Loki", "Dyzio"]
IMIONA_KOTY = ["Mruczek", "Kitek", "Filemon", "Bonifacy", "Puszek", "Mia", "Luna", "Kicia", "Rysio", "Tygrys", "Plamka", "Kleo", "Simba", "Nala", "Salem", "Garfield", "Lola", "Tofik", "Zuzia", "Felix", "Bela", "Gacek", "Mela", "Ciri", "Yennefer", "Geralt", "Triss", "Jaskier", "Płotka", "Zelda"]
IMIONA_INNE = ["Tuptuś", "Kicałek", "Chrupek", "Bugs", "Lola", "Alvin", "Teodor", "Szymon", "Bambi", "Pepa"]

GATUNKI = ["Pies"] * 60 + ["Kot"] * 35 + ["Inne"] * 5  # 60% Psy, 35% Koty, 5% Inne
STATUSY = ["Do adopcji", "Do adopcji", "Do adopcji", "Adoptowany", "Adoptowany", "Leczenie", "Kwarantanna"]
ZRODLA = ["Znaleziony", "Oddany", "Interwencja", "Urodzony w fundacji"]

IMIONA_LUDZIE = ["Anna", "Piotr", "Krzysztof", "Maria", "Agnieszka", "Jan", "Tomasz", "Ewa", "Michał", "Paweł", "Magdalena", "Marcin", "Katarzyna", "Andrzej", "Małgorzata", "Stanisław", "Barbara", "Jakub", "Zofia", "Adam"]
NAZWISKA = ["Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Jankowski", "Mazur", "Kwiatkowski", "Krawczyk"]
MIASTA = ["Warszawa", "Kraków", "Wrocław", "Poznań", "Gdańsk", "Łódź", "Lublin", "Katowice", "Białystok", "Szczecin"]
ULICE = ["Polna", "Leśna", "Słoneczna", "Krótka", "Długa", "Lipowa", "Brzozowa", "Łąkowa", "Kwiatowa", "Ogrodowa"]

UWAGI_MEDYCZNE = [
    "Stan ogólny dobry.", "Wymaga obserwacji po zabiegu.", "Alergia na drób.", "Problemy ze stawami, zalecana suplementacja.", 
    "Lekka nadwaga, zalecana dieta.", "Regularne czyszczenie uszu.", "Po urazie łapy, kuleje.", "Wymaga specjalistycznej karmy nerkowej.", 
    "Zdrowy, gotowy do adopcji.", "Zęby wymagają sanacji."
]

OPISY_HISTORIA = [
    "Znaleziony błąkający się przy drodze.", "Oddany przez właściciela z powodu alergii.", "Interwencja w pseudohodowli.", 
    "Przyniesiony przez straż miejską.", "Znaleziony w lesie przywiązany do drzewa.", "Urodzony w domu tymczasowym."
]

ZDJECIA_PSY = [
    "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1596492784531-6e6eb5ea9205?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=400&q=80"
]
ZDJECIA_KOTY = [
    "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1495360019602-e001920a2746?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13?auto=format&fit=crop&w=400&q=80"
]


def rand_date(start_year=2018):
    start = datetime(start_year, 1, 1)
    end = datetime.now()
    delta = end - start
    random_days = random.randrange(delta.days)
    return (start + timedelta(days=random_days)).date()

def generuj():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    print("🚀 Rozpoczynam generowanie danych...")

    # 1. Generowanie Osób (30 sztuk)
    print("👤 Tworzę ludzi...")
    osoby_ids = []
    dt_ids = [] # IDs osób, które są DT
    
    for _ in range(30):
        imie = random.choice(IMIONA_LUDZIE)
        nazwisko = random.choice(NAZWISKA)
        czy_dt = 1 if random.random() < 0.3 else 0 # 30% szans na bycie DT
        email = f"{imie.lower()}.{nazwisko.lower()}{random.randint(1,99)}@example.com"
        
        c.execute("""
            INSERT INTO OSOBA (Imie, Nazwisko, Telefon, Email, AdresMiasto, AdresUlica, CzyJestDT)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            imie, nazwisko, 
            f"{random.randint(500,800)}-{random.randint(100,999)}-{random.randint(100,999)}",
            email, random.choice(MIASTA), f"{random.choice(ULICE)} {random.randint(1,100)}",
            czy_dt
        ))
        id_osoby = c.lastrowid
        osoby_ids.append(id_osoby)
        if czy_dt: dt_ids.append(id_osoby)

    # Upewniamy się, że jest przynajmniej jeden DT
    if not dt_ids and osoby_ids:
        dt_ids.append(osoby_ids[0])

    # 2. Generowanie Zwierząt (100 sztuk)
    print("🐾 Tworzę 100 zwierząt...")
    
    for i in range(100):
        gatunek = random.choice(GATUNKI)
        plec = random.choice(['M', 'K'])
        
        # Imię zależne od gatunku
        if gatunek == 'Pies': imie = random.choice(IMIONA_PSY)
        elif gatunek == 'Kot': imie = random.choice(IMIONA_KOTY)
        else: imie = random.choice(IMIONA_INNE)
        
        # Unikalne imię (dodajemy numer jeśli trzeba, żeby nie było 10 Reksiów)
        if random.random() > 0.7: imie = f"{imie} {random.choice(['Junior', 'Senior', 'Duży', 'Mały'])}"
        
        status = random.choice(STATUSY)
        data_ur = rand_date(2015)
        chip = str(random.randint(616093400000000, 616099900000000)) if random.random() > 0.2 else None
        
        # Opiekun i Adopcja
        id_dt = random.choice(dt_ids) if dt_ids else None
        id_adoptujacy = None
        data_adopcji = None
        
        if status == 'Adoptowany':
            id_adoptujacy = random.choice(osoby_ids)
            data_adopcji = rand_date(2023).strftime("%Y-%m-%d")
            # Jeśli adoptowany, to zazwyczaj nie ma już DT, ale w historii mógł mieć
            id_dt = None 

        # Zdjęcie
        img = None
        if gatunek == 'Pies': img = random.choice(ZDJECIA_PSY)
        elif gatunek == 'Kot': img = random.choice(ZDJECIA_KOTY)
        
        # INSERT ZWIERZE
        c.execute("""
            INSERT INTO ZWIERZE (Imie, Gatunek, Plec, NrChip, DataUrodzenia, StatusZwierzecia, 
            ZrodloFinansowania, CzyOgloszenieOLX, CzyOgloszenieWWW, ID_OpiekunTymczasowy, 
            ID_Adoptujacy, DataAdopcji, ZdjecieProfilowe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            imie, gatunek, plec, chip, data_ur.strftime("%Y-%m-%d"), status,
            random.choice(ZRODLA), random.randint(0,1), random.randint(0,1),
            id_dt, id_adoptujacy, data_adopcji, img
        ))
        id_zw = c.lastrowid
        
        # 3. Profil Medyczny
        czy_kast = 1 if status == 'Adoptowany' or random.random() > 0.4 else 0
        data_kast = (data_ur + timedelta(days=365)).strftime("%Y-%m-%d") if czy_kast else None
        
        c.execute("""
            INSERT INTO PROFIL_MEDYCZNY (ID_Zwierze, CzyKastrowany, DataKastracji, 
            SzczepienieWscieklizna, SzczepienieZakazne, Odrobaczenie, UwagiMedyczne)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            id_zw, czy_kast, data_kast,
            rand_date(2023).strftime("%Y-%m-%d"), rand_date(2023).strftime("%Y-%m-%d"),
            rand_date(2024).strftime("%Y-%m-%d"),
            random.choice(UWAGI_MEDYCZNE) if random.random() > 0.5 else None
        ))
        
        # 4. Historia (1-4 wpisy na zwierzę)
        # Pierwszy wpis: Przyjęcie
        data_przyjecia = (data_ur + timedelta(days=random.randint(30, 1000)))
        if data_przyjecia > datetime.now().date(): data_przyjecia = datetime.now().date()
        
        c.execute("INSERT INTO OS_CZASU_ZDARZENIE (ID_Zwierze, DataZdarzenia, Kategoria, Opis) VALUES (?, ?, ?, ?)",
                 (id_zw, data_przyjecia.strftime("%Y-%m-%d"), "Inne", random.choice(OPISY_HISTORIA)))
        
        # Kolejne losowe wpisy
        for _ in range(random.randint(0, 3)):
            data_zd = data_przyjecia + timedelta(days=random.randint(1, 300))
            if data_zd > datetime.now().date(): break
            
            kategoria = random.choice(["Wizyta", "Zabieg", "Inne"])
            opis = f"Rutynowe działanie: {kategoria}. {random.choice(UWAGI_MEDYCZNE)}"
            c.execute("INSERT INTO OS_CZASU_ZDARZENIE (ID_Zwierze, DataZdarzenia, Kategoria, Opis) VALUES (?, ?, ?, ?)",
                     (id_zw, data_zd.strftime("%Y-%m-%d"), kategoria, opis))

        # 5. Galeria (losowo dodatkowe zdjęcia)
        if random.random() > 0.7:
            for _ in range(random.randint(1,3)):
                fotka = random.choice(ZDJECIA_PSY if gatunek == 'Pies' else ZDJECIA_KOTY)
                c.execute("INSERT INTO ZWIERZE_GALERIA (ID_Zwierze, ZdjecieURL, Opis) VALUES (?, ?, ?)",
                         (id_zw, fotka, "Zdjęcie z spaceru"))

    conn.commit()
    conn.close()
    print(f"✅ Zakończono! Baza 'fundacja.db' ma teraz 30 osób i 100 zwierząt.")

if __name__ == "__main__":
    generuj()