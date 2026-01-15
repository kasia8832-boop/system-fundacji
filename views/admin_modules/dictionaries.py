"""
MODUŁ ADMINA: ZARZĄDZANIE SŁOWNIKAMI
------------------------------------
Pozwala dodawać i usuwać wartości ze słowników systemowych:
- Kategorie zdarzeń
- Gatunki
- Statusy
- Źródła finansowania
"""
import streamlit as st
import crud
import time

def render_dictionaries():
    if st.button("⬅️ Wróć do Pulpitu"): 
        st.session_state.admin_mode = "dashboard"
        st.rerun()
        
    st.header("📚 Zarządzanie Słownikami")
    
    # Uprawnienia: Tylko Admin i Pracownik mogą tu wejść (zgodnie z dashboardem)
    # Ale dodajmy check dla pewności
    role = st.session_state.user_role
    if role == "Wolontariusz" or role == "Dom Tymczasowy":
         st.error("Brak uprawnień do edycji słowników.")
         st.stop()

    # Mapa nazw wyświetlanych na nazwy tabel w bazie
    mapa_slownikow = {
        "Kategorie Zdarzeń (Oś Czasu)": "SLOWNIK_KATEGORIA",
        "Gatunki Zwierząt": "SLOWNIK_GATUNEK",
        "Statusy Zwierzęcia": "SLOWNIK_STATUS",
        "Źródła Finansowania": "SLOWNIK_ZRODLO"
    }

    wybrany_slownik_label = st.selectbox("Wybierz słownik do edycji", list(mapa_slownikow.keys()))
    tabela_db = mapa_slownikow[wybrany_slownik_label]

    st.divider()

    col_left, col_right = st.columns(2)

    # --- LEWA KOLUMNA: Lista i Usuwanie ---
    with col_left:
        st.subheader(f"Lista: {wybrany_slownik_label}")
        # Wymuszamy odświeżenie cache, pobierając dane
        wartosci = crud.pobierz_liste_slownika(tabela_db)
        crud.pobierz_liste_slownika.clear() # Czyścimy cache żeby widzieć zmiany natychmiast
        
        if wartosci:
            for val in wartosci:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"• {val}")
                with c2:
                    if st.button("🗑️", key=f"del_{tabela_db}_{val}"):
                        ok, msg = crud.usun_element_slownika(tabela_db, val)
                        if ok:
                            st.success("Usunięto!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("Słownik jest pusty.")

    # --- PRAWA KOLUMNA: Dodawanie ---
    with col_right:
        st.subheader("➕ Dodaj nową wartość")
        with st.form(f"add_{tabela_db}"):
            nowa_wartosc = st.text_input("Nazwa")
            if st.form_submit_button("Dodaj"):
                if nowa_wartosc:
                    # Walidacja prostych duplikatów (wielkość liter)
                    if nowa_wartosc in wartosci:
                         st.error("Taka wartość już istnieje!")
                    else:
                        ok, msg = crud.dodaj_element_slownika(tabela_db, nowa_wartosc)
                        if ok:
                            st.success(f"Dodano: {nowa_wartosc}")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.warning("Wpisz wartość.")

    st.divider()
    st.info("💡 **Płeć (M/K)** oraz **Role użytkowników** są stałymi systemowymi i nie edytuje się ich w tym panelu, aby nie naruszyć logiki aplikacji.")