"""
ROUTER MODUŁU: REJESTR ZWIERZĄT
-------------------------------
To jest 'kierownik' działu Rejestr. Nie zawiera logiki wyświetlania (HTML/UI),
tylko importuje pod-moduły (lista, szczegóły, edycja) i decyduje,
który z nich wyświetlić na podstawie zmiennej 'view_mode'.
"""
import streamlit as st
# ...

import streamlit as st
# Importujemy nasze nowe pod-moduły
from views.registry_modules import listing, details, admission, editing, adoption

def render_registry():
    # 1. Pasek nawigacji (wspólny dla wszystkich widoków w rejestrze)
    col_nav, col_title = st.columns([1, 6])
    with col_nav:
        if st.button("🏠 Menu", use_container_width=True): 
            st.session_state.current_module = "home"
            st.rerun()
    with col_title: 
        st.subheader("Moduł: Rejestr Zwierząt")

    # 2. Router - Decyduje co wyświetlić
    mode = st.session_state.view_mode

    if mode == "list":
        listing.render_list()
        
    elif mode == "details":
        details.render_details()
        
    elif mode == "admission":
        admission.render_admission()
        
    elif mode == "edit":
        editing.render_edit()
        
    elif mode == "adoption_process":
        adoption.render_adoption()
        
    else:
        st.error(f"Nieznany tryb widoku: {mode}")
        if st.button("Reset widoku"):
            st.session_state.view_mode = "list"
            st.rerun()