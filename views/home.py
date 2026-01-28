"""
WIDOK: KOKPIT (HOME)
--------------------
Strona startowa po zalogowaniu.
Wersja 2.0: Poprawiono nazwę roli "Admin" zamiast "Administrator".
"""
import streamlit as st
import crud

def render_home():
    # --- NAGŁÓWEK Z POWIADOMIENIAMI ---
    col_title, col_notify = st.columns([5, 1])
    
    with col_title:
        st.title("🏠 Kokpit")
        
    with col_notify:
        # Pobieramy alerty (funkcja już działa w crud.py)
        try:
            alerty = crud.pobierz_alerty_medyczne()
            liczba = len(alerty)
        except Exception:
            # Zabezpieczenie gdyby crud rzucił błąd
            liczba = 0
        
        # Stylizacja przycisku w zależności od liczby
        label = "🔔 Brak"
        type_btn = "secondary"
        
        if liczba > 0:
            label = f"🔔 ({liczba})"
            type_btn = "primary" # Czerwony kolor przyciąga uwagę
            
        if st.button(label, type=type_btn, use_container_width=True):
            st.session_state.current_module = "notifications"
            st.rerun()

    # --- PONIŻEJ LOGIKA WYŚWIETLANIA ROLI I MENU ---
    
    # 1. Poprawiony warunek dla koloru (Admin)
    role_color = "red" if st.session_state.user_role == "Admin" else "green"
    
    st.markdown(f"Zalogowany jako: **{st.session_state.user_name}** <span style='background-color:{role_color}; color:white; padding: 2px 6px; border-radius: 4px; font-size: 12px;'>{st.session_state.user_role.upper()}</span>", unsafe_allow_html=True)
    st.divider()
    
    # 2. KLUCZOWA POPRAWKA: Sprawdzamy "Admin", a nie "Administrator"
    if st.session_state.user_role == "Admin":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🐾 Rejestr Podopiecznych")
            if st.button("Otwórz Rejestr ➡️", key="b1", use_container_width=True, type="primary"):
                st.session_state.current_module = "registry"
                st.session_state.view_mode = "list" # Reset widoku na listę
                st.rerun()
        with col2:
            st.subheader("⚙️ Panel Administracyjny")
            if st.button("Otwórz Panel ➡️", key="b2", use_container_width=True):
                st.session_state.current_module = "admin"
                st.session_state.admin_mode = "dashboard" # Reset widoku dashboardu
                st.rerun()
    else:
        # Widok dla Wolontariusza / DT
        c_l, c_c, c_r = st.columns([1, 2, 1])
        with c_c:
            st.subheader("🐾 Rejestr Podopiecznych")
            if st.button("Otwórz Rejestr ➡️", key="b1_vol", use_container_width=True, type="primary"):
                st.session_state.current_module = "registry"
                st.session_state.view_mode = "list"
                st.rerun()
            
            st.write("")
            st.info("ℹ️ Panel Administracyjny dostępny tylko dla Administratora.")

    st.divider()
    if st.button("Wyloguj"): 
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = "User"
        st.rerun()