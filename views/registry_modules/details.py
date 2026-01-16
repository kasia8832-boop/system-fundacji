"""
MODUŁ REJESTRU: SZCZEGÓŁY (LAYOUT)
----------------------------------
Główny kontener widoku szczegółów.
Wersja 2.0: Pobiera dane z nowego CRUD (rozdzielone tabele) i scala je
dla komponentów podrzędnych.
"""

import streamlit as st
import crud
import pandas as pd
# Importujemy nasze komponenty
from views.registry_modules.details_components import side_panel, top_bar, tab_info, tab_medical, tab_media, tab_history

def render_details():
    # 1. Weryfikacja ID sesji
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Błąd: Brak aktywnego ID zwierzęcia.")
        st.button("Wróć do listy", on_click=lambda: setattr(st.session_state, 'view_mode', 'list'))
        st.stop()
        
    # 2. Pobieranie danych (NOWY MODEL)
    # W nowym CRUD dane są w dwóch funkcjach, musimy je pobrać osobno
    animal_basic = crud.get_animal_details(id_zw)
    animal_med = crud.get_medical_profile(id_zw)

    if animal_basic is None: 
        st.error("Błąd: Nie znaleziono zwierzęcia w bazie.")
        st.stop()
    
    # 3. Scalanie danych (Data Merging)
    # Komponenty (side_panel, tab_info itp.) spodziewają się jednego obiektu 'r'.
    # Konwertujemy Pandas Series na zwykły słownik (dict) i łączymy je.
    r = animal_basic.to_dict()
    
    if animal_med is not None:
        r.update(animal_med.to_dict())
    
    # Teraz 'r' zawiera zarówno Imie, Gatunek jak i SzczepienieWscieklizna
    
    # 4. Przycisk powrotu
    nav_col, action_col = st.columns([1, 6])
    with nav_col:
        if st.button("⬅️ Wróć", use_container_width=True): 
            st.session_state.view_mode = "list"
            st.rerun()
    st.divider()

    # 5. Układ strony: Lewy Panel (Zdjęcie) + Prawy Panel (Treść)
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Przekazujemy scalony słownik 'r'
        side_panel.render_side_panel(r)

    with col_right:
        # Górny pasek (Imię, Chip, Status)
        top_bar.render_top_bar(r, id_zw)

        # Zakładki
        # Zmieniono nazwę zakładki 3 (usunięto "Wideo")
        t1, t2, t3, t4 = st.tabs(["📄 Dane", "💉 Zdrowie", "📷 Galeria", "📜 Historia"])
        
        with t1:
            tab_info.render_tab(r)
        with t2:
            tab_medical.render_tab(r)
        with t3:
            # Pamiętaj, żeby sprawdzić plik tab_media.py czy nie wyświetla YouTubeURL!
            tab_media.render_tab(r, id_zw)
        with t4:
            tab_history.render_tab(id_zw)