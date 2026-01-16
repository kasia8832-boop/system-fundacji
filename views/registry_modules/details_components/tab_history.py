"""
KOMPONENT KARTY: ZAKŁADKA 'HISTORIA'
------------------------------------
Zarządza widokiem historii medycznej i behawioralnej.
Wersja 2.0: Dostosowana do nowego CRUD.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import time
import crud
from views.registry_modules.details_components import event_details

# --- OKNO DIALOGOWE DO USUWANIA ---
@st.dialog("🚨 Usuwanie zdarzenia")
def potwierdz_usuniecie_z_listy(id_historia):
    st.write("Czy na pewno chcesz usunąć ten wpis?")
    st.warning("Zostanie on usunięty wraz ze wszystkimi załącznikami.")
    
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Tak, usuń", type="primary", use_container_width=True):
            ok, msg = crud.usun_wpis_historii(id_historia)
            if ok:
                st.success("Usunięto.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(f"Błąd: {msg}")
            
    with col_no:
        if st.button("Anuluj", use_container_width=True):
            st.rerun()

# --- GŁÓWNA FUNKCJA ---
def render_tab(id_zw):
    # Inicjalizacja
    if 'active_history_event_id' not in st.session_state:
        st.session_state.active_history_event_id = None

    # TRYB 1: SZCZEGÓŁY (Sub-view)
    if st.session_state.active_history_event_id is not None:
        event_details.render_event_details(st.session_state.active_history_event_id)
        return

    # TRYB 2: LISTA (Main-view)
    
    # --- 1. Formularz Dodawania ---
    with st.expander("➕ Dodaj nowe zdarzenie", expanded=False):
        with st.form("new_history_entry_advanced"):
            st.write("Nowy wpis do historii")
            c1, c2 = st.columns(2)
            
            # CRUD: get_dictionary
            sl_k = crud.get_dictionary("SLOWNIK_KATEGORIE") # Sprawdź nazwę słownika w bazie!
            if not sl_k: sl_k = ["Wizyta", "Zabieg", "Inne"]
            
            kt = c1.selectbox("Typ zdarzenia", sl_k)
            dt = c2.date_input("Data zdarzenia", date.today())
            
            # CRUD: get_all_people (bo historię tworzą Osoby, np. Wolontariusze)
            dfa = crud.get_all_people()
            
            amp = {}
            if not dfa.empty:
                amp = {f"{x['Imie']} {x['Nazwisko']}": x['ID_Osoba'] for i,x in dfa.iterrows()}
            
            # Próba domyślnego wyboru zalogowanego usera (jeśli nazwa pasuje)
            current_user = st.session_state.get('user_name', '')
            def_idx = 0
            # Proste dopasowanie po nazwie (User == Imie Osoby) - opcjonalne
            possible_match = [k for k in amp.keys() if current_user in k]
            if possible_match:
                 def_idx = list(amp.keys()).index(possible_match[0])
            
            asu = st.selectbox("Autor", list(amp.keys()), index=def_idx)
            de = st.text_area("Opis zdarzenia")
            
            pliki_startowe = st.file_uploader("Załączniki (PDF, JPG)", accept_multiple_files=True)

            if st.form_submit_button("Zapisz zdarzenie", type="primary"):
                # Pobranie ID autora z mapy
                id_autora = amp.get(asu)
                
                # Dodanie wpisu (nowy CRUD)
                new_id = crud.dodaj_wpis_historii(id_zw, id_autora, dt, kt, de)
                
                # Dodanie załączników
                if pliki_startowe and new_id:
                    for f in pliki_startowe:
                        crud.dodaj_zalacznik(new_id, f)
                        
                st.success("Dodano wpis!")
                time.sleep(1)
                st.rerun()

    # --- 2. Filtry ---
    with st.expander("🔍 Filtrowanie historii", expanded=True):
        c1, c2 = st.columns(2)
        # Ponowne pobranie słownika
        sl_kat = crud.get_dictionary("SLOWNIK_KATEGORIE")
        if not sl_kat: sl_kat = ["Wizyta", "Zabieg", "Inne"]
        
        filter_kat = c1.multiselect("Kategoria", sl_kat, default=[]) # Default empty = pokaż wszystko
        filter_data_od = c2.date_input("Data od", date(2020, 1, 1))
        
    # --- 3. Lista ---
    # Funkcja pobierz_historie_zdarzen została zachowana w nowym CRUD
    df_h = crud.pobierz_historie_zdarzen(id_zw)
    
    if not df_h.empty:
        df_h['DataZdarzenia'] = pd.to_datetime(df_h['DataZdarzenia'])
        
        # Filtrowanie
        mask = df_h['DataZdarzenia'].dt.date >= filter_data_od
        if filter_kat:
            mask = mask & df_h['Kategoria'].isin(filter_kat)
            
        df_filtered = df_h.loc[mask].sort_values(by='DataZdarzenia', ascending=False)
        
        for index, row in df_filtered.iterrows():
            with st.container(border=True):
                c_date, c_info, c_details, c_del = st.columns([2, 4, 2, 1])
                
                with c_date:
                    st.write(f"📅 **{row['DataZdarzenia'].strftime('%Y-%m-%d')}**")
                    st.caption(row['Kategoria'])
                
                with c_info:
                    opis = row['Opis']
                    if len(opis) > 60: opis = opis[:60] + "..."
                    st.write(opis)
                    st.caption(f"Autor: {row['Autor']}")
                    
                with c_details:
                    if st.button("Szczegóły", key=f"hist_{row['ID_Historia']}", use_container_width=True):
                        st.session_state.active_history_event_id = row['ID_Historia']
                        st.rerun()
                
                with c_del:
                    if st.button("🗑️", key=f"del_list_{row['ID_Historia']}"):
                        potwierdz_usuniecie_z_listy(row['ID_Historia'])

    else:
        st.info("Brak wpisów w historii.")