"""
MODUŁ REJESTRU: PROCES ADOPCJI
------------------------------
Wizard finalizacji adopcji.
Użytkownik wpisuje dane adoptującego (tekst) i zatwierdza umowę.
To zmienia status zwierzęcia na 'Adoptowany'.
"""
import streamlit as st
from datetime import date
import time
import crud

def render_adoption():
    # Pobieramy ID zwierzęcia
    try:
        id_zw = int(st.session_state.active_animal_id)
        # Pobieramy imię dla lepszego wyglądu
        zwierz = crud.get_animal_details(id_zw)
        imie = zwierz['Imie']
    except:
        st.error("Błąd ID zwierzęcia")
        st.button("Wróć", on_click=lambda: setattr(st.session_state, 'view_mode', 'list'))
        st.stop()

    # Nagłówek
    st.header(f"🏠 Adopcja: {imie}")
    st.info("Wypełnij dane osoby adoptującej. To działanie zmieni status zwierzęcia na 'Adoptowany'.")

    # Formularz
    with st.form("adoption_form"):
        # Data
        data_adopcji = st.date_input("Data Adopcji", date.today())
        
        # Dane osoby - Zwykły String (Text Area)
        dane_osoby = st.text_area(
            "Dane Adoptującego", 
            placeholder="Imię i Nazwisko\nAdres zamieszkania\nNumer telefonu\nNr Dowodu (opcjonalnie)",
            height=150,
            help="Wpisz tutaj wszystkie dane kontaktowe osoby adoptującej."
        )
        
        st.divider()
        chk = st.checkbox("✅ Potwierdzam, że umowa adopcyjna została podpisana.")
        
        # Przyciski
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.form_submit_button("Anuluj"):
                st.session_state.view_mode = "details"
                st.rerun()
        
        with c2:
            submitted = st.form_submit_button("🎉 Finalizuj Adopcję", type="primary")
            
        if submitted:
            if not chk:
                st.error("Musisz potwierdzić podpisanie umowy!")
            elif not dane_osoby:
                st.error("Musisz wpisać dane osoby adoptującej!")
            else:
                # Wykonanie adopcji w bazie
                if crud.adoptuj_zwierze(id_zw, dane_osoby, data_adopcji):
                    st.balloons()
                    st.success("Gratulacje! Zwierzę zostało pomyślnie adoptowane.")
                    time.sleep(2)
                    st.session_state.view_mode = "details"
                    st.rerun()
                else:
                    st.error("Wystąpił błąd bazy danych.")