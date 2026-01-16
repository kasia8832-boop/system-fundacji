"""
MODUŁ ADMINA: ZARZĄDZANIE DOSTĘPEM
----------------------------------
Zarządzanie użytkownikami systemowymi (tabela UZYTKOWNIK).
Wersja 2.0: Dostosowana do nowej tabeli UZYTKOWNIK (LoginName, brak Imienia/Nazwiska w tej tabeli).
"""
import streamlit as st
import crud
import pandas as pd
import time

def render_access_control():
    # ZABEZPIECZENIE: Tylko Administrator
    if st.session_state.user_role != "Administrator":
        st.error("⛔ BRAK DOSTĘPU. Moduł tylko dla Administratora.")
        st.stop()

    st.subheader("🔐 Zarządzanie Kontami Systemowymi")
    
    tab_lista, tab_dodaj = st.tabs(["👥 Lista Kont", "➕ Utwórz Konto"])
    
    # --- ZAKŁADKA 1: LISTA ---
    with tab_lista:
        # Pobieramy dane z nowej funkcji CRUD
        users = crud.get_all_users()
        
        if not users.empty:
            st.dataframe(
                users,
                column_config={
                    "LoginName": "Login",
                    "Email": "E-mail",
                    "Rola": "Uprawnienia",
                    "CzyAktywny": st.column_config.CheckboxColumn("Aktywny?", disabled=True),
                    "ID_User": st.column_config.NumberColumn("ID", disabled=True)
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.divider()
            st.subheader("⚡ Akcje na koncie")
            
            # Selectbox do wyboru usera (po Loginie)
            lista_loginow = users['LoginName'].tolist()
            wybrany_login = st.selectbox("Wybierz użytkownika", lista_loginow)
            
            if wybrany_login:
                # Pobieramy wiersz danych wybranego usera
                user_row = users[users['LoginName'] == wybrany_login].iloc[0]
                user_id = int(user_row['ID_User'])
                is_active = int(user_row['CzyAktywny'])
                
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    # BLOKOWANIE
                    btn_label = "🚫 Zablokuj" if is_active else "✅ Odblokuj"
                    if st.button(btn_label, use_container_width=True):
                        crud.toggle_user_status(user_id, is_active)
                        st.success(f"Zmieniono status dla {wybrany_login}")
                        time.sleep(1)
                        st.rerun()
                        
                with c2:
                    # RESET HASŁA
                    new_pass_manual = st.text_input("Nowe hasło (dla resetu)", type="password", key="reset_pass_input")
                    if st.button("🔄 Zmień hasło", use_container_width=True):
                        if new_pass_manual:
                            crud.change_user_password(wybrany_login, new_pass_manual)
                            st.success("Hasło zostało zmienione.")
                        else:
                            st.warning("Wpisz najpierw nowe hasło.")
                            
                with c3:
                    # USUWANIE
                    if st.button("🗑️ Usuń konto", type="primary", use_container_width=True):
                        crud.delete_user(user_id)
                        st.warning(f"Usunięto konto: {wybrany_login}")
                        time.sleep(1)
                        st.rerun()

        else:
            st.info("Brak użytkowników w systemie.")
            
    # --- ZAKŁADKA 2: DODAWANIE ---
    with tab_dodaj:
        st.subheader("Tworzenie nowego użytkownika")
        with st.form("new_user_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_login = st.text_input("Login (unikalny)")
                new_email = st.text_input("E-mail")
            with c2:
                new_pass = st.text_input("Hasło startowe", type="password")
                new_role = st.selectbox("Rola", ["Administrator", "Pracownik", "Wolontariusz", "Dom Tymczasowy"])
            
            if st.form_submit_button("Utwórz konto"):
                if new_login and new_email and new_pass:
                    # Wywołanie nowej funkcji CRUD
                    ok = crud.create_user(new_login, new_email, new_pass, new_role)
                    if ok:
                        st.success(f"Utworzono użytkownika: {new_login}")
                        st.info(f"Hasło: {new_pass}")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Login jest już zajęty!")
                else:
                    st.warning("Wypełnij wszystkie pola.")