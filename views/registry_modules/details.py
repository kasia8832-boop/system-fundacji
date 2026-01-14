"""
MODUŁ REJESTRU: SZCZEGÓŁY (LAYOUT)
----------------------------------
Odpowiada za układ (Layout) Karty Zwierzęcia.
Dzieli ekran na lewy panel (zdjęcie) i prawy panel (dane).
Importuje mniejsze komponenty z folderu 'details_components', aby zbudować całość.
"""


import streamlit as st
import crud
# Importujemy nasze nowe komponenty
from views.registry_modules.details_components import side_panel, top_bar, tab_info, tab_medical, tab_media, tab_history

def render_details():
    # 1. Pobranie ID i Danych
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Błąd ID")
        st.stop()
        
    r_df = crud.pobierz_pelna_karte(id_zw)
    if r_df.empty: 
        st.error("Błąd: Nie znaleziono danych.")
        st.stop()
    r = r_df.iloc[0] # Mamy dane jednego zwierzęcia
    
    # 2. Przycisk powrotu
    nav_col, action_col = st.columns([1, 6])
    with nav_col:
        if st.button("⬅️ Wróć", use_container_width=True): 
            st.session_state.view_mode = "list"
            st.rerun()
    st.divider()

    # 3. Układ strony: Lewy Panel (Zdjęcie) + Prawy Panel (Treść)
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Renderujemy lewy panel z osobnego pliku
        side_panel.render_side_panel(r)

    with col_right:
        # Renderujemy górny pasek (tytuł, przyciski)
        top_bar.render_top_bar(r, id_zw)

        # Renderujemy Zakładki
        t1, t2, t3, t4 = st.tabs(["📄 Dane", "💉 Zdrowie", "📷 Galeria & Wideo", "📜 Historia"])
        
        with t1:
            tab_info.render_tab(r)
        with t2:
            tab_medical.render_tab(r)
        with t3:
            tab_media.render_tab(r, id_zw)
        with t4:
            tab_history.render_tab(id_zw)
