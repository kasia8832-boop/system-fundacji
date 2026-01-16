# crud.py
import sqlite3 # <--- NAPRAWIONO IMPORT (zamiast socket)
import streamlit as st
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
# Zakładam, że database.py nadal istnieje dla starszych funkcji
# Jeśli nie, trzeba by przepisać wszystko na sqlite3, ale na razie mieszamy
try:
    from database import run_query, run_command
except ImportError:
    # Fallback jeśli database.py nie działa, żeby kod się nie wywalił od razu
    pass 

# --- KONFIGURACJA BAZY DANYCH ---
DB_FILE = "fundacja.db"

def create_connection(address=DB_FILE):
    """
    Tworzy połączenie do bazy SQLite.
    Argument 'address' ma wartość domyślną, co naprawia błąd TypeError.
    """
    conn = None
    try:
        conn = sqlite3.connect(address)
    except Exception as e:
        print(f"Błąd połączenia z bazą: {e}")
    return conn

# ==========================
# 1. ZWIERZĘTA
# ==========================
def pobierz_zwierzeta_filtrowane(gatunki, statusy, szukaj_tekst, id_dt_only=None):
    """
    id_dt_only: Jeśli podane (int), zwraca zwierzęta tylko tego opiekuna.
    """
    query = "SELECT * FROM ZWIERZE WHERE 1=1"
    params = []
    
    # 1. Filtracja po DT (Najważniejsze dla bezpieczeństwa)
    if id_dt_only is not None:
        query += " AND ID_OpiekunTymczasowy = ?"
        params.append(id_dt_only)

    # 2. Reszta filtrów
    if gatunki:
        placeholders = ','.join('?' for _ in gatunki)
        query += f" AND Gatunek IN ({placeholders})"
        params.extend(gatunki)
    if statusy:
        placeholders = ','.join('?' for _ in statusy)
        query += f" AND StatusZwierzecia IN ({placeholders})"
        params.extend(statusy)
    if szukaj_tekst:
        query += " AND (Imie LIKE ? OR NrChip LIKE ?)"
        params.extend([f"%{szukaj_tekst}%", f"%{szukaj_tekst}%"])
    
    return run_query(query, params)

def pobierz_pelna_karte(id_zwierza):
    query = f"""
    SELECT z.*, pm.CzyKastrowany, pm.DataKastracji, pm.SzczepienieWscieklizna, 
           pm.SzczepienieZakazne, pm.Odrobaczenie, pm.UwagiMedyczne,
           o.Imie as DT_Imie, o.Nazwisko as DT_Nazwisko, o.Telefon as DT_Telefon, o.Email as DT_Email
    FROM ZWIERZE z
    LEFT JOIN PROFIL_MEDYCZNY pm ON z.ID_Zwierze = pm.ID_Zwierze
    LEFT JOIN OSOBA o ON z.ID_OpiekunTymczasowy = o.ID_Osoba
    WHERE z.ID_Zwierze = ?
    """
    return run_query(query, (id_zwierza,))

def pobierz_dane_do_edycji(id_zwierza):
    return pobierz_pelna_karte(id_zwierza)

def dodaj_zwierze(imie, gatunek, plec, chip, data_ur, status, zrodlo, olx, www, id_dt):
    chip_db = chip if chip != "" else None
    plec_db = 'M' if plec == "Samiec" else 'K'
    query = """
    INSERT INTO ZWIERZE (Imie, Gatunek, Plec, NrChip, DataUrodzenia, StatusZwierzecia, 
    ZrodloFinansowania, CzyOgloszenieOLX, CzyOgloszenieWWW, ID_OpiekunTymczasowy)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return run_command(query, (imie, gatunek, plec_db, chip_db, data_ur, status, zrodlo, olx, www, id_dt))

def zapisz_edycje_i_profil(id_zw, imie, chip, status, kastracja, data_kast, wsciek, zakazne, odrobacz, uwagi, img_url, yt_url):
    chip_db = chip if chip != "" else None
    
    run_command("UPDATE ZWIERZE SET Imie=?, NrChip=?, StatusZwierzecia=?, ZdjecieProfilowe=?, YouTubeURL=? WHERE ID_Zwierze=?", 
                (imie, chip_db, status, img_url, yt_url, id_zw))
    
    check = run_query(f"SELECT ID_Zwierze FROM PROFIL_MEDYCZNY WHERE ID_Zwierze=?", (id_zw,))
    kastracja_bit = 1 if kastracja else 0
    
    if not check.empty:
        sql = """UPDATE PROFIL_MEDYCZNY SET CzyKastrowany=?, DataKastracji=?, SzczepienieWscieklizna=?, 
                 SzczepienieZakazne=?, Odrobaczenie=?, UwagiMedyczne=? WHERE ID_Zwierze=?"""
        return run_command(sql, (kastracja_bit, data_kast, wsciek, zakazne, odrobacz, uwagi, id_zw))
    else:
        sql = """INSERT INTO PROFIL_MEDYCZNY (ID_Zwierze, CzyKastrowany, DataKastracji, SzczepienieWscieklizna, 
                 SzczepienieZakazne, Odrobaczenie, UwagiMedyczne) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        return run_command(sql, (id_zw, kastracja_bit, data_kast, wsciek, zakazne, odrobacz, uwagi))

def adoptuj_zwierze(id_zw, id_osoby, data_adopcji):
    query = "UPDATE ZWIERZE SET StatusZwierzecia='Adoptowany', ID_Adoptujacy=?, DataAdopcji=? WHERE ID_Zwierze=?"
    return run_command(query, (id_osoby, data_adopcji, id_zw))

# ==========================
# 2. OSOBY
# ==========================
def pobierz_id_osoby_po_emailu(email):
    """Zwraca ID_Osoba z tabeli OSOBA na podstawie emaila (dla DT)"""
    # Zakładamy, że email w systemie logowania = email w kartotece osób
    res = run_query("SELECT ID_Osoba FROM OSOBA WHERE Email = ?", (email,))
    if not res.empty:
        return res.iloc[0]['ID_Osoba']
    return None

@st.cache_data(ttl=60)
def pobierz_wszystkie_osoby():
    return run_query("SELECT * FROM OSOBA")

@st.cache_data(ttl=60)
def pobierz_liste_dt():
    return run_query("SELECT ID_Osoba, Imie, Nazwisko FROM OSOBA WHERE CzyJestDT = 1")

def dodaj_osobe(imie, nazwisko, telefon, email, miasto, ulica, czy_dt):
    dt_val = 1 if czy_dt else 0
    return run_command("INSERT INTO OSOBA (Imie, Nazwisko, Telefon, Email, AdresMiasto, AdresUlica, CzyJestDT) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (imie, nazwisko, telefon, email, miasto, ulica, dt_val))

# ==========================
# 3. GALERIA
# ==========================
def pobierz_galerie(id_zw):
    return run_query("SELECT * FROM ZWIERZE_GALERIA WHERE ID_Zwierze = ? ORDER BY ID_Zdjecie DESC", (id_zw,))

def dodaj_zdjecie_galerii(id_zw, url, opis):
    return run_command("INSERT INTO ZWIERZE_GALERIA (ID_Zwierze, ZdjecieURL, Opis) VALUES (?, ?, ?)", (id_zw, url, opis))

# ==========================
# 4. SŁOWNIKI
# ==========================
@st.cache_data(ttl=600)
# ==========================
# 4. SŁOWNIKI
# ==========================
@st.cache_data(ttl=60) # Zmniejszamy TTL, żeby zmiany były widoczne szybciej
def pobierz_liste_slownika(nazwa_tabeli):
    whitelist = ["SLOWNIK_GATUNEK", "SLOWNIK_STATUS", "SLOWNIK_ZRODLO", "SLOWNIK_KATEGORIA"]
    if nazwa_tabeli not in whitelist: return []
    df = run_query(f"SELECT Wartosc FROM {nazwa_tabeli} ORDER BY Wartosc")
    return df['Wartosc'].tolist() if not df.empty else []

def dodaj_element_slownika(nazwa_tabeli, wartosc):
    whitelist = ["SLOWNIK_GATUNEK", "SLOWNIK_STATUS", "SLOWNIK_ZRODLO", "SLOWNIK_KATEGORIA"]
    if nazwa_tabeli not in whitelist: return False, "Niedozwolona tabela"
    
    # Sprawdzenie czy już istnieje
    check = run_query(f"SELECT Wartosc FROM {nazwa_tabeli} WHERE Wartosc = ?", (wartosc,))
    if not check.empty:
        return False, "Taka wartość już istnieje."
        
    return run_command(f"INSERT INTO {nazwa_tabeli} (Wartosc) VALUES (?)", (wartosc,)), "Dodano pomyślnie"

def usun_element_slownika(nazwa_tabeli, wartosc):
    whitelist = ["SLOWNIK_GATUNEK", "SLOWNIK_STATUS", "SLOWNIK_ZRODLO", "SLOWNIK_KATEGORIA"]
    if nazwa_tabeli not in whitelist: return False, "Niedozwolona tabela"
    
    return run_command(f"DELETE FROM {nazwa_tabeli} WHERE Wartosc = ?", (wartosc,)), "Usunięto pomyślnie"

# ==========================
# 5. BEZPIECZEŃSTWO
# ==========================
def generuj_haslo_losowe(dlugosc=8):
    znaki = string.ascii_letters + string.digits
    return ''.join(random.choice(znaki) for i in range(dlugosc))

def hashuj_haslo(haslo_jawne):
    return generate_password_hash(haslo_jawne)

def weryfikuj_logowanie(email, haslo):
    query = "SELECT PasswordHash, Imie, Nazwisko, Role FROM SYSTEM_USER_APP WHERE Email = ? AND IsActive = 1"
    df = run_query(query, (email,))
    
    if df.empty:
        return False, None, None
    
    stored_hash = df.iloc[0]['PasswordHash']
    imie_nazwisko = f"{df.iloc[0]['Imie']} {df.iloc[0]['Nazwisko']}"
    rola = df.iloc[0]['Role']
    
    if check_password_hash(stored_hash, haslo):
        return True, imie_nazwisko, rola
    else:
        return False, None, None

def dodaj_uzytkownika_systemu(imie, nazwisko, email, rola="Wolontariusz"):
    check = run_query("SELECT ID FROM SYSTEM_USER_APP WHERE Email = ?", (email,))
    if not check.empty: return False, "Email zajęty"

    temp = generuj_haslo_losowe()
    hashed = hashuj_haslo(temp)

    query = "INSERT INTO SYSTEM_USER_APP (Imie, Nazwisko, Email, PasswordHash, Role) VALUES (?, ?, ?, ?, ?)"
    if run_command(query, (imie, nazwisko, email, hashed, rola)):
        return True, temp
    else: return False, "Błąd SQL"

def resetuj_haslo(email):
    check = run_query("SELECT ID FROM SYSTEM_USER_APP WHERE Email = ?", (email,))
    if check.empty: return False, "Nie znaleziono emaila"
    
    temp = generuj_haslo_losowe()
    hashed = hashuj_haslo(temp)
    
    if run_command("UPDATE SYSTEM_USER_APP SET PasswordHash = ? WHERE Email = ?", (hashed, email)):
        return True, temp
    return False, "Błąd SQL"

def pobierz_liste_uzytkownikow():
    return run_query("SELECT ID, Imie, Nazwisko, Email, Role, IsActive, DataUtworzenia FROM SYSTEM_USER_APP")

def zmien_role_uzytkownika(id_user, nowa_rola):
    return run_command("UPDATE SYSTEM_USER_APP SET Role = ? WHERE ID = ?", (nowa_rola, id_user))

# ==========================
# 6. HISTORIA I ZAŁĄCZNIKI (NOWE FUNKCJE)
# ==========================

# W pliku crud.py

def dodaj_zalacznik(id_historia, plik):
    """
    Zapisuje plik binarny w bazie danych.
    Zwraca: (True, "OK") lub (False, "Treść błędu")
    """
    conn = create_connection()
    c = conn.cursor()
    dane = plik.getvalue()
    
    try:
        c.execute("""
            INSERT INTO ZALACZNIKI (ID_Historia, NazwaPliku, TypPliku, DaneBLOB, DataDodania)
            VALUES (?, ?, ?, ?, DATE('now'))
        """, (id_historia, plik.name, plik.type, dane))
        conn.commit()
        return True, "OK"
    except Exception as e:
        return False, str(e) # Zwracamy treść błędu
    finally:
        conn.close()

def pobierz_zalaczniki(id_historia):
    """Pobiera listę załączników (bez danych BLOB dla szybkości listy)"""
    conn = create_connection()
    # Pobieramy ID, Nazwę i Rozmiar (długość BLOBa)
    try:
        df = pd.read_sql_query(f"""
            SELECT ID_Zalacznik, NazwaPliku, TypPliku, length(DaneBLOB) as RozmiarBajt, DataDodania 
            FROM ZALACZNIKI 
            WHERE ID_Historia = {id_historia}
        """, conn)
    except Exception as e:
        print(f"Błąd pobierania listy załączników: {e}")
        df = pd.DataFrame() # Zwróć pusty DF w razie błędu
    finally:
        conn.close()
    return df

def pobierz_plik_content(id_zalacznik):
    """Pobiera konkretny plik (binaria) do pobrania"""
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT NazwaPliku, DaneBLOB, TypPliku FROM ZALACZNIKI WHERE ID_Zalacznik = ?", (id_zalacznik,))
        row = c.fetchone()
    except Exception as e:
        print(f"Błąd pobierania treści pliku: {e}")
        row = None
    finally:
        conn.close()
    return row # (Nazwa, Dane, Typ)

def usun_zalacznik(id_zalacznik):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM ZALACZNIKI WHERE ID_Zalacznik = ?", (id_zalacznik,))
        conn.commit()
    except Exception as e:
        print(f"Błąd usuwania załącznika: {e}")
    finally:
        conn.close()
    
def dodaj_wpis_historii(id_zwierze, id_autor, data, kategoria, opis):
    """
    Dodaje wpis do historii i ZWRACA ID nowego wiersza.
    """
    conn = create_connection()
    c = conn.cursor()
    new_id = None
    try:
        # Zmieniono nazwę tabeli na nową: HISTORIA_ZDARZEN
        c.execute("""
            INSERT INTO HISTORIA_ZDARZEN (ID_Zwierze, ID_Osoba, DataZdarzenia, Kategoria, Opis)
            VALUES (?, ?, ?, ?, ?)
        """, (id_zwierze, id_autor, data, kategoria, opis))
        new_id = c.lastrowid # <-- WAŻNE: Pobieramy ID nowo utworzonego wpisu
        conn.commit()
    except Exception as e:
        print(f"Błąd dodawania historii: {e}")
    finally:
        conn.close()
    return new_id

def pobierz_historie_zdarzen(id_zwierze):
    """
    Pobiera historię zdarzeń. Funkcja korzysta z create_connection() 
    z domyślnym argumentem.
    """
    conn = create_connection()
    
    # Zmieniono nazwę tabeli na nową: HISTORIA_ZDARZEN
    query = f"""
        SELECT 
            h.ID_Historia, 
            h.DataZdarzenia, 
            h.Kategoria, 
            h.Opis, 
            o.Imie || ' ' || o.Nazwisko as Autor
        FROM HISTORIA_ZDARZEN h
        LEFT JOIN OSOBA o ON h.ID_Osoba = o.ID_Osoba
        WHERE h.ID_Zwierze = {id_zwierze}
        ORDER BY h.DataZdarzenia DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Błąd pobierania historii: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def usun_wpis_historii(id_historia):
    """
    Usuwa zdarzenie oraz wszystkie powiązane z nim załączniki.
    Transakcja zapewnia, że albo usunie się wszystko, albo nic.
    """
    conn = create_connection()
    c = conn.cursor()
    try:
        # 1. Najpierw usuwamy załączniki tego zdarzenia (CASCADE ręczne)
        c.execute("DELETE FROM ZALACZNIKI WHERE ID_Historia = ?", (id_historia,))
        
        # 2. Teraz usuwamy samo zdarzenie
        c.execute("DELETE FROM HISTORIA_ZDARZEN WHERE ID_Historia = ?", (id_historia,))
        
        conn.commit()
        return True, "Usunięto pomyślnie"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ==========================
# 7. RESET HASŁA (NOWE FUNKCJE)
# ==========================

def inicjuj_reset_hasla(email):
    """
    Sprawdza czy email istnieje. Jeśli tak - generuje kod, zapisuje w bazie i zwraca go.
    """
    # 1. Sprawdź czy user istnieje
    check = run_query("SELECT ID FROM SYSTEM_USER_APP WHERE Email = ?", (email,))
    if check.empty:
        return False, "Nie znaleziono takiego adresu email."
    
    # 2. Wygeneruj kod (6 cyfr)
    kod = str(random.randint(100000, 999999))
    
    # 3. Zapisz kod w bazie (wymaga kolumny ResetToken dodanej w create_db.py)
    sql = "UPDATE SYSTEM_USER_APP SET ResetToken = ? WHERE Email = ?"
    if run_command(sql, (kod, email)):
        return True, kod
    else:
        return False, "Błąd bazy danych."

def finalizuj_reset_hasla(email, podany_kod, nowe_haslo):
    """
    Sprawdza czy kod pasuje. Jeśli tak - zmienia hasło i czyści token.
    """
    # 1. Pobierz zapisany token
    res = run_query("SELECT ResetToken FROM SYSTEM_USER_APP WHERE Email = ?", (email,))
    
    if res.empty:
        return False, "Błąd użytkownika."
    
    zapisany_token = res.iloc[0]['ResetToken']
    
    # 2. Walidacja kodu
    if not zapisany_token:
        return False, "Brak aktywnego procesu resetu."
    
    # Konwersja na str, żeby uniknąć błędów typów
    if str(zapisany_token).strip() != str(podany_kod).strip():
        return False, "Nieprawidłowy kod resetujący."
    
    # 3. Zmiana hasła
    nowy_hash = hashuj_haslo(nowe_haslo)
    
    # Ustawiamy hasło i CZYŚCIMY token (żeby nie można go użyć drugi raz)
    sql = "UPDATE SYSTEM_USER_APP SET PasswordHash = ?, ResetToken = NULL WHERE Email = ?"
    if run_command(sql, (nowy_hash, email)):
        return True, "Hasło zostało zmienione."
    else:
        return False, "Błąd zapisu hasła."
# ==========================
# 8. POWIADOMIENIA I KONFIGURACJA
# ==========================
from datetime import datetime, date

def pobierz_konfiguracje_alertow():
    """Pobiera wszystkie reguły alertów do edycji w panelu Admina"""
    conn = create_connection()
    try:
        return pd.read_sql_query("SELECT * FROM KONFIGURACJA_ALERTY", conn)
    finally:
        conn.close()

def zapisz_konfiguracje_alertow(df_edited):
    """Zapisuje zmienione reguły z panelu Admina"""
    conn = create_connection()
    c = conn.cursor()
    try:
        # Iterujemy po dataframe i aktualizujemy rekordy
        for index, row in df_edited.iterrows():
            c.execute("""
                UPDATE KONFIGURACJA_ALERTY 
                SET Etykieta = ?, DniWaznosci = ?, CzyAktywny = ?
                WHERE KodPola = ?
            """, (row['Etykieta'], row['DniWaznosci'], row['CzyAktywny'], row['KodPola']))
        conn.commit()
        return True
    except Exception as e:
        print(f"Błąd zapisu configu: {e}")
        return False
    finally:
        conn.close()

def pobierz_alerty_medyczne():
    """
    Dynamiczna wersja skanera alertów.
    Pobiera reguły z bazy i sprawdza tylko aktywne pola.
    """
    conn = create_connection()
    
    # 1. Pobieramy konfigurację (tylko aktywne reguły)
    try:
        reguly = pd.read_sql_query("SELECT * FROM KONFIGURACJA_ALERTY WHERE CzyAktywny = 1", conn)
    except:
        conn.close()
        return [] # Jeśli tabela nie istnieje (zabezpieczenie)

    if reguly.empty:
        conn.close()
        return []

    # 2. Budujemy zapytanie SQL dynamicznie
    # Pobieramy zawsze podstawowe dane + kolumny zdefiniowane w konfiguracji
    kolumny_do_sprawdzenia = reguly['KodPola'].tolist()
    kolumny_sql = ", ".join([f"pm.{k}" for k in kolumny_do_sprawdzenia])
    
    query = f"""
        SELECT z.ID_Zwierze, z.Imie, z.NrChip, {kolumny_sql}
        FROM ZWIERZE z
        LEFT JOIN PROFIL_MEDYCZNY pm ON z.ID_Zwierze = pm.ID_Zwierze
        WHERE z.StatusZwierzecia NOT IN ('Adoptowany', 'Za Tęczowym Mostem')
    """
    
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Błąd zapytania alertów: {e}")
        conn.close()
        return []
    finally:
        conn.close()
    
    alerty = []
    dzis = date.today()
    
    if df.empty:
        return alerty

    # 3. Pętla sprawdzająca
    for index, row_zwierze in df.iterrows():
        
        # Dla każdego zwierzęcia sprawdzamy każdą aktywną regułę
        for _, regula in reguly.iterrows():
            pole = regula['KodPola']       # np. SzczepienieWscieklizna
            limit_dni = regula['DniWaznosci'] # np. 365
            etykieta = regula['Etykieta']  # np. Wścieklizna
            
            data_zabiegu_raw = row_zwierze[pole]
            
            # Logika sprawdzania daty
            if not data_zabiegu_raw:
                # Opcjonalnie: Możesz wyłączyć alerty dla pustych pól, jeśli wolisz
                alerty.append({
                    "id": row_zwierze['ID_Zwierze'],
                    "imie": row_zwierze['Imie'],
                    "chip": row_zwierze['NrChip'],
                    "typ": "Brak danych",
                    "komunikat": f"Brak wpisu: {etykieta}"
                })
                continue
            
            try:
                # Obsługa formatu daty (czasem pandas zwraca Timestamp, czasem str)
                if isinstance(data_zabiegu_raw, str):
                    data_zabiegu = datetime.strptime(data_zabiegu_raw, '%Y-%m-%d').date()
                else:
                    data_zabiegu = data_zabiegu_raw.date() # Jeśli to obiekt datetime/timestamp
                
                delta = (dzis - data_zabiegu).days
                
                if delta > limit_dni:
                    alerty.append({
                        "id": row_zwierze['ID_Zwierze'],
                        "imie": row_zwierze['Imie'],
                        "chip": row_zwierze['NrChip'],
                        "typ": "Przeterminowane",
                        "komunikat": f"{etykieta}: upłynęło {delta} dni (Limit: {limit_dni})"
                    })
            except Exception as e:
                pass # Ignorujemy błędy parsowania dat

    return alerty