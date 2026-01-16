"""
MODUŁ REJESTRU: EDYCJA DANYCH
-----------------------------
Formularz edycji danych zwierzęcia.
Wersja 2.0: Dostosowana do nowej bazy (DataPrzyjecia, Kleszcze) i rozdzielonego CRUD.
"""

import streamlit as st
import pandas as pd
import time
import crud
from datetime import datetime, date

def parse_date(date_obj):
    """Pomocnicza funkcja do bezpiecznej konwersji daty z bazy"""
    if not date_obj:
        return None
    try:
        # Jeśli to string (SQLite tak często zwraca)
        if isinstance(date_obj, str):
            return datetime.strptime(date_obj, "%Y-%m-%d").date()
        # Jeśli to timestamp/datetime
        return date_obj.date()
    except:
        return None

def render_edit():
    # Przycisk Anuluj
    if st.button("❌ Anuluj"): 
        st.session_state.view_mode = "details"
        st.rerun()
        
    st.header("✏️ Edycja Profilu")
    
    id_zw = int(st.session_state.active_animal_id)
    
    # 1. Pobieramy dane (Teraz są to dwie osobne funkcje w CRUD!)
    animal = crud.get_animal_details(id_zw)
    med = crud.get_medical_profile(id_zw)
    
    if animal is None or med is None:
        st.error("Błąd pobierania danych z bazy.")
        return

    # Słowniki do selectboxów
    try:
        sl_gat = crud.get_dictionary("SLOWNIK_GATUNKI")
        sl_stat = crud.get_dictionary("SLOWNIK_STATUSY")
    except:
        sl_gat = ["Pies", "Kot"]
        sl_stat = ["Do adopcji", "W trakcie leczenia"]

    # Tabs: Podstawowe i Medyczne (Multimedia wyrzucamy, bo URL do YouTube usunięty, a zdjęcia są w Details)
    tab_main, tab_med = st.tabs(["📋 Dane Podstawowe", "🏥 Dane Medyczne"])
    
    with st.form("ed_form"):
        # --- ZAKŁADKA 1: PODSTAWOWE ---
        with tab_main:
            c1, c2 = st.columns(2)
            with c1:
                ni = st.text_input("Imię", animal['Imie'])
                
                # Gatunek (zabezpieczenie indexu)
                idx_gat = sl_gat.index(animal['Gatunek']) if animal['Gatunek'] in sl_gat else 0
                ng = st.selectbox("Gatunek", sl_gat, index=idx_gat)
                
                nr = st.text_input("Rasa", animal['Rasa'] or "")
                
                # Data Przyjęcia (NOWE POLE)
                dp = st.date_input("Data Przyjęcia", parse_date(animal['DataPrzyjecia']))

            with c2:
                # Płeć
                opcje_plec = ["Samiec", "Samica", "Nieznana"]
                idx_plec = opcje_plec.index(animal['Plec']) if animal['Plec'] in opcje_plec else 0
                np_val = st.radio("Płeć", opcje_plec, index=idx_plec, horizontal=True)

                nc = st.text_input("Nr Chip", animal['NrChip'] or "")
                
                # Data Urodzenia
                du = st.date_input("Data Urodzenia", parse_date(animal['DataUrodzenia']))
                nw = st.text_input("Wiek (opis)", animal['WiekOpisowy'] or "")

                # Status
                idx_stat = sl_stat.index(animal['StatusZwierzecia']) if animal['StatusZwierzecia'] in sl_stat else 0
                ns = st.selectbox("Status", sl_stat, index=idx_stat)

            no = st.text_area("Opis ogólny", animal['Opis'] or "")

        # --- ZAKŁADKA 2: MEDYCZNE ---
        with tab_med:
            st.info("Daty ważności zabiegów")
            cm1, cm2 = st.columns(2)
            with cm1:
                w = st.date_input("Wścieklizna", parse_date(med['SzczepienieWscieklizna']))
                z = st.date_input("Zakaźne", parse_date(med['SzczepienieZakazne']))
            with cm2:
                o = st.date_input("Odrobaczenie", parse_date(med['Odrobaczenie']))
                
                # Ochrona Kleszcze (NOWE POLE)
                kl = st.date_input("🛡️ Kleszcze (Ważne do)", parse_date(med['OchronaKleszczeDo']))

            st.divider()
            dk = st.date_input("Data Kastracji", parse_date(med['DataKastracji']))
            
            # Opis medyczny (Zmieniona nazwa pola w bazie na OpisZdrowia)
            u = st.text_area("Opis Zdrowia / Uwagi Weterynarza", med['OpisZdrowia'] or "")
        
        # --- ZAPIS ---
        if st.form_submit_button("💾 Zapisz Zmiany", type="primary"):
            # Musimy wywołać DWIE funkcje update, bo tak jest w nowym CRUD
            
            # 1. Update podstawowy
            crud.update_animal_basic(
                id_zw, ni, ng, nr, np_val, du, nw, ns, nc, no, dp
            )
            
            # 2. Update medyczny
            crud.update_medical_profile(
                id_zw, w, z, o, dk, kl, u
            )
            
            st.success("Pomyślnie zaktualizowano profil!")
            time.sleep(1)
            st.session_state.view_mode = "details"
            st.rerun()