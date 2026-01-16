"""
MODUŁ ADMINA: ZARZĄDZANIE SŁOWNIKAMI
------------------------------------
Pozwala dodawać i usuwać wartości ze słowników systemowych.
Wersja 2.0: Używa nowego CRUD.
"""
import streamlit as st
import crud
import time

def render_dictionaries():
    if st.button("⬅️ Wróć do Pulpitu"): 
        st.session_state.admin_mode = "dashboard"
        st.rerun()
        
    st.header("📚 Zarządzanie Słownikami")
    
    role = st.session_state.user_role
    if role == "Wolontariusz" or role == "Dom Tymczasowy":
         st.error("Brak uprawnień do edycji słowników.")
         st.stop()

    # Mapa nazw wyświetlanych na nazwy tabel w bazie
    # UWAGA: Upewnij się, że te nazwy tabel zgadzają się z tymi w bazie (wielka litera/liczba mnoga)
    mapa_slownikow = {
        "Kategorie Zdarzeń (Oś Czasu)": "SLOWNIK_KATEGORIE",
        "Gatunki Zwierząt": "SLOWNIK_GATUNKI",
        "Statusy Zwierzęcia": "SLOWNIK_STATUSY",
        "Źródła Finansowania": "SLOWNIK_ZRODLO" # Jeśli ta tabela została
    }

    wybrany_slownik_label = st.selectbox("Wybierz słownik do edycji", list(mapa_slownikow.keys()))
    tabela_db = mapa_slownikow[wybrany_slownik_label]

    st.divider()

    col_left, col_right = st.columns(2)

    # --- LEWA KOLUMNA: Lista i Usuwanie ---
    with col_left:
        st.subheader(f"Lista: {wybrany_slownik_label}")
        
        # Nowa funkcja CRUD
        wartosci = crud.get_dictionary(tabela_db)
        
        if wartosci:
            for val in wartosci:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"• {val}")
                with c2:
                    if st.button("🗑️", key=f"del_{tabela_db}_{val}"):
                        crud.delete_dict_value(tabela_db, val)
                        st.success("Usunięto!")
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.info("Słownik jest pusty.")

    # --- PRAWA KOLUMNA: Dodawanie ---
    with col_right:
        st.subheader("➕ Dodaj nową wartość")
        with st.form(f"add_{tabela_db}"):
            nowa_wartosc = st.text_input("Nazwa")
            if st.form_submit_button("Dodaj"):
                if nowa_wartosc:
                    if wartosci and nowa_wartosc in wartosci:
                          st.error("Taka wartość już istnieje!")
                    else:
                        crud.add_dict_value(tabela_db, nowa_wartosc)
                        st.success(f"Dodano: {nowa_wartosc}")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.warning("Wpisz wartość.")

    st.divider()
    st.info("💡 **Płeć** oraz **Role użytkowników** są stałymi systemowymi.")