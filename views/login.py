"""
WIDOK: LOGOWANIE
----------------
Obsługuje formularz logowania użytkownika.
Weryfikuje e-mail i hasło przez bazę danych (crud.py) i ustawia flagę 'logged_in'.
"""
import streamlit as st
# ...import streamlit as st
import time
import crud

def render_login():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>🔐 Witaj po tej Mostu</h1>", unsafe_allow_html=True)
        st.container(border=True)
        
        if st.session_state.login_mode == "login":
            st.subheader("Zaloguj się")
            with st.form("login_form"):
                email = st.text_input("Login (Email)", autocomplete="username") 
                passwd = st.text_input("Hasło", type="password", autocomplete="current-password")
                submitted = st.form_submit_button("Wejdź", type="primary", use_container_width=True)
                
                if submitted:
                    ok, name, role = crud.weryfikuj_logowanie(email, passwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_name = name
                        st.session_state.user_role = role
                        st.success(f"Witaj {name}!")
                        time.sleep(0.5)
                        st.rerun()
                    else: 
                        st.error("Błąd logowania.")

            if st.button("Reset hasła", use_container_width=True):
                st.session_state.login_mode = "forgot"
                st.rerun()
        else:
            st.subheader("Reset hasła")
            st.info("Funkcja resetu dostępna u Administratora.")
            if st.button("Wróć"): 
                st.session_state.login_mode = "login"
                st.rerun()