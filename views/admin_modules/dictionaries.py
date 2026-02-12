"""
MODUŁ ADMINA: SŁOWNIKI
----------------------
Wersja 4.0: Usunięto przycisk powrotu i nagłówek (obsługiwane globalnie przez admin.py).
"""
import streamlit as st
import crud
import time

def render_dictionaries():
    # USUNIĘTO: Lokalny przycisk "Wróć" oraz st.header (są teraz w admin.py)
    
    mapa_slownikow = {
        "Gatunki Zwierząt": "gatunek",
        "Statusy Zwierzęcia": "status",
        "Kategorie Zdarzeń": "kategoria"
    }

    # Wybór słownika
    # Dodajemy etykietę, ale chowamy ją (label_visibility), żeby było estetyczniej, 
    # bo kontekst jest jasny z tytułu strony.
    wybrany_label = st.selectbox(
        "Wybierz słownik do edycji", 
        list(mapa_slownikow.keys()),
        label_visibility="visible"
    )
    klucz_crud = mapa_slownikow[wybrany_label]

    st.write("")
    
    c1, c2 = st.columns([1.5, 1])

    # --- LEWA: LISTA ---
    with c1:
        with st.container(border=True):
            st.markdown(f"**Lista wartości: {wybrany_label}**")
            wartosci = crud.pobierz_slownik(klucz_crud)
            
            if wartosci:
                # Wyświetlamy jako tabelkę z przyciskami
                for val in wartosci:
                    cc1, cc2 = st.columns([5, 1], vertical_alignment="center")
                    cc1.text(f"• {val}")
                    # Przycisk usuwania (mały)
                    if cc2.button("🗑️", key=f"del_{klucz_crud}_{val}", help="Usuń wartość"):
                        crud.usun_wartosc_slownika(klucz_crud, val)
                        st.rerun()
            else:
                st.info("Słownik jest pusty.")

    # --- PRAWA: DODAWANIE ---
    with c2:
        with st.container(border=True):
            st.markdown("**➕ Dodaj nową wartość**")
            with st.form("add_dic_form", clear_on_submit=True):
                nw = st.text_input("Nazwa", placeholder="np. Królik")
                
                st.write("")
                # Przycisk Primary (niebieski z admin.py)
                if st.form_submit_button("Dodaj", type="primary", use_container_width=True):
                    if nw:
                        crud.dodaj_wartosc_slownika(klucz_crud, nw)
                        st.success("Dodano!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.warning("Wpisz nazwę.")