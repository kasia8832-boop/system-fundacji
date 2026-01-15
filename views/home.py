"""
WIDOK: KOKPIT (HOME)
--------------------
Strona startowa po zalogowaniu.
Wyświetla przyciski nawigacyjne do innych modułów (Rejestr, Admin)
zależnie od uprawnień użytkownika (Wolontariusz vs Admin).
"""



import streamlit as st

def render_home():
    st.title("🏠 Kokpit")
    
    # 1. ZMIANA TUTAJ: "Admin" -> "Administrator"
    role_color = "red" if st.session_state.user_role == "Administrator" else "green"
    
    st.markdown(f"Zalogowany jako: **{st.session_state.user_name}** <span style='background-color:{role_color}; color:white; padding: 2px 6px; border-radius: 4px; font-size: 12px;'>{st.session_state.user_role.upper()}</span>", unsafe_allow_html=True)
    st.divider()
    
    # 2. ZMIANA TUTAJ: "Admin" -> "Administrator"
    if st.session_state.user_role == "Administrator":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🐾 Rejestr Podopiecznych")
            if st.button("Otwórz Rejestr ➡️", key="b1", use_container_width=True, type="primary"):
                st.session_state.current_module = "registry"
                st.rerun()
        with col2:
            st.subheader("⚙️ Panel Administracyjny")
            if st.button("Otwórz Panel ➡️", key="b2", use_container_width=True):
                st.session_state.current_module = "admin"
                st.rerun()
    else:
        # Widok dla Wolontariusza / DT / Pracownika
        c_l, c_c, c_r = st.columns([1, 2, 1])
        with c_c:
            st.subheader("🐾 Rejestr Podopiecznych")
            if st.button("Otwórz Rejestr ➡️", key="b1_vol", use_container_width=True, type="primary"):
                st.session_state.current_module = "registry"
                st.rerun()
            
            # Opcjonalnie: Ukrywamy info o braku uprawnień, żeby było czyściej
            # st.info("ℹ️ Nie masz uprawnień do Panelu Administracyjnego.")

    st.divider()
    if st.button("Wyloguj"): 
        st.session_state.logged_in = False
        st.session_state.user_name = "User"
        # Czyścimy też email przy wylogowaniu
        if 'user_email' in st.session_state:
            del st.session_state['user_email']
        st.rerun()