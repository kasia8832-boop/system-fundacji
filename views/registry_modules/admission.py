"""
MODUŁ REJESTRU: PRZYJĘCIE (NOWE ZWIERZĘ)
----------------------------------------
Formularz dodawania nowego podopiecznego do bazy.
Obsługuje wprowadzanie danych podstawowych i przypisanie do Domu Tymczasowego.
"""

#przyjęcie_zwierzecia

import streamlit as st
from datetime import date
import time
import crud

def render_admission():
    if st.button("❌ Anuluj"): 
        st.session_state.view_mode = "list"
        st.rerun()
        
    st.header("📝 Przyjęcie")
    sl_gat = crud.pobierz_liste_slownika("SLOWNIK_GATUNEK")
    sl_stat = crud.pobierz_liste_slownika("SLOWNIK_STATUS")
    
    # NOWE: Pobieranie źródła z bazy zamiast na sztywno
    sl_zrodlo = crud.pobierz_liste_slownika("SLOWNIK_ZRODLO")
    df_dt = crud.pobierz_liste_dt()
    dt_opts = {"Brak": None}
    for i, r in df_dt.iterrows(): dt_opts[f"{r['Imie']} {r['Nazwisko']}"] = r['ID_Osoba']
    
    with st.form("adm"):
        c1, c2 = st.columns(2)
        with c1:
            im = st.text_input("Imię")
            gt = st.selectbox("Gatunek", sl_gat)
            pl = st.radio("Płeć", ["Samiec", "Samica"], horizontal=True)
            ch = st.text_input("Chip")
            dt = st.selectbox("DT", list(dt_opts.keys()))
        with c2:
            ur = st.date_input("Urodzenie", date(2020,1,1))
            stt = st.selectbox("Status", sl_stat)
            src = st.selectbox("Źródło", sl_zrodlo)
            olx = st.checkbox("OLX"); www = st.checkbox("WWW")
            
        if st.form_submit_button("Zapisz", type="primary"):
            if im:
                crud.dodaj_zwierze(im, gt, pl, ch, ur, stt, src, olx, www, dt_opts[dt])
                st.success("Dodano!")
                time.sleep(1)
                st.session_state.view_mode = "list"
                st.rerun()
            else: 
                st.error("Brak imienia")