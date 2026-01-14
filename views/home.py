"""
WIDOK: KOKPIT (HOME)
--------------------
Strona startowa po zalogowaniu.
Wyświetla przyciski nawigacyjne do innych modułów (Rejestr, Admin)
zależnie od uprawnień użytkownika (Wolontariusz vs Admin).
"""



import streamlit as st

def render_home():
    st.title("🏠 Kokpit!")
    role_color = "red" if st.session_state.user_role == "Admin" else "green"
    st.markdown(f"Zalogowany jako: **{st.session_state.user_name}** <span style='background-color:{role_color}; color:white; padding: 2px 6px; border-radius: 4px; font-size: 12px;'>{st.session_state.user_role.upper()}</span>", unsafe_allow_html=True)
    st.divider()
    
    if st.session_state.user_role == "Admin":
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
        c_l, c_c, c_r = st.columns([1, 2, 1])
        with c_c:
            st.subheader("🐾 Rejestr Podopiecznych")
            if st.button("Otwórz Rejestr ➡️", key="b1_vol", use_container_width=True, type="primary"):
                st.session_state.current_module = "registry"
                st.rerun()
            st.info("ℹ️ Nie masz uprawnień do Panelu Administracyjnego.")

    st.divider()
    if st.button("Wyloguj"): 
        st.session_state.logged_in = False
        st.rerun()