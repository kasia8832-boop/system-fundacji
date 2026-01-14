"""
KOMPONENT KARTY: ZAKŁADKA 'HISTORIA'
------------------------------------
Zarządza widokiem historii medycznej i behawioralnej.
Obsługuje dwa stany:
1. Lista zdarzeń (z filtrowaniem i usuwaniem).
2. Szczegóły pojedynczego zdarzenia - importowane z event_details.py.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import time
import crud
from views.registry_modules.details_components import event_details

# --- OKNO DIALOGOWE DO USUWANIA Z LISTY ---
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

# --- GŁÓWNA FUNKCJA ZAKŁADKI ---
def render_tab(id_zw):
    # Inicjalizacja stanu dla nawigacji wewnątrz zakładki
    if 'active_history_event_id' not in st.session_state:
        st.session_state.active_history_event_id = None

    # --- TRYB 1: SZCZEGÓŁY ZDARZENIA ---
    if st.session_state.active_history_event_id is not None:
        event_details.render_event_details(st.session_state.active_history_event_id)
        return

    # --- TRYB 2: LISTA ZDARZEŃ (GŁÓWNY WIDOK) ---
     # 1. Formularz dodawania nowego zdarzenia
    with st.expander("➕ Dodaj nowe zdarzenie", expanded=False):
        with st.form("new_history_entry_advanced"):
            st.write("Nowy wpis")
            c1, c2 = st.columns(2)
            sl_k = crud.pobierz_liste_slownika("SLOWNIK_KATEGORIA")
            kt = c1.selectbox("Typ zdarzenia", sl_k)
            dt = c2.date_input("Data zdarzenia", date.today())
            
            # Pobieranie autorów
            dfa = crud.pobierz_wszystkie_osoby()
            amp = {f"{x['Imie']} {x['Nazwisko']}": x['ID_Osoba'] for i,x in dfa.iterrows()}
            current_user = st.session_state.get('user_name', '')
            
            def_idx = 0
            if current_user in amp:
                def_idx = list(amp.keys()).index(current_user)
            
            asu = st.selectbox("Autor", list(amp.keys()), index=def_idx)
            de = st.text_area("Opis zdarzenia")
            
            pliki_startowe = st.file_uploader("Załączniki (opcjonalne)", accept_multiple_files=True)

            if st.form_submit_button("Zapisz zdarzenie", type="primary"):
                new_id = crud.dodaj_wpis_historii(id_zw, amp[asu], dt, kt, de)
                if pliki_startowe:
                    for f in pliki_startowe:
                        crud.dodaj_zalacznik(new_id, f)
                        
                st.success("Dodano wpis!")
                time.sleep(1)
                st.rerun()
    # 2. Filtry
    with st.expander("🔍 Filtrowanie historii", expanded=True):
        c1, c2 = st.columns(2)
        sl_kat = crud.pobierz_liste_slownika("SLOWNIK_KATEGORIA")
        filter_kat = c1.multiselect("Kategoria", sl_kat, default=sl_kat)
        filter_data_od = c2.date_input("Data od", date(2015, 1, 1))
        
    # 3. Pobieranie danych
    df_h = crud.pobierz_historie_zdarzen(id_zw)
    
    if not df_h.empty:
        # Filtrowanie (Pandas)
        df_h['DataZdarzenia'] = pd.to_datetime(df_h['DataZdarzenia'])
        mask = (df_h['Kategoria'].isin(filter_kat)) & (df_h['DataZdarzenia'].dt.date >= filter_data_od)
        df_filtered = df_h.loc[mask].sort_values(by='DataZdarzenia', ascending=False)
        
        # Wyświetlanie listy
        for index, row in df_filtered.iterrows():
            with st.container(border=True):
                # POPRAWKA: Zamiast 3 kolumn i zagnieżdżania, robimy od razu 4 kolumny
                # Układ: Data | Treść | Przycisk Szczegóły | Kosz
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
                    if st.button("🗑️", key=f"del_list_{row['ID_Historia']}", help="Usuń wpis"):
                        potwierdz_usuniecie_z_listy(row['ID_Historia'])

    else:
        st.info("Brak wpisów w historii.")

    st.divider()

   