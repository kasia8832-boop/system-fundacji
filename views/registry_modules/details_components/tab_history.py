"""
KOMPONENT KARTY: ZAKŁADKA 'HISTORIA'
Wersja 3.1: Fix przycisku szczegółów (obsługa IDHistoria).
"""
import streamlit as st
import pandas as pd
from datetime import date
import time
import crud
from views.registry_modules.details_components import event_details
from models import Uzytkownik 

@st.dialog("🚨 Usuwanie zdarzenia")
def potwierdz_usuniecie_z_listy(id_historia):
    st.write("Czy na pewno chcesz usunąć ten wpis?")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Tak, usuń", type="primary", use_container_width=True):
            ok, msg = crud.usun_wpis_historii(id_historia)
            if ok:
                st.success("Usunięto.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(msg)
    with col_no:
        if st.button("Anuluj", use_container_width=True):
            st.rerun()

def render_tab(id_zw):
    # Inicjalizacja stanu aktywnego zdarzenia
    if 'active_history_event_id' not in st.session_state:
        st.session_state.active_history_event_id = None

    # --- TRYB 1: SZCZEGÓŁY ZDARZENIA (Sub-view) ---
    if st.session_state.active_history_event_id is not None:
        # Jeśli wybrano konkretne zdarzenie, pokazujemy jego szczegóły
        event_details.render_event_details(st.session_state.active_history_event_id)
        return

    # --- TRYB 2: LISTA ZDARZEŃ (Main-view) ---
    
    # 1. Dodawanie nowego wpisu
    with st.expander("➕ Dodaj nowe zdarzenie", expanded=False):
        with st.form("new_history_entry_advanced"):
            c1, c2 = st.columns(2)
            
            # Pobieramy kategorie
            try:
                sl_kat = crud.pobierz_slownik("kategoria")
            except:
                sl_kat = []
            if not sl_kat: sl_kat = ["Wizyta", "Zabieg", "Inne"]
            
            kt = c1.selectbox("Typ zdarzenia", sl_kat)
            dt = c2.date_input("Data zdarzenia", date.today())
            de = st.text_area("Opis zdarzenia")
            pliki = st.file_uploader("Załączniki", accept_multiple_files=True)

            if st.form_submit_button("Zapisz", type="primary"):
                # Pobieramy ID zalogowanego usera
                db = crud.get_db_session()
                user = db.query(Uzytkownik).filter(Uzytkownik.LoginName == st.session_state.user_name).first()
                my_id = user.IDUser if user else None
                db.close()

                if my_id:
                    new_id = crud.dodaj_wpis_historii(id_zw, my_id, kt, de)
                    if pliki and new_id:
                        for f in pliki:
                            crud.dodaj_zalacznik(new_id, f)
                    st.success("Dodano wpis!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Błąd: Nie rozpoznano zalogowanego użytkownika.")

    # 2. Filtry
    with st.expander("🔍 Filtry", expanded=False):
        # Ponowne pobranie słownika dla filtrów
        try:
            opcje_kat = crud.pobierz_slownik("kategoria") or ["Wizyta", "Zabieg"]
        except:
            opcje_kat = ["Wizyta", "Zabieg"]
            
        f_kat = st.multiselect("Filtruj kategorię", opcje_kat)

    # 3. Wyświetlanie listy
    df = crud.pobierz_historie(id_zw)
    
    if not df.empty:
        # Konwersja daty (SQLite zwraca string)
        df['DataZdarzenia'] = pd.to_datetime(df['DataZdarzenia'])
        
        if f_kat:
            df = df[df['Kategoria'].isin(f_kat)]
            
        for _, row in df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 5, 2])
                
                # Kolumna 1: Data i Typ
                c1.write(f"**{row['DataZdarzenia'].strftime('%Y-%m-%d')}**")
                c1.caption(row['Kategoria'])
                
                # Kolumna 2: Opis i Autor
                c2.write(row['Opis'])
                c2.caption(f"Autor: {row.get('Autor', 'System')}")
                
                # Kolumna 3: Przyciski
                with c3:
                    # Teraz mamy pewność, że IDHistoria jest w row, bo poprawiliśmy crud.py
                    id_hist = row['IDHistoria']
                    
                    if st.button("Szczegóły / Pliki", key=f"btn_hist_{id_hist}", use_container_width=True):
                        st.session_state.active_history_event_id = int(id_hist)
                        st.rerun()
    else:
        st.info("Brak wpisów w historii.")