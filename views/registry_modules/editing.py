"""
MODUŁ REJESTRU: EDYCJA DANYCH
-----------------------------
Formularz pozwalający zmienić dane istniejącego zwierzęcia.
Pobiera aktualne dane z bazy, wypełnia nimi pola i zapisuje zmiany.
"""


import streamlit as st
import pandas as pd
import time
import crud

def render_edit():
    if st.button("❌ Anuluj"): 
        st.session_state.view_mode = "details"
        st.rerun()
        
    st.header("✏️ Edycja Profilu")
    id_zw = int(st.session_state.active_animal_id)
    r = crud.pobierz_dane_do_edycji(id_zw).iloc[0]
    
    tab_main, tab_media, tab_med = st.tabs(["Podstawowe", "Multimedia", "Medyczne"])
    with st.form("ed_form"):
        with tab_main:
            c1, c2 = st.columns(2)
            with c1:
                ni = st.text_input("Imię", r['Imie'])
                nc = st.text_input("Nr Chip", r['NrChip'] or "")
            with c2:
                sl_stat = crud.pobierz_liste_slownika("SLOWNIK_STATUS")
                c_idx = sl_stat.index(r['StatusZwierzecia']) if r['StatusZwierzecia'] in sl_stat else 0
                ns = st.selectbox("Status", sl_stat, index=c_idx)
        with tab_media:
            n_img = st.text_input("Link do zdjęcia profilowego (URL)", r['ZdjecieProfilowe'] or "")
            n_yt = st.text_input("Link do filmu na YouTube", r['YouTubeURL'] or "")
        with tab_med:
            k = st.checkbox("Kastracja", bool(r['CzyKastrowany']))
            dk = st.date_input("Data Kastracji", pd.to_datetime(r['DataKastracji']) if r['DataKastracji'] else None)
            w = st.date_input("Wścieklizna", pd.to_datetime(r['SzczepienieWscieklizna']) if r['SzczepienieWscieklizna'] else None)
            z = st.date_input("Zakaźne", pd.to_datetime(r['SzczepienieZakazne']) if r['SzczepienieZakazne'] else None)
            o = st.date_input("Odrobaczenie", pd.to_datetime(r['Odrobaczenie']) if r['Odrobaczenie'] else None)
            u = st.text_area("Uwagi Weterynarza", r['UwagiMedyczne'] or "")
        
        if st.form_submit_button("💾 Zapisz", type="primary"):
            crud.zapisz_edycje_i_profil(id_zw, ni, nc, ns, k, dk, w, z, o, u, n_img, n_yt)
            st.success("Zapisano!")
            time.sleep(1)
            st.session_state.view_mode = "details"
            st.rerun()