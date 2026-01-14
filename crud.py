# crud.py
import streamlit as st
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from database import run_query, run_command

# ==========================
# 1. ZWIERZĘTA
# ==========================
def pobierz_zwierzeta_filtrowane(gatunki, statusy, szukaj_tekst):
    query = "SELECT * FROM ZWIERZE WHERE 1=1"
    params = []
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
    # SQLite: używamy || do łączenia stringów zamiast +
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
# 2. HISTORIA I OSOBY
# ==========================
def pobierz_historie_zdarzen(id_zw):
    # SQLite: || zamiast +
    query = """SELECT z.DataZdarzenia, z.Kategoria, z.Opis, o.Imie || ' ' || o.Nazwisko as Autor
                FROM OS_CZASU_ZDARZENIE z LEFT JOIN OSOBA o ON z.ID_Autor = o.ID_Osoba
                WHERE z.ID_Zwierze = ? ORDER BY z.DataZdarzenia DESC"""
    return run_query(query, (id_zw,))

def dodaj_wpis_historii(id_zw, id_autora, data, kategoria, opis):
    return run_command("INSERT INTO OS_CZASU_ZDARZENIE (ID_Zwierze, ID_Autor, DataZdarzenia, Kategoria, Opis) VALUES (?, ?, ?, ?, ?)", 
                       (id_zw, id_autora, data, kategoria, opis))

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
# 3. GALERIA (NOWOŚĆ)
# ==========================
def pobierz_galerie(id_zw):
    return run_query("SELECT * FROM ZWIERZE_GALERIA WHERE ID_Zwierze = ? ORDER BY ID_Zdjecie DESC", (id_zw,))

def dodaj_zdjecie_galerii(id_zw, url, opis):
    return run_command("INSERT INTO ZWIERZE_GALERIA (ID_Zwierze, ZdjecieURL, Opis) VALUES (?, ?, ?)", (id_zw, url, opis))

# ==========================
# 4. SŁOWNIKI
# ==========================
@st.cache_data(ttl=600)
def pobierz_liste_slownika(nazwa_tabeli):
    whitelist = ["SLOWNIK_GATUNEK", "SLOWNIK_STATUS", "SLOWNIK_ZRODLO", "SLOWNIK_KATEGORIA"]
    if nazwa_tabeli not in whitelist: return []
    df = run_query(f"SELECT Wartosc FROM {nazwa_tabeli} ORDER BY Wartosc")
    return df['Wartosc'].tolist() if not df.empty else []

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