"""
MODUŁ ADMINA: DASHBOARD (PULPIT)
--------------------------------
Strona startowa panelu administracyjnego.
Wyświetla kafelki/przyciski nawigacyjne kierujące do poszczególnych
sekcji zarządzania (Dostęp, Osoby, Słowniki).
"""
# views/admin_modules/dashboard.py
import streamlit as st

def render_dashboard():
    role = st.session_state.user_role
    st.markdown("### Panel Zarządzania")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("🔐 Dostęp")
        st.caption("Użytkownicy systemu, hasła.")
        # Przycisk aktywny TYLKO dla Admina
        if role == "Administrator":
            if st.button("Zarządzaj Dostępem", use_container_width=True): 
                st.session_state.admin_mode = "access"
                st.rerun()
        else:
            st.button("🔒 Brak dostępu", disabled=True, use_container_width=True)
            
    with c2:
        st.subheader("👥 Baza Osób")
        st.caption("DT, Adoptujący, Wolontariusze.")
        # Dostępne dla wszystkich (Wolontariusz w trybie READ-ONLY)
        if st.button("Zarządzaj Osobami", use_container_width=True): 
            st.session_state.admin_mode = "users"
            st.rerun()
            
    with c3:
        st.subheader("📚 Słowniki")
        st.caption("Edycja list rozwijanych.")
        if st.button("Słowniki", use_container_width=True): 
            st.session_state.admin_mode = "dictionaries"
            st.rerun()