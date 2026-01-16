"""
MODUŁ REJESTRU: PRZYJĘCIE (NOWE ZWIERZĘ)
----------------------------------------
Szybki formularz dodawania nowego podopiecznego.
Tworzy kartę zwierzęcia. Szczegóły (Chip, Data Urodzenia, Zdjęcia) 
dodaje się w trybie Edycji po utworzeniu rekordu.
"""
import streamlit as st
import time
import crud

def render_admission():
    # Przycisk Anuluj
    if st.button("❌ Anuluj"): 
        st.session_state.view_mode = "list"
        st.rerun()
        
    st.header("📝 Przyjęcie nowego podopiecznego")
    st.info("Tutaj tworzysz podstawową kartę. Chip, datę urodzenia i opis dodasz w edycji po utworzeniu.")

    # 1. Pobieranie słowników (Nowe nazwy funkcji z crud.py)
    # Używamy try/except na wypadek gdyby słowniki były puste
    try:
        sl_gat = crud.get_dictionary("SLOWNIK_GATUNKI")
        sl_stat = crud.get_dictionary("SLOWNIK_STATUSY")
    except:
        sl_gat = ["Pies", "Kot"]
        sl_stat = ["Do adopcji", "Kwarantanna"]
    
    # 2. Formularz
    with st.form("adm_form"):
        c1, c2 = st.columns(2)
        
        with c1:
            imie = st.text_input("Imię")
            gatunek = st.selectbox("Gatunek", sl_gat)
            
        with c2:
            plec = st.radio("Płeć", ["Samiec", "Samica", "Nieznana"], horizontal=True)
            status = st.selectbox("Status", sl_stat)
            
        # UWAGA: Usunęliśmy pola Chip, Urodzenie, Źródło, DT, OLX, WWW
        # ponieważ funkcja crud.add_animal() w nowej wersji ich nie obsługuje
        # (zostały przeniesione do edycji szczegółowej).
            
        submitted = st.form_submit_button("💾 Utwórz Kartę", type="primary")
        
        if submitted:
            if imie:
                # Wywołujemy nową, uproszczoną funkcję z crud.py
                new_id = crud.add_animal(imie, gatunek, plec, status)
                
                st.success(f"Dodano zwierzę! Nadano ID: {new_id}")
                time.sleep(1)
                
                # Automatyczne przekierowanie do edycji tego zwierzęcia
                # żeby użytkownik mógł od razu uzupełnić resztę danych
                st.session_state.active_animal_id = new_id
                st.session_state.view_mode = "details" # lub "edit" zależnie od preferencji
                st.rerun()
            else: 
                st.error("Imię jest wymagane!")