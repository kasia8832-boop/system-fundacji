"""
MODUŁ ADMINA: DASHBOARD (PULPIT)
--------------------------------
Strona startowa panelu administracyjnego.
Wyświetla kafelki/przyciski nawigacyjne kierujące do poszczególnych
sekcji zarządzania (Dostęp, Osoby, Słowniki).
"""
import streamlit as st

def render_dashboard():
    st.markdown("### Panel Zarządzania")
    st.info("Wybierz moduł, którym chcesz zarządzać.")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("🔐 Dostęp")
        st.caption("Użytkownicy systemu, hasła, role.")
        if st.button("Zarządzaj Dostępem", use_container_width=True): 
            st.session_state.admin_mode = "access"
            st.rerun()
            
    with c2:
        st.subheader("👥 Baza Osób")
        st.caption("Domy Tymczasowe, Adoptujący, Wolontariusze.")
        if st.button("Zarządzaj Osobami", use_container_width=True): 
            st.session_state.admin_mode = "users"
            st.rerun()
            
    with c3:
        st.subheader("📚 Słowniki")
        st.caption("Edycja list rozwijanych (Gatunki, Statusy).")
        if st.button("Edytuj Słowniki", use_container_width=True): 
            st.session_state.admin_mode = "dictionaries"
            st.rerun()