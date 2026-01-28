"""
MODUŁ ADMINA: BAZA OSÓB
-----------------------
Wersja 3.0: Nowy CRUD (dodawanie osoby z pełnymi danymi).
"""
import streamlit as st
import crud
import pandas as pd

def render_people_db():
    if st.button("⬅️ Wróć do Pulpitu"): 
        st.session_state.admin_mode = "dashboard"
        st.rerun()
        
    st.header("👥 Baza Osób (DT / Adoptujący)")
    
    role = st.session_state.user_role
    
    tabs = ["Lista Osób"]
    if role in ["Admin", "Pracownik"]:
        tabs.append("Dodaj Osobę")
        
    active_tab = st.radio("Widok", tabs, horizontal=True, label_visibility="collapsed")
    st.divider()
    
    # --- WIDOK 1: LISTA ---
    if active_tab == "Lista Osób":
         df_os = crud.pobierz_wszystkie_osoby() # Ta funkcja już była w crud
         
         if not df_os.empty:
             st.dataframe(
                 df_os, 
                 use_container_width=True,
                 hide_index=True
             )
         else:
             st.info("Baza osób jest pusta.")
             
    # --- WIDOK 2: DODAWANIE ---
    elif active_tab == "Dodaj Osobę":
         st.subheader("➕ Nowy Kontakt")
         with st.form("add_os_form"):
             c1, c2 = st.columns(2)
             with c1:
                 im = st.text_input("Imię *")
                 tel = st.text_input("Telefon")
                 mi = st.text_input("Miasto")
                 ul = st.text_input("Ulica")
             with c2:
                 nz = st.text_input("Nazwisko *")
                 em = st.text_input("Email")
                 kod = st.text_input("Kod pocztowy")
                 lok = st.text_input("Nr lokalu/domu")
             
             if st.form_submit_button("Zapisz w bazie", type="primary"):
                 if im and nz:
                     # Wywołanie: imie, nazwisko, telefon, email, miasto, ulica, lokal, kod
                     ok, msg = crud.dodaj_osobe(im, nz, tel, em, mi, ul, lok, kod)
                     if ok:
                        st.success(f"Dodano osobę: {im} {nz}")
                        st.rerun()
                     else:
                        st.error(f"Błąd: {msg}")
                 else:
                     st.warning("Imię i Nazwisko są wymagane.")