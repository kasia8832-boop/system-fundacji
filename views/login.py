"""
WIDOK: LOGOWANIE I RESET HASŁA
------------------------------
Obsługuje logowanie oraz dwuetapowy proces odzyskiwania hasła.
Integruje frontend z email_service.
"""
import streamlit as st
import time
import crud
from services import email_service

def render_login():
    # Centrowanie formularza na ekranie
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>🔐 System Fundacji</h1>", unsafe_allow_html=True)
        st.container(border=True)
        
        # Inicjalizacja trybu logowania, jeśli go nie ma
        if 'login_mode' not in st.session_state:
            st.session_state.login_mode = "login"

        # ======================================================
        # TRYB 1: STANDARDOWE LOGOWANIE
        # ======================================================
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
                        st.session_state.user_email = email
                        st.success(f"Witaj {name}!")
                        time.sleep(0.5)
                        st.rerun()
                    else: 
                        st.error("Błędny email lub hasło.")

            # --- TO JEST TEN NOWY PRZYCISK ---
            st.write("")
            if st.button("Nie pamiętam hasła ❓", use_container_width=True):
                st.session_state.login_mode = "forgot_request"
                st.rerun()
            # ---------------------------------

        # ======================================================
        # TRYB 2: RESET - KROK 1 (PODAJ EMAIL)
        # ======================================================
        elif st.session_state.login_mode == "forgot_request":
            st.subheader("Reset hasła (Krok 1/2)")
            st.info("Podaj adres e-mail powiązany z kontem. Wyślemy na niego kod weryfikacyjny.")
            
            email_reset = st.text_input("Twój Email")
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button("⬅️ Wróć"):
                    st.session_state.login_mode = "login"
                    st.rerun()
            with c_b2:
                if st.button("Wyślij kod 📩", type="primary"):
                    # 1. Generujemy kod w bazie
                    ok, wynik = crud.inicjuj_reset_hasla(email_reset)
                    
                    if ok:
                        # 2. Wysyłamy kod mailem (wynik = kod np. 123456)
                        with st.spinner("Wysyłanie e-maila..."):
                            sent_ok, msg = email_service.wyslij_email_resetu(email_reset, wynik)
                        
                        if sent_ok:
                            st.session_state.reset_email = email_reset # Zapamiętujemy email do następnego kroku
                            st.session_state.login_mode = "forgot_verify"
                            st.success("Kod został wysłany! Sprawdź skrzynkę.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg) # Błąd wysyłki maila
                    else:
                        # Błąd bazy (np. nie ma takiego emaila)
                        st.error(wynik)

        # ======================================================
        # TRYB 3: RESET - KROK 2 (WPISZ KOD I NOWE HASŁO)
        # ======================================================
        elif st.session_state.login_mode == "forgot_verify":
            st.subheader("Reset hasła (Krok 2/2)")
            st.success(f"Kod wysłano na: **{st.session_state.get('reset_email', '')}**")
            st.caption("Jeśli nie widzisz maila, sprawdź folder SPAM.")
            
            with st.form("reset_final"):
                kod = st.text_input("Kod weryfikacyjny (6 cyfr)")
                new_pass = st.text_input("Nowe hasło", type="password")
                new_pass2 = st.text_input("Powtórz nowe hasło", type="password")
                
                if st.form_submit_button("Zmień hasło 💾", type="primary"):
                    if new_pass != new_pass2:
                        st.error("Hasła nie są identyczne!")
                    elif len(new_pass) < 4:
                        st.error("Hasło jest za krótkie (min. 4 znaki).")
                    else:
                        # Finalizacja w bazie
                        email_u = st.session_state.get('reset_email')
                        ok, msg = crud.finalizuj_reset_hasla(email_u, kod, new_pass)
                        
                        if ok:
                            st.balloons()
                            st.success("Hasło zmienione pomyślnie! Możesz się teraz zalogować.")
                            time.sleep(3)
                            st.session_state.login_mode = "login"
                            st.rerun()
                        else:
                            st.error(msg) # np. Zły kod
            
            if st.button("Anuluj"):
                st.session_state.login_mode = "login"
                st.rerun()