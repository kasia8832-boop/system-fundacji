"""
MODUŁ ADMINA: DASHBOARD (PULPIT)
--------------------------------
Wersja 2.0: Poprawiono nazwę roli na 'Admin'.
"""
import streamlit as st

def render_dashboard():
    role = st.session_state.user_role
    st.markdown("### 🎛️ Panel Zarządzania")
    st.info("Wybierz obszar, którym chcesz zarządzać.")
    
    # --- WIERSZ 1 (Dostęp i Osoby) ---
    c1, c2 = st.columns(2)
    
    with c1:
        with st.container(border=True):
            st.subheader("🔐 Dostęp i Konta")
            st.caption("Zarządzanie użytkownikami systemu i hasłami.")
            
            # --- POPRAWKA: Admin zamiast Administrator ---
            if role == "Admin":
                if st.button("Zarządzaj Dostępem ➡️", use_container_width=True): 
                    st.session_state.admin_mode = "access"
                    st.rerun()
            else:
                st.button("🔒 Brak uprawnień", disabled=True, use_container_width=True)
            
    with c2:
        with st.container(border=True):
            st.subheader("👥 Baza Osób")
            st.caption("Domy Tymczasowe, Adoptujący, Wolontariusze.")
            
            if st.button("Zarządzaj Osobami ➡️", use_container_width=True): 
                st.session_state.admin_mode = "users"
                st.rerun()
            
    # --- WIERSZ 2 (Słowniki i Powiadomienia) ---
    c3, c4 = st.columns(2)
    
    with c3:
        with st.container(border=True):
            st.subheader("📚 Słowniki Danych")
            st.caption("Edycja gatunków, statusów i źródeł.")
            
            if st.button("Edytuj Słowniki ➡️", use_container_width=True): 
                st.session_state.admin_mode = "dictionaries"
                st.rerun()

    with c4:
        with st.container(border=True):
            st.subheader("🔔 Powiadomienia")
            st.caption("Konfiguracja terminów szczepień i alertów.")
            
            if st.button("Konfiguruj Alerty ➡️", use_container_width=True): 
                st.session_state.admin_mode = "alerts"
                st.rerun()