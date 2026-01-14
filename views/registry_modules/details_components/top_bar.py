"""
KOMPONENT KARTY: NAGŁÓWEK
-------------------------
Wyświetla imię zwierzęcia, ID oraz główne przyciski akcji:
'Edytuj' oraz 'Adoptuj' (jeśli zwierzę jest do adopcji).
"""

import streamlit as st

def render_top_bar(r, id_zw):
    st.title(r['Imie'])
    st.caption(f"Gatunek: {r['Gatunek']} | ID: {id_zw}")
    st.divider()

    c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 2])
    
    with c_btn1:
        if st.button("✏️ Edytuj", use_container_width=True): 
            st.session_state.view_mode = "edit"
            st.rerun()
            
    with c_btn2:
        if r['StatusZwierzecia'] == 'Do adopcji':
            if st.button("🏠 Adoptuj", type="primary", use_container_width=True): 
                st.session_state.view_mode = "adoption_process"
                st.rerun()