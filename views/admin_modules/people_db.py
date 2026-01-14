"""
MODUŁ ADMINA: BAZA OSÓB (CRM)
-----------------------------
Baza danych osób fizycznych powiązanych z fundacją.
Są to Domy Tymczasowe (DT) oraz osoby Adoptujące.
Moduł pozwala na przeglądanie listy kontaktów i dodawanie nowych osób.
"""
import streamlit as st
import crud

def render_people_db():
    if st.button("⬅️ Wróć do Pulpitu"): 
        st.session_state.admin_mode = "dashboard"
        st.rerun()
        
    st.header("👥 Baza Osób (DT / Adoptujący)")
    
    t1, t2 = st.tabs(["Lista Osób", "Dodaj Osobę"])
    
    with t1:
         df_os = crud.pobierz_wszystkie_osoby()
         st.dataframe(df_os, width=1000)
         
    with t2:
         with st.form("add_os"):
             c1, c2 = st.columns(2)
             im = c1.text_input("Imię")
             nz = c2.text_input("Nazwisko")
             tel = c1.text_input("Telefon")
             em = c2.text_input("Email")
             mi = c1.text_input("Miasto")
             ul = c2.text_input("Ulica")
             dt = st.checkbox("Czy ta osoba to Dom Tymczasowy (DT)?")
             
             if st.form_submit_button("Dodaj do bazy"):
                 crud.dodaj_osobe(im, nz, tel, em, mi, ul, dt)
                 st.success("Dodano osobę!")
                 st.rerun()