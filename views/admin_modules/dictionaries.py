"""
MODUŁ ADMINA: SŁOWNIKI
----------------------
Wersja 3.0: Nowy CRUD (dodaj/usuń wartość).
"""
import streamlit as st
import crud
import time

def render_dictionaries():
    if st.button("⬅️ Wróć do Pulpitu"): 
        st.session_state.admin_mode = "dashboard"
        st.rerun()
        
    st.header("📚 Zarządzanie Słownikami")
    
    # Mapowanie na klucze, które rozumie nasz nowy crud.py
    mapa_slownikow = {
        "Gatunki Zwierząt": "gatunek",
        "Statusy Zwierzęcia": "status",
        "Kategorie Zdarzeń": "kategoria"
    }

    wybrany_label = st.selectbox("Wybierz słownik", list(mapa_slownikow.keys()))
    klucz_crud = mapa_slownikow[wybrany_label]

    st.divider()
    c1, c2 = st.columns(2)

    # --- LISTA ---
    with c1:
        st.subheader(f"Lista: {wybrany_label}")
        wartosci = crud.pobierz_slownik(klucz_crud)
        
        if wartosci:
            for val in wartosci:
                cols = st.columns([4, 1])
                cols[0].write(f"• {val}")
                if cols[1].button("🗑️", key=f"d_{klucz_crud}_{val}"):
                    crud.usun_wartosc_slownika(klucz_crud, val)
                    st.rerun()
        else:
            st.info("Pusto.")

    # --- DODAWANIE ---
    with c2:
        st.subheader("➕ Dodaj")
        with st.form("add_dic"):
            nw = st.text_input("Nowa nazwa")
            if st.form_submit_button("Dodaj"):
                if nw:
                    crud.dodaj_wartosc_slownika(klucz_crud, nw)
                    st.success("Dodano!")
                    time.sleep(0.5)
                    st.rerun()