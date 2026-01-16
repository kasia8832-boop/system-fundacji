"""
MODUŁ REJESTRU: LISTA ZWIERZĄT
------------------------------
Wyświetla tabelę ze wszystkimi zwierzętami.
Wersja 2.0: Dostosowana do nowej bazy (DataPrzyjecia) i nowego CRUD.
"""
import streamlit as st
import crud
import pandas as pd

def render_list():
    role = st.session_state.user_role
    
    # 1. Pobieramy dane słownikowe (używając nowych nazw funkcji z crud.py)
    # W nowym crud funkcja nazywa się get_dictionary
    try:
        sl_gat = crud.get_dictionary("SLOWNIK_GATUNKI")
        sl_stat = crud.get_dictionary("SLOWNIK_STATUSY")
    except Exception:
        # Fallback gdyby słowniki były puste/nieistniejące
        sl_gat = []
        sl_stat = []

    # 2. Pasek akcji (Przycisk dodawania)
    c_filt, c_act = st.columns([4, 1])
    
    with c_act:
        # Blokada przycisku dodawania dla DT
        if role in ["Administrator", "Pracownik", "Wolontariusz"]:
             if st.button("➕ Przyjmij", type="primary", use_container_width=True):
                st.session_state.view_mode = "admission"
                st.rerun()
        else:
             st.write("") 

    # 3. Filtry UI
    with c_filt:
        c1, c2, c3 = st.columns(3)
        with c1: 
            f_gat = st.multiselect("Gatunek", sl_gat, default=[])
        with c2: 
            f_stat = st.multiselect("Status", sl_stat, default=[])
        with c3: 
            f_txt = st.text_input("Szukaj (Imię/Chip)")

    # 4. Pobieranie danych (Nowa funkcja z crud.py)
    df = crud.get_all_animals_df()

    if df.empty:
        st.info("Brak zwierząt w bazie.")
        return

    # 5. Logika Filtrowania (Pandas)
    # Filtrujemy dane w pamięci aplikacji, bo crud zwraca wszystko
    
    if f_gat:
        df = df[df['Gatunek'].isin(f_gat)]
        
    if f_stat:
        df = df[df['StatusZwierzecia'].isin(f_stat)]
        
    if f_txt:
        # Szukanie case-insensitive w Imieniu LUB NrChip
        # Musimy obsłużyć sytuację, gdy NrChip jest pusty (None)
        mask = df['Imie'].str.contains(f_txt, case=False, na=False) | \
               df.get('NrChip', pd.Series()).astype(str).str.contains(f_txt, case=False, na=False)
        df = df[mask]

    # UWAGA: Logika filtrowania dla DT została tymczasowo zawieszona,
    # ponieważ usunęliśmy powiązania ID_Adoptujacy/DT z tabeli Zwierzę.
    # W przyszłości dodamy tabelę 'OPIEKA_TYMCZASOWA'.

    # 6. Wyświetlanie tabeli (Z nową kolumną DataPrzyjecia)
    if not df.empty:
        # Wybieramy kolumny do wyświetlenia (ID jest potrzebne do selecta, ale można je ukryć)
        cols_to_show = ['Imie', 'Gatunek', 'Plec', 'StatusZwierzecia', 'DataPrzyjecia', 'ID_Zwierze']
        
        # Sprawdzenie czy kolumny istnieją (zabezpieczenie po migracji)
        dostepne_kolumny = [c for c in cols_to_show if c in df.columns]
        
        event = st.dataframe(
            df[dostepne_kolumny],
            column_config={
                "DataPrzyjecia": st.column_config.DateColumn("Data Przyjęcia", format="DD.MM.YYYY"),
                "Imie": st.column_config.TextColumn("Imię"),
                "ID_Zwierze": st.column_config.NumberColumn("ID", disabled=True),
            },
            on_select="rerun",
            selection_mode="single-row",
            hide_index=True,
            use_container_width=True
        )

        # Obsługa kliknięcia w wiersz
        if len(event.selection.rows) > 0:
            selected_row_index = event.selection.rows[0]
            # Pobieramy ID z przefiltrowanego dataframe'u
            wybrane_id = df.iloc[selected_row_index]["ID_Zwierze"]
            
            st.session_state.active_animal_id = int(wybrane_id)
            st.session_state.view_mode = "details"
            st.rerun()
            
    else: 
        st.warning("Brak wyników spełniających kryteria wyszukiwania.")