# crud.py
"""
MODUŁ: CRUD (Create, Read, Update, Delete) - Wersja ORM (SQLAlchemy)
--------------------------------------------------------------------
Odpowiada za logikę biznesową i komunikację z bazą danych.
Teraz korzysta z klas zdefiniowanych w models.py, zamiast surowego SQL.
"""
import pandas as pd
import hashlib
from datetime import date, datetime
from sqlalchemy import text
from database import SessionLocal
from models import (
    Uzytkownik, Osoba, Zwierze, HistoriaZdarzen, Zalacznik,
    SlownikGatunek, SlownikStatus, SlownikKategoria, KonfiguracjaAlerty
)

# ==============================================================================
# 🔧 NARZĘDZIA POMOCNICZE
# ==============================================================================

def get_db_session():
    """Tworzy nową sesję do bazy danych."""
    return SessionLocal()

def hash_password(password: str) -> str:
    """Szyfrowanie hasła (SHA256 + Salt)."""
    return hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        b'salt_fundacja', 
        100000
    ).hex()

# ==============================================================================
# 👤 1. UŻYTKOWNICY I LOGOWANIE
# ==============================================================================

def verify_user(login_input, password_input):
    """
    Weryfikuje logowanie.
    Zwraca: (Rola, LoginName, IDOsoba) lub (None, None, None)
    """
    db = get_db_session()
    try:
        # Szukamy użytkownika po loginie
        user = db.query(Uzytkownik).filter(Uzytkownik.LoginName == login_input, Uzytkownik.CzyAktywny == True).first()
        
        if user:
            input_hash = hash_password(password_input)
            if user.HasloHash == input_hash:
                # Zwracamy IDOsoba, aby wiedzieć kim fizycznie jest ten user (np. dla DT)
                return user.Rola, user.LoginName, user.IDOsoba
                
        return None, None, None
    finally:
        db.close() # Zawsze zamykamy sesję!

def create_user(login, email, password, rola, id_osoba=None):
    """Tworzy nowego użytkownika systemowego."""
    db = get_db_session()
    try:
        new_user = Uzytkownik(
            LoginName=login,
            Email=email,
            HasloHash=hash_password(password),
            Rola=rola,
            IDOsoba=id_osoba, # Powiązanie z tabelą OSOBA
            CzyAktywny=True
        )
        db.add(new_user)
        db.commit()
        return True, "Użytkownik utworzony."
    except Exception as e:
        db.rollback() # Cofnij zmiany w razie błędu
        return False, f"Błąd: {e}"
    finally:
        db.close()

# ==============================================================================
# 🐾 2. ZWIERZĘTA (LISTING I SZCZEGÓŁY)
# ==============================================================================

def pobierz_liste_zwierzat(id_opiekun_dt=None):
    """
    Pobiera DataFrame do kafelków na stronie głównej (Listing).
    Filtracja:
    - Jeśli id_opiekun_dt jest podane -> pokazuje tylko zwierzęta przypisane do tego DT.
    - Ukrywa zwierzęta 'Za Tęczowym Mostem'.
    """
    db = get_db_session()
    try:
        # Budujemy zapytanie (Query)
        q = db.query(
            Zwierze.IDZwierze, 
            Zwierze.Imie, 
            Zwierze.Rasa, 
            Zwierze.StatusZwierzecia, 
            Zwierze.Zdjecie,
            Zwierze.IDOpiekun # Potrzebne do weryfikacji
        ).filter(Zwierze.StatusZwierzecia != 'Za Tęczowym Mostem')

        # Jeśli to DT, dodajemy filtr WHERE IDOpiekun = ...
        if id_opiekun_dt:
            q = q.filter(Zwierze.IDOpiekun == id_opiekun_dt)

        # Pobieramy dane do Pandas DataFrame
        # statement to skompilowany SQL, db.bind to połączenie
        df = pd.read_sql(q.statement, db.bind)
        return df
    except Exception as e:
        print(f"Błąd listingu: {e}")
        return pd.DataFrame()
    finally:
        db.close()

def pobierz_szczegoly_zwierzecia(id_zwierze):
    """Pobiera pełny obiekt zwierzęcia (wraz z polami medycznymi)."""
    db = get_db_session()
    try:
        zwierze = db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).first()
        return zwierze
    finally:
        db.close()

def dodaj_nowe_zwierze(imie, gatunek, plec, status, id_nadzorca=None):
    """Rejestruje nowe zwierzę."""
    db = get_db_session()
    try:
        nowe = Zwierze(
            Imie=imie,
            Gatunek=gatunek,
            Plec=plec,
            StatusZwierzecia=status,
            IDNadzor=id_nadzorca, # Kto wprowadza/opiekuje się z ramienia fundacji
            DataPrzyjecia=date.today()
        )
        db.add(nowe)
        db.commit()
        return nowe.IDZwierze
    except Exception as e:
        db.rollback()
        print(e)
        return None
    finally:
        db.close()

# ==============================================================================
# ✏️ 3. EDYCJA DANYCH (ZWIERZĘ + MEDYCZNE)
# ==============================================================================

def aktualizuj_dane_podstawowe(id_zwierze, dane_dict):
    """
    Aktualizuje podstawowe pola (Imie, Rasa, Chip itp.)
    dane_dict: słownik {NazwaPolaModelu: Wartość}
    """
    db = get_db_session()
    try:
        # Pobieramy obiekt do edycji
        zwierze = db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).first()
        if not zwierze:
            return False

        # Aktualizujemy pola dynamicznie
        for key, value in dane_dict.items():
            if hasattr(zwierze, key): # Sprawdź czy pole istnieje w modelu
                setattr(zwierze, key, value)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Błąd update: {e}")
        return False
    finally:
        db.close()

def aktualizuj_zdjecie(id_zwierze, bytes_data):
    """Zapisuje BLOB zdjęcia."""
    db = get_db_session()
    try:
        db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).update({Zwierze.Zdjecie: bytes_data})
        db.commit()
    finally:
        db.close()

def adoptuj_zwierze(id_zwierze, id_nowy_wlasciciel):
    """
    Finalizacja adopcji:
    1. Zmienia status na 'Adoptowany'.
    2. Przypisuje IDOpiekun = id_nowy_wlasciciel.
    """
    db = get_db_session()
    try:
        zwierze = db.query(Zwierze).filter(Zwierze.IDZwierze == id_zwierze).first()
        if zwierze:
            zwierze.StatusZwierzecia = 'Adoptowany'
            zwierze.IDOpiekun = id_nowy_wlasciciel
            # zwierze.DataAdopcji - usunęliśmy to pole z bazy, historia załatwi sprawę daty
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

# ==============================================================================
# 🏥 4. MEDYCYNA I HISTORIA
# ==============================================================================

def dodaj_wpis_historii(id_zwierze, id_user, kategoria, opis):
    """
    Dodaje zdarzenie do historii.
    WAŻNE: id_user to ID zalogowanego UZYTKOWNIKA, nie Osoby.
    """
    db = get_db_session()
    try:
        wpis = HistoriaZdarzen(
            IDZwierze=id_zwierze,
            IDUser=id_user,
            Kategoria=kategoria,
            Opis=opis,
            DataZdarzenia=date.today()
        )
        db.add(wpis)
        db.commit()
        return wpis.IDHistoria
    except Exception as e:
        db.rollback()
        return None
    finally:
        db.close()

def pobierz_historie(id_zwierze):
    """Pobiera historię jako DataFrame (do wyświetlenia tabeli)."""
    db = get_db_session()
    try:
        # Łączymy (JOIN) z tabelą Uzytkownik, żeby pobrać Login autora wpisu
        # POPRAWKA: Dodano HistoriaZdarzen.IDHistoria do zapytania!
        q = db.query(
            HistoriaZdarzen.IDHistoria,      # <--- TO BYŁO KLUCZOWE
            HistoriaZdarzen.DataZdarzenia,
            HistoriaZdarzen.Kategoria,
            HistoriaZdarzen.Opis,
            Uzytkownik.LoginName.label("Autor")
        ).join(Uzytkownik, HistoriaZdarzen.IDUser == Uzytkownik.IDUser)\
         .filter(HistoriaZdarzen.IDZwierze == id_zwierze)\
         .order_by(HistoriaZdarzen.DataZdarzenia.desc())
        
        df = pd.read_sql(q.statement, db.bind)
        return df
    finally:
        db.close()

# ==============================================================================
# 👥 5. OSOBY (Słownik Ludzi)
# ==============================================================================

def pobierz_wszystkie_osoby():
    """Zwraca DataFrame wszystkich osób (do selectboxów)."""
    db = get_db_session()
    try:
        q = db.query(Osoba.IDOsoba, Osoba.Imie, Osoba.Nazwisko, Osoba.AdresMiasto)
        df = pd.read_sql(q.statement, db.bind)
        # Tworzymy kolumnę pomocniczą do wyświetlania w SelectBox (np. "Jan Kowalski (Warszawa)")
        if not df.empty:
            df['Display'] = df['Imie'] + " " + df['Nazwisko'] + " (" + df['AdresMiasto'].fillna('-') + ")"
        return df
    finally:
        db.close()

def dodaj_osobe(imie, nazwisko, telefon, email, miasto, ulica, lokal, kod):
    db = get_db_session()
    try:
        osoba = Osoba(
            Imie=imie, Nazwisko=nazwisko, Telefon=telefon, Email=email,
            AdresMiasto=miasto, AdresUlica=ulica, AdresNrLokalu=lokal, AdresKodPocztowy=kod
        )
        db.add(osoba)
        db.commit()
        return True, "Osoba dodana"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

# ==============================================================================
# 📚 6. SŁOWNIKI
# ==============================================================================

def pobierz_slownik(nazwa_modelu):
    """
    Pobiera wartości ze słownika.
    nazwa_modelu: np. 'gatunek', 'status'
    """
    db = get_db_session()
    model_map = {
        'gatunek': SlownikGatunek,
        'status': SlownikStatus,
        'kategoria': SlownikKategoria
    }
    
    try:
        model = model_map.get(nazwa_modelu)
        if not model: return []
        
        wyniki = db.query(model.Wartosc).all()
        return [w[0] for w in wyniki] # Spłaszczamy listę krotek do listy stringów
    finally:
        db.close()
# ==============================================================================
# 🚨 7. POWIADOMIENIA I ALERTY (DODANE)
# ==============================================================================

def pobierz_alerty_medyczne():
    """
    Skanuje bazę w poszukiwaniu przeterminowanych szczepień i badań.
    Zwraca listę słowników z alertami.
    """
    db = get_db_session()
    alerty = []
    dzis = date.today()
    
    try:
        # 1. Pobieramy aktywne reguły alertów
        reguly = db.query(KonfiguracjaAlerty).filter(KonfiguracjaAlerty.CzyAktywny == True).all()
        if not reguly:
            return []

        # 2. Pobieramy zwierzęta (tylko te, które są pod opieką fundacji)
        # Wykluczamy adoptowane i nieżyjące
        zwierzeta = db.query(Zwierze).filter(
            Zwierze.StatusZwierzecia.notin_(['Adoptowany', 'Za Tęczowym Mostem'])
        ).all()

        # 3. Pętla sprawdzająca
        for zwierzak in zwierzeta:
            for regula in reguly:
                pole = regula.KodPola      # np. "SzczepienieWscieklizna"
                limit_dni = regula.DniWaznosci
                etykieta = regula.Etykieta
                
                # Pobieramy wartość pola dynamicznie z obiektu Zwierze
                # getattr(obiekt, "NazwaPola") to to samo co obiekt.NazwaPola
                data_baza = getattr(zwierzak, pole, None)
                
                if not data_baza:
                    continue # Brak daty wpisanej = brak weryfikacji (lub można dodać alert "Brak danych")

                # --- A. LOGIKA DLA OCHRONY PRZECIW KLESZCZOM (Data "Ważne do") ---
                if pole == 'OchronaKleszczeDo':
                    # Tutaj data w bazie to data WYGAŚNIĘCIA, a nie zabiegu
                    dni_po_terminie = (dzis - data_baza).days
                    
                    if dni_po_terminie > 0: # Jeśli dzis jest po dacie wygaśnięcia
                        alerty.append({
                            "id": zwierzak.IDZwierze,
                            "imie": zwierzak.Imie,
                            "chip": zwierzak.NrChip,
                            "typ": "Wygasła Ochrona",
                            "komunikat": f"{etykieta}: wygasła {data_baza} ({dni_po_terminie} dni temu)"
                        })

                # --- B. LOGIKA DLA SZCZEPIEŃ (Data zabiegu + Okres ważności) ---
                else:
                    # Tutaj data w bazie to data ZABIEGU. Dodajemy do niej dni ważności.
                    dni_od_zabiegu = (dzis - data_baza).days
                    
                    if dni_od_zabiegu > limit_dni:
                        alerty.append({
                            "id": zwierzak.IDZwierze,
                            "imie": zwierzak.Imie,
                            "chip": zwierzak.NrChip,
                            "typ": "Przeterminowane",
                            "komunikat": f"{etykieta}: minęło {dni_od_zabiegu} dni (Limit: {limit_dni})"
                        })

        return alerty

    except Exception as e:
        print(f"Błąd generowania alertów: {e}")
        return []
    finally:
        db.close()

# ==============================================================================
# 📂 8. ZAŁĄCZNIKI I HISTORIA (BRAKUJĄCE FUNKCJE)
# ==============================================================================

def usun_wpis_historii(id_historia):
    """Usuwa zdarzenie i kaskadowo jego załączniki."""
    db = get_db_session()
    try:
        wpis = db.query(HistoriaZdarzen).filter(HistoriaZdarzen.IDHistoria == id_historia).first()
        if wpis:
            db.delete(wpis)
            db.commit()
            return True, "Usunięto wpis."
        return False, "Nie znaleziono wpisu."
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def pobierz_liste_zalacznikow(id_historia):
    """
    Pobiera listę plików BEZ ich zawartości (żeby nie zapchać pamięci).
    Oblicza rozmiar pliku na podstawie długości BLOBa.
    """
    db = get_db_session()
    try:
        # SQLAlchmey nie ma prostego func.length dla BLOB w każdym dialekcie,
        # więc pobierzemy obiekty, ale deferujemy (opóźniamy) pobranie DaneBLOB
        from sqlalchemy.orm import defer
        
        pliki = db.query(Zalacznik).filter(Zalacznik.IDHistoria == id_historia).all()
        
        data = []
        for p in pliki:
            rozmiar = len(p.DaneBLOB) if p.DaneBLOB else 0
            data.append({
                "ID_Zalacznik": p.IDZalacznik,
                "NazwaPliku": p.NazwaPliku,
                "TypPliku": p.TypPliku,
                "RozmiarBajt": rozmiar
            })
        return pd.DataFrame(data)
    finally:
        db.close()

def pobierz_plik_content(id_zalacznik):
    """Pobiera pełną zawartość pliku (BLOB) do pobrania."""
    db = get_db_session()
    try:
        plik = db.query(Zalacznik).filter(Zalacznik.IDZalacznik == id_zalacznik).first()
        if plik:
            return plik.NazwaPliku, plik.DaneBLOB, plik.TypPliku
        return None
    finally:
        db.close()

def dodaj_zalacznik(id_historia, uploaded_file):
    """Zapisuje plik w bazie."""
    db = get_db_session()
    try:
        bytes_data = uploaded_file.getvalue()
        
        nowy = Zalacznik(
            IDHistoria=id_historia,
            NazwaPliku=uploaded_file.name,
            TypPliku=uploaded_file.type,
            DaneBLOB=bytes_data
        )
        db.add(nowy)
        db.commit()
        return True, "Dodano plik"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def usun_zalacznik(id_zalacznik):
    """Usuwa pojedynczy plik."""
    db = get_db_session()
    try:
        plik = db.query(Zalacznik).filter(Zalacznik.IDZalacznik == id_zalacznik).first()
        if plik:
            db.delete(plik)
            db.commit()
    finally:
        db.close()

# ==============================================================================
# 🛠️ 8. ADMINISTRACJA (DODATKI DO CRUD.PY)
# ==============================================================================

# --- ZARZĄDZANIE UŻYTKOWNIKAMI ---

def pobierz_wszystkich_uzytkownikow():
    """Zwraca DataFrame z listą użytkowników systemu."""
    db = get_db_session()
    try:
        # Pobieramy też rolę z tabeli OSOBA jeśli jest powiązanie (opcjonalne)
        q = db.query(Uzytkownik.IDUser, Uzytkownik.LoginName, Uzytkownik.Email, Uzytkownik.Rola, Uzytkownik.CzyAktywny)
        df = pd.read_sql(q.statement, db.bind)
        return df
    finally:
        db.close()

def zmien_status_uzytkownika(id_user, obecny_status):
    """Blokuje lub odblokowuje konto."""
    db = get_db_session()
    try:
        nowy_status = not bool(obecny_status)
        db.query(Uzytkownik).filter(Uzytkownik.IDUser == id_user).update({Uzytkownik.CzyAktywny: nowy_status})
        db.commit()
    finally:
        db.close()

def zmien_haslo_uzytkownika(login, nowe_haslo_plain):
    """Resetuje hasło użytkownika (Admin force reset)."""
    db = get_db_session()
    try:
        nowy_hash = hash_password(nowe_haslo_plain)
        db.query(Uzytkownik).filter(Uzytkownik.LoginName == login).update({Uzytkownik.HasloHash: nowy_hash})
        db.commit()
    finally:
        db.close()

def usun_uzytkownika(id_user):
    """Usuwa konto systemowe."""
    db = get_db_session()
    try:
        db.query(Uzytkownik).filter(Uzytkownik.IDUser == id_user).delete()
        db.commit()
    finally:
        db.close()

# --- ZARZĄDZANIE SŁOWNIKAMI ---

def dodaj_wartosc_slownika(typ_slownika, wartosc):
    """
    Dodaje wartość do odpowiedniej tabeli słownikowej.
    typ_slownika: 'gatunek', 'status', 'kategoria'
    """
    db = get_db_session()
    model_map = {
        'gatunek': SlownikGatunek,
        'status': SlownikStatus,
        'kategoria': SlownikKategoria
    }
    try:
        Model = model_map.get(typ_slownika)
        if Model:
            db.add(Model(Wartosc=wartosc))
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

def usun_wartosc_slownika(typ_slownika, wartosc):
    """Usuwa wartość ze słownika."""
    db = get_db_session()
    model_map = {
        'gatunek': SlownikGatunek,
        'status': SlownikStatus,
        'kategoria': SlownikKategoria
    }
    try:
        Model = model_map.get(typ_slownika)
        if Model:
            db.query(Model).filter(Model.Wartosc == wartosc).delete()
            db.commit()
    finally:
        db.close()
# ==============================================================================
# KONFIGURACJA ALERTÓW (DODATEK DO ADMINA)
# ==============================================================================

def pobierz_konfiguracje_alertow():
    """Pobiera tabelę reguł alertów do edycji."""
    db = get_db_session()
    try:
        q = db.query(KonfiguracjaAlerty)
        # Używamy pandas do łatwego wyświetlenia w st.data_editor
        df = pd.read_sql(q.statement, db.bind)
        return df
    finally:
        db.close()

def zapisz_konfiguracje_alertow(edited_df):
    """Zapisuje zmiany z edytora tabeli (Data Editor)."""
    db = get_db_session()
    try:
        # Iterujemy po wierszach z edytora i aktualizujemy bazę
        for index, row in edited_df.iterrows():
            db.query(KonfiguracjaAlerty).filter(KonfiguracjaAlerty.KodPola == row['KodPola']).update({
                KonfiguracjaAlerty.Etykieta: row['Etykieta'],
                KonfiguracjaAlerty.DniWaznosci: row['DniWaznosci'],
                KonfiguracjaAlerty.CzyAktywny: bool(row['CzyAktywny']) # Upewniamy się, że to boolean
            })
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Błąd zapisu alertów: {e}")
        return False
    finally:
        db.close()