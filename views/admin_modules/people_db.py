"""
MODUŁ ADMINA: BAZA OSÓB
-----------------------
Wersja 4.0: Usunięto lokalny nagłówek i przycisk powrotu (obsługiwane przez admin.py).
"""
import streamlit as st
import crud
import pandas as pd
import time

def render_people_db():
    # USUNIĘTO: Lokalny przycisk "Wróć" i Nagłówek.
    # Są one teraz wyświetlane globalnie w views/admin.py
    
    role = st.session_state.user_role
    
    # Konfiguracja zakładek
    tabs_names = ["📋 Lista Osób"]
    if role in ["Admin", "Pracownik"]:
        tabs_names.append("➕ Dodaj Osobę")
        
    # Obsługa jednej lub wielu zakładek
    if len(tabs_names) > 1:
        tab_view, tab_add = st.tabs(tabs_names)
    else:
        tab_view = st.tabs(tabs_names)[0]
        tab_add = None
    
    # --- ZAKŁADKA 1: LISTA ---
    with tab_view:
         df_os = crud.pobierz_wszystkie_osoby()
         
         if not df_os.empty:
             st.dataframe(
                 df_os, 
                 use_container_width=True,
                 hide_index=True,
                 column_config={
                     "IDOsoba": st.column_config.NumberColumn("ID", width="small"),
                     "Imie": "Imię",
                     "Nazwisko": "Nazwisko",
                     "Telefon": "Tel",
                     "Email": "E-mail",
                     "Display": None # Ukrywamy kolumnę techniczną
                 }
             )
         else:
             st.info("Baza osób jest pusta.")
             
    # --- ZAKŁADKA 2: DODAWANIE ---
    if tab_add:
        with tab_add:
             with st.container(border=True):
                 st.markdown("##### Nowy Kontakt")
                 with st.form("add_os_form", clear_on_submit=True):
                     
                     st.caption("Dane Kontaktowe")
                     c1, c2 = st.columns(2)
                     with c1:
                         im = st.text_input("Imię *")
                         tel = st.text_input("Telefon")
                     with c2:
                         nz = st.text_input("Nazwisko *")
                         em = st.text_input("E-mail")
                     
                     st.divider()
                     st.caption("Dane Adresowe")
                     
                     a1, a2 = st.columns(2)
                     with a1:
                         mi = st.text_input("Miasto")
                         ul = st.text_input("Ulica")
                     with a2:
                         kod = st.text_input("Kod pocztowy")
                         lok = st.text_input("Nr lokalu/domu")
                     
                     st.write("")
                     # Przycisk Primary (niebieski z admin.py)
                     if st.form_submit_button("💾 Zapisz w bazie", type="primary", use_container_width=True):
                         if im and nz:
                             ok, msg = crud.dodaj_osobe(im, nz, tel, em, mi, ul, lok, kod)
                             if ok:
                                st.success(f"Dodano osobę: {im} {nz}")
                                time.sleep(1)
                                st.rerun()
                             else:
                                st.error(f"Błąd: {msg}")
                         else:
                             st.warning("Pola oznaczone gwiazdką (*) są wymagane.")