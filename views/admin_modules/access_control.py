"""
MODUŁ ADMINA: KONTROLA DOSTĘPU
------------------------------
Zarządzanie użytkownikami systemu:
1. Lista użytkowników (zmiana ról, reset haseł).
2. Dodawanie nowych użytkowników.

ZABEZPIECZENIE: Dostęp tylko dla roli 'Administrator'.
"""
import streamlit as st
import pandas as pd
import time
import crud

# --- OKNO DIALOGOWE: RESET HASŁA ---
@st.dialog("🔑 Resetowanie hasła")
def potwierdz_reset_hasla(email_user):
    st.write(f"Czy na pewno chcesz zresetować hasło dla: **{email_user}**?")
    st.warning("Użytkownik otrzyma nowe, tymczasowe hasło.")
    
    if st.button("Tak, resetuj hasło", type="primary"):
        ok, wynik = crud.resetuj_haslo(email_user)
        if ok:
            st.success(f"Hasło zresetowane! Nowe hasło to: {wynik}")
            st.info("Przekaż to hasło użytkownikowi. Będzie widoczne tylko teraz.")
        else:
            st.error(f"Błąd: {wynik}")

def render_access_control():
    # ============================================================
    # 🛑 SECURITY GATE (BRAMKA BEZPIECZEŃSTWA)
    # ============================================================
    # Zgodnie z wymaganiami: Pracownik i Wolontariusz nie mają tu wstępu.
    if st.session_state.user_role != "Administrator":
        st.error("⛔ BRAK DOSTĘPU. Zarządzanie kontami jest dostępne tylko dla Administratora.")
        # Przycisk awaryjny do powrotu
        if st.button("Wróć"):
            st.session_state.admin_mode = "dashboard"
            st.rerun()
        st.stop() # Zatrzymuje dalsze wykonywanie kodu poniżej!
    # ============================================================

    st.header("🔐 Zarządzanie Dostępem")
    
    tab_lista, tab_dodaj = st.tabs(["👥 Lista użytkowników", "➕ Dodaj użytkownika"])
    
    # --- ZAKŁADKA 1: LISTA UŻYTKOWNIKÓW ---
    with tab_lista:
        users = crud.pobierz_liste_uzytkownikow()
        
        if not users.empty:
            st.dataframe(users, use_container_width=True)
            st.divider()
            
            st.subheader("Edycja uprawnień")
            
            # Wybór użytkownika do edycji
            user_options = {f"{u['Imie']} {u['Nazwisko']} ({u['Email']})": u['ID'] for i, u in users.iterrows()}
            selected_user_label = st.selectbox("Wybierz użytkownika do edycji", list(user_options.keys()))
            selected_user_id = user_options[selected_user_label]
            
            # Pobranie aktualnej roli wybranego usera
            current_role = users.loc[users['ID'] == selected_user_id, 'Role'].values[0]
            current_email = users.loc[users['ID'] == selected_user_id, 'Email'].values[0]
            
            c1, c2, c3 = st.columns([2, 1, 1])
            
            with c1:
                # Zmiana roli - dodano nowe role zgodnie z Twoim opisem
                dostepne_role = ["Administrator", "Pracownik", "Wolontariusz", "Dom Tymczasowy"]
                
                try:
                    idx = dostepne_role.index(current_role)
                except:
                    idx = 2 # Domyślnie Wolontariusz
                
                new_role = st.selectbox("Zmień rolę", dostepne_role, index=idx)
                
            with c2:
                st.write("") 
                st.write("") 
                if st.button("Zapisz rolę", use_container_width=True):
                    crud.zmien_role_uzytkownika(selected_user_id, new_role)
                    st.success("Zmieniono rolę!")
                    time.sleep(1)
                    st.rerun()
            
            with c3:
                st.write("") 
                st.write("") 
                # Reset hasła
                if st.button("Resetuj hasło", type="primary", use_container_width=True):
                    potwierdz_reset_hasla(current_email)

        else:
            st.info("Brak użytkowników w bazie.")

    # --- ZAKŁADKA 2: DODAWANIE UŻYTKOWNIKA ---
    with tab_dodaj:
        st.subheader("Tworzenie nowego konta")
        
        with st.form("add_user_form"):
            c1, c2 = st.columns(2)
            imie = c1.text_input("Imię")
            nazwisko = c2.text_input("Nazwisko")
            
            email = st.text_input("Adres Email (Login)")
            rola = st.selectbox("Rola w systemie", ["Wolontariusz", "Dom Tymczasowy", "Pracownik", "Administrator"])
            
            st.info("ℹ️ Hasło zostanie wygenerowane automatycznie.")
            
            if st.form_submit_button("Utwórz użytkownika", type="primary"):
                if imie and nazwisko and email:
                    ok, wynik = crud.dodaj_uzytkownika_systemu(imie, nazwisko, email, rola)
                    if ok:
                        st.success("Konto utworzone pomyślnie!")
                        st.warning(f"🔑 ZAPISZ HASŁO TYMCZASOWE: **{wynik}**")
                        st.info("Przekaż to hasło nowemu użytkownikowi.")
                    else:
                        st.error(f"Błąd: {wynik}")
                else:
                    st.warning("Wypełnij wszystkie pola.")