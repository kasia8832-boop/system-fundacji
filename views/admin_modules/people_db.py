"""
MODUŁ ADMINA: BAZA OSÓB (CRM)
-----------------------------
Baza danych osób fizycznych powiązanych z fundacją.
Wersja 2.0: Dostosowana do nowego CRUD (DataRejestracji, Rola).
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
    
    # Zakładki nawigacyjne
    tabs = ["Lista Osób"]
    if role in ["Administrator", "Pracownik"]:
        tabs.append("Dodaj Osobę")
        
    active_tab = st.radio("Widok", tabs, horizontal=True, label_visibility="collapsed")
    st.divider()
    
    # --- WIDOK 1: LISTA OSÓB ---
    if active_tab == "Lista Osób":
         # Nowa funkcja CRUD
         df_os = crud.get_all_people()
         
         if not df_os.empty:
             st.dataframe(
                 df_os, 
                 column_config={
                     "DataRejestracji": st.column_config.DateColumn("Rejestracja", format="DD.MM.YYYY"),
                     "Imie": "Imię",
                     "Nazwisko": "Nazwisko",
                     "Rola": "Typ Kontaktu",
                     "Telefon": "Telefon",
                     "Email": "E-mail",
                     "Miasto": "Miasto"
                 },
                 use_container_width=True,
                 hide_index=True
             )
         else:
             st.info("Baza osób jest pusta.")
             
    # --- WIDOK 2: DODAJ OSOBĘ ---
    elif active_tab == "Dodaj Osobę":
         st.subheader("➕ Nowy Kontakt")
         with st.form("add_os_form"):
             c1, c2 = st.columns(2)
             with c1:
                 im = st.text_input("Imię")
                 tel = st.text_input("Telefon")
                 mi = st.text_input("Miasto")
             with c2:
                 nz = st.text_input("Nazwisko")
                 em = st.text_input("Email")
                 # Zamiast checkboxa 'Czy DT', wybieramy Rolę (zgodnie z nowym CRUD)
                 rola_osoby = st.selectbox("Rola / Typ Kontaktu", ["Adoptujący", "Dom Tymczasowy", "Wolontariusz", "Inny"])
             
             # Usunięto pole "Ulica", bo nowy crud.add_person go nie obsługuje
             
             if st.form_submit_button("Zapisz w bazie", type="primary"):
                 if im and nz:
                     # Wywołanie nowej funkcji CRUD
                     crud.add_person(im, nz, rola_osoby, tel, em, mi)
                     st.success(f"Dodano osobę: {im} {nz}")
                     st.rerun()
                 else:
                     st.warning("Imię i Nazwisko są wymagane.")