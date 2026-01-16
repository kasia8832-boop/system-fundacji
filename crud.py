"""
MODUŁ: CRUD (Create, Read, Update, Delete)
------------------------------------------
Warstwa dostępu do danych (Data Access Layer).
Wersja FINALNA: Obsługuje v2.0 bazy, w tym:
- Nową tabelę UZYTKOWNIK
- Reset hasła (Token)
- Adopcję tekstową (String)
- Zdjęcia (BLOB)
- Alerty medyczne (Kleszcze)
"""
import sqlite3
import pandas as pd
from datetime import datetime, date
import hashlib
import os
import random  # Niezbędne do generowania kodu resetu

# --- KONFIGURACJA BAZY DANYCH ---
DB_FILE = "fundacja.db"

def create_connection():
    """Tworzy połączenie do bazy SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except Exception as e:
        print(f"Błąd połączenia z bazą: {e}")
    return conn

# ==========================
# 1. UŻYTKOWNICY (LOGIN & DOSTĘP)
# ==========================
def verify_user(login_input, password):
    """
    Logowanie oparte na nowej tabeli UZYTKOWNIK.
    login_input = LoginName.
    """
    conn = create_connection()
    c = conn.cursor()
    
    # Pobieramy dane użytkownika
    c.execute("SELECT HasloHash, Rola, ID_User, LoginName FROM UZYTKOWNIK WHERE LoginName = ? AND CzyAktywny = 1", (login_input,))
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_hash = result[0]
        role = result[1]
        user_name = result[3]
        
        # Weryfikacja hasła (PBKDF2 SHA256)
        input_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            b'salt_fundacja', 
            100000
        ).hex()
        
        if stored_hash == input_hash:
            return role, user_name
            
    return None, None

def create_user(login_name, email, password, role):
    """Rejestracja nowego użytkownika systemowego."""
    conn = create_connection()
    c = conn.cursor()
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        b'salt_fundacja', 
        100000
    ).hex()
    
    try:
        c.execute("""
            INSERT INTO UZYTKOWNIK (LoginName, Email, HasloHash, Rola, CzyAktywny)
            VALUES (?, ?, ?, ?, 1)
        """, (login_name, email, password_hash, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Login zajęty
    finally:
        conn.close()

def change_user_password(login_name, new_password):
    """Zmiana hasła (np. przez Admina)."""
    conn = create_connection()
    c = conn.cursor()
    
    new_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        new_password.encode('utf-8'), 
        b'salt_fundacja', 
        100000
    ).hex()
    
    c.execute("UPDATE UZYTKOWNIK SET HasloHash = ? WHERE LoginName = ?", (new_hash, login_name))
    conn.commit()
    conn.close()
    return True

# ==========================
# 2. ZWIERZĘTA (REJESTR)
# ==========================
def add_animal(imie, gatunek, plec, status):
    """Dodaje zwierzę. DataPrzyjecia ustawiana automatycznie na dzisiaj."""
    conn = create_connection()
    c = conn.cursor()
    
    dzis = date.today().strftime("%Y-%m-%d")
    
    c.execute("""
        INSERT INTO ZWIERZE (Imie, Gatunek, Plec, StatusZwierzecia, DataPrzyjecia)
        VALUES (?, ?, ?, ?, ?)
    """, (imie, gatunek, plec, status, dzis))
    
    new_id = c.lastrowid
    
    # Tworzymy pusty profil medyczny od razu
    c.execute("INSERT INTO PROFIL_MEDYCZNY (ID_Zwierze) VALUES (?)", (new_id,))
    
    conn.commit()
    conn.close()
    return new_id

def get_all_animals_df():
    """Pobiera listę zwierząt do tabeli głównej."""
    conn = create_connection()
    df = pd.read_sql_query("SELECT ID_Zwierze, Imie, Gatunek, Rasa, StatusZwierzecia, NrChip, DataPrzyjecia FROM ZWIERZE", conn)
    conn.close()
    return df

def get_animal_details(id_zwierze):
    conn = create_connection()
    # SELECT * pobierze też nowe kolumny DaneAdoptujacego i DataAdopcji
    df = pd.read_sql_query("SELECT * FROM ZWIERZE WHERE ID_Zwierze = ?", conn, params=(id_zwierze,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def update_animal_basic(id_zwierze, imie, gatunek, rasa, plec, data_ur, wiek_opis, status, chip, opis, data_przyjecia):
    """Aktualizacja danych podstawowych."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE ZWIERZE 
        SET Imie=?, Gatunek=?, Rasa=?, Plec=?, DataUrodzenia=?, WiekOpisowy=?, StatusZwierzecia=?, NrChip=?, Opis=?, DataPrzyjecia=?
        WHERE ID_Zwierze=?
    """, (imie, gatunek, rasa, plec, data_ur, wiek_opis, status, chip, opis, data_przyjecia, id_zwierze))
    conn.commit()
    conn.close()

def update_animal_photo(id_zwierze, photo_bytes):
    """Aktualizacja zdjęcia (BLOB)."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE ZWIERZE SET Zdjecie=? WHERE ID_Zwierze=?", (photo_bytes, id_zwierze))
    conn.commit()
    conn.close()

def adoptuj_zwierze(id_zwierze, dane_osoby, data_adopcji):
    """
    Finalizuje adopcję: 
    1. Zmienia status na 'Adoptowany'
    2. Zapisuje dane osoby (string) i datę.
    """
    conn = create_connection()
    c = conn.cursor()
    
    try:
        c.execute("""
            UPDATE ZWIERZE 
            SET StatusZwierzecia = 'Adoptowany', 
                DaneAdoptujacego = ?, 
                DataAdopcji = ? 
            WHERE ID_Zwierze = ?
        """, (dane_osoby, data_adopcji, id_zwierze))
        conn.commit()
        return True
    except Exception as e:
        print(f"Błąd adopcji: {e}")
        return False
    finally:
        conn.close()

# ==========================
# 3. PROFIL MEDYCZNY
# ==========================
def get_medical_profile(id_zwierze):
    """Pobiera profil medyczny (w tym nowe pole OchronaKleszczeDo)."""
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM PROFIL_MEDYCZNY WHERE ID_Zwierze = ?", conn, params=(id_zwierze,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def update_medical_profile(id_zwierze, wscieklizna, zakazne, odrobaczenie, kastracja, kleszcze_do, opis):
    """Aktualizacja medyczna."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE PROFIL_MEDYCZNY 
        SET SzczepienieWscieklizna=?, SzczepienieZakazne=?, Odrobaczenie=?, DataKastracji=?, OchronaKleszczeDo=?, OpisZdrowia=?
        WHERE ID_Zwierze=?
    """, (wscieklizna, zakazne, odrobaczenie, kastracja, kleszcze_do, opis, id_zwierze))
    conn.commit()
    conn.close()

def add_medical_event(id_zwierze, data, typ, opis):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO HISTORIA_MEDYCZNA (ID_Zwierze, DataZdarzenia, TypZdarzenia, Opis) VALUES (?, ?, ?, ?)",
              (id_zwierze, data, typ, opis))
    conn.commit()
    conn.close()

def get_medical_history(id_zwierze):
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM HISTORIA_MEDYCZNA WHERE ID_Zwierze=? ORDER BY DataZdarzenia DESC", conn, params=(id_zwierze,))
    conn.close()
    return df

# ==========================
# 4. SŁOWNIKI
# ==========================
def get_dictionary(table_name):
    conn = create_connection()
    try:
        df = pd.read_sql_query(f"SELECT Wartosc FROM {table_name} ORDER BY Wartosc", conn)
        return df['Wartosc'].tolist()
    except:
        return []
    finally:
        conn.close()

def add_dict_value(table_name, value):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute(f"INSERT INTO {table_name} (Wartosc) VALUES (?)", (value,))
        conn.commit()
    except:
        pass
    finally:
        conn.close()

def delete_dict_value(table_name, value):
    conn = create_connection()
    c = conn.cursor()
    c.execute(f"DELETE FROM {table_name} WHERE Wartosc=?", (value,))
    conn.commit()
    conn.close()

# ==========================
# 5. OSOBY I ADMIN
# ==========================
def get_all_users():
    """Pobiera listę użytkowników systemowych."""
    conn = create_connection()
    df = pd.read_sql_query("SELECT ID_User, LoginName, Email, Rola, CzyAktywny FROM UZYTKOWNIK", conn)
    conn.close()
    return df

def toggle_user_status(id_user, current_status):
    conn = create_connection()
    c = conn.cursor()
    new_status = 0 if current_status == 1 else 1
    c.execute("UPDATE UZYTKOWNIK SET CzyAktywny = ? WHERE ID_User = ?", (new_status, id_user))
    conn.commit()
    conn.close()

def delete_user(id_user):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM UZYTKOWNIK WHERE ID_User = ?", (id_user,))
    conn.commit()
    conn.close()

def get_all_people():
    conn = create_connection()
    df = pd.read_sql_query("SELECT ID_Osoba, Imie, Nazwisko, Rola, Telefon, Email, Miasto, DataRejestracji FROM OSOBA", conn)
    conn.close()
    return df

def add_person(imie, nazwisko, rola, telefon, email, miasto):
    conn = create_connection()
    c = conn.cursor()
    dzis = date.today().strftime("%Y-%m-%d")
    c.execute("""
        INSERT INTO OSOBA (Imie, Nazwisko, Rola, Telefon, Email, Miasto, DataRejestracji)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (imie, nazwisko, rola, telefon, email, miasto, dzis))
    conn.commit()
    conn.close()

def delete_person(id_osoba):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM OSOBA WHERE ID_Osoba = ?", (id_osoba,))
    conn.commit()
    conn.close()

# ==========================
# 6. RESET HASŁA (NAPRAWIONE)
# ==========================
def inicjuj_reset_hasla(email_login):
    """
    Generuje kod i zapisuje go w bazie (kolumna ResetToken).
    """
    conn = create_connection()
    c = conn.cursor()
    
    # Sprawdź czy user istnieje
    c.execute("SELECT ID_User FROM UZYTKOWNIK WHERE LoginName = ?", (email_login,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return False, "Nie znaleziono użytkownika o takim loginie."
    
    # Generuj kod
    kod = str(random.randint(100000, 999999))
    
    try:
        # UWAGA: Upewnij się, że masz kolumnę ResetToken w bazie!
        # Jeśli nie, puść skrypt add_reset_token.py
        c.execute("UPDATE UZYTKOWNIK SET ResetToken = ? WHERE LoginName = ?", (kod, email_login))
        conn.commit()
        conn.close()
        return True, kod
    except Exception as e:
        conn.close()
        return False, f"Błąd bazy: {e}"

def finalizuj_reset_hasla(email_login, kod_uzytkownika, nowe_haslo):
    """
    Weryfikuje kod i zmienia hasło.
    """
    conn = create_connection()
    c = conn.cursor()
    
    c.execute("SELECT ResetToken FROM UZYTKOWNIK WHERE LoginName = ?", (email_login,))
    row = c.fetchone()
    
    if not row or row[0] != kod_uzytkownika:
        conn.close()
        return False, "Nieprawidłowy kod weryfikacyjny."
    
    # Kod poprawny - haszujemy i zmieniamy
    new_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        nowe_haslo.encode('utf-8'), 
        b'salt_fundacja', 
        100000
    ).hex()

    try:
        c.execute("""
            UPDATE UZYTKOWNIK 
            SET HasloHash = ?, ResetToken = NULL 
            WHERE LoginName = ?
        """, (new_hash, email_login))
        conn.commit()
        return True, "Hasło zmienione."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ==========================
# 7. POWIADOMIENIA (ALERTY)
# ==========================
def pobierz_konfiguracje_alertow():
    conn = create_connection()
    try:
        return pd.read_sql_query("SELECT * FROM KONFIGURACJA_ALERTY", conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def zapisz_konfiguracje_alertow(df_edited):
    conn = create_connection()
    c = conn.cursor()
    try:
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
    Skaner alertów uwzględniający nowe pole OchronaKleszczeDo.
    """
    conn = create_connection()
    
    # 1. Pobieramy konfigurację
    try:
        reguly = pd.read_sql_query("SELECT * FROM KONFIGURACJA_ALERTY WHERE CzyAktywny = 1", conn)
    except:
        conn.close()
        return []

    if reguly.empty:
        conn.close()
        return []

    # 2. Budujemy zapytanie SQL dynamicznie
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
        for _, regula in reguly.iterrows():
            pole = regula['KodPola']
            limit_dni = regula['DniWaznosci']
            etykieta = regula['Etykieta']
            
            data_db_raw = row_zwierze.get(pole)
            
            if not data_db_raw:
                continue
            
            try:
                if isinstance(data_db_raw, str):
                    data_db = datetime.strptime(data_db_raw, '%Y-%m-%d').date()
                else:
                    data_db = data_db_raw.date()

                # --- OBSŁUGA DLA KLESZCZY (Data wygaśnięcia) ---
                if pole == 'OchronaKleszczeDo':
                    dni_po_terminie = (dzis - data_db).days
                    if dni_po_terminie > 0:
                        alerty.append({
                            "id": row_zwierze['ID_Zwierze'],
                            "imie": row_zwierze['Imie'],
                            "chip": row_zwierze['NrChip'],
                            "typ": "Wygasła Ochrona",
                            "komunikat": f"{etykieta}: wygasła {data_db} ({dni_po_terminie} dni temu)"
                        })
                
                # --- OBSŁUGA SZCZEPIEŃ (Data zabiegu + Ważność) ---
                else:
                    delta = (dzis - data_db).days
                    if delta > limit_dni:
                        alerty.append({
                            "id": row_zwierze['ID_Zwierze'],
                            "imie": row_zwierze['Imie'],
                            "chip": row_zwierze['NrChip'],
                            "typ": "Przeterminowane",
                            "komunikat": f"{etykieta}: upłynęło {delta} dni (Limit: {limit_dni})"
                        })
                        
            except Exception as e:
                pass 

    return alerty

# ==========================
# 8. HISTORIA I ZAŁĄCZNIKI
# ==========================
def dodaj_zalacznik(id_historia, plik):
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
        return False, str(e)
    finally:
        conn.close()

def pobierz_zalaczniki(id_historia):
    conn = create_connection()
    try:
        df = pd.read_sql_query(f"""
            SELECT ID_Zalacznik, NazwaPliku, TypPliku, length(DaneBLOB) as RozmiarBajt, DataDodania 
            FROM ZALACZNIKI 
            WHERE ID_Historia = {id_historia}
        """, conn)
    except:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def pobierz_plik_content(id_zalacznik):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT NazwaPliku, DaneBLOB, TypPliku FROM ZALACZNIKI WHERE ID_Zalacznik = ?", (id_zalacznik,))
        row = c.fetchone()
    except:
        row = None
    finally:
        conn.close()
    return row

def usun_zalacznik(id_zalacznik):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM ZALACZNIKI WHERE ID_Zalacznik = ?", (id_zalacznik,))
        conn.commit()
    except:
        pass
    finally:
        conn.close()
    
def dodaj_wpis_historii(id_zwierze, id_autor, data, kategoria, opis):
    conn = create_connection()
    c = conn.cursor()
    new_id = None
    try:
        c.execute("""
            INSERT INTO HISTORIA_ZDARZEN (ID_Zwierze, ID_Osoba, DataZdarzenia, Kategoria, Opis)
            VALUES (?, ?, ?, ?, ?)
        """, (id_zwierze, id_autor, data, kategoria, opis))
        new_id = c.lastrowid
        conn.commit()
    except Exception as e:
        print(f"Błąd dodawania historii: {e}")
    finally:
        conn.close()
    return new_id

def pobierz_historie_zdarzen(id_zwierze):
    conn = create_connection()
    query = f"""
        SELECT h.ID_Historia, h.DataZdarzenia, h.Kategoria, h.Opis, 
               o.Imie || ' ' || o.Nazwisko as Autor
        FROM HISTORIA_ZDARZEN h
        LEFT JOIN OSOBA o ON h.ID_Osoba = o.ID_Osoba
        WHERE h.ID_Zwierze = {id_zwierze}
        ORDER BY h.DataZdarzenia DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def usun_wpis_historii(id_historia):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM ZALACZNIKI WHERE ID_Historia = ?", (id_historia,))
        c.execute("DELETE FROM HISTORIA_ZDARZEN WHERE ID_Historia = ?", (id_historia,))
        conn.commit()
        return True, "Usunięto pomyślnie"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()