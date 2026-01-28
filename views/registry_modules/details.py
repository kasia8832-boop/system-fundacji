"""
MODUŁ REJESTRU: SZCZEGÓŁY (LAYOUT)
----------------------------------
Główny kontener widoku szczegółów.
Wersja 3.1: Usunięto zakładkę Galeria (uproszczenie interfejsu).
"""

import streamlit as st
import crud
# Importujemy komponenty (BEZ tab_media)
from views.registry_modules.details_components import side_panel, top_bar, tab_info, tab_medical, tab_history

def render_details():
    # 1. Weryfikacja ID sesji
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Błąd: Brak aktywnego ID zwierzęcia.")
        if st.button("Wróć do listy"):
             st.session_state.view_mode = "list"
             st.rerun()
        st.stop()
        
    # 2. Pobieranie danych
    zwierze_obj = crud.pobierz_szczegoly_zwierzecia(id_zw)

    if zwierze_obj is None: 
        st.error(f"Błąd: Nie znaleziono zwierzęcia o ID {id_zw} w bazie.")
        if st.button("Wróć"):
            st.session_state.view_mode = "list"
            st.rerun()
        st.stop()
    
    # 3. Konwersja na słownik
    r = {k: v for k, v in vars(zwierze_obj).items() if not k.startswith('_')}
    r['ID_Zwierze'] = zwierze_obj.IDZwierze 
    r['CzyKastrowany'] = "Tak" if zwierze_obj.DataKastracji else "Nie"
    
    # 4. Przycisk powrotu
    nav_col, action_col = st.columns([1, 6])
    with nav_col:
        if st.button("⬅️ Wróć", use_container_width=True): 
            st.session_state.view_mode = "list"
            st.rerun()
    st.divider()

    # 5. Układ strony
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Panel boczny ze zdjęciem
        side_panel.render_side_panel(r)

    with col_right:
        # Górny pasek
        top_bar.render_top_bar(r, id_zw)

        # Zakładki (TERAZ TYLKO 3)
        t1, t2, t3 = st.tabs(["📄 Dane", "💉 Zdrowie", "📜 Historia"])
        
        with t1:
            tab_info.render_tab(r)
        with t2:
            tab_medical.render_tab(r)
        with t3:
            tab_history.render_tab(id_zw)