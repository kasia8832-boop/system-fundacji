"""
ROUTER MODUŁU: ADMIN
--------------------
Główny punkt wejścia do panelu administracyjnego.
Weryfikuje uprawnienia (Security Check) i kieruje do odpowiedniego pod-modułu
(Dashboard, Dostęp, Ludzie, Słowniki).
"""
import streamlit as st
# Importujemy nasze nowe pod-moduły
from views.admin_modules import dashboard, access_control, people_db, dictionaries

def render_admin():
    # 1. SECURITY CHECK - Sprawdzamy czy user to Admin
    if st.session_state.user_role != "Admin":
        st.error("⛔ BRAK DOSTĘPU - Ten moduł jest tylko dla Administratorów.")
        st.stop()
        
    # 2. Pasek nawigacji powrotu do Home
    c_n, c_t = st.columns([1, 6])
    with c_n: 
        if st.button("🏠 Menu Gł.", use_container_width=True): 
            st.session_state.current_module = "home"
            st.rerun()
    with c_t: 
        st.subheader("Panel Administracyjny")
    
    st.divider()

    # 3. Router Admina
    mode = st.session_state.admin_mode
    
    if mode == "dashboard":
        dashboard.render_dashboard()
        
    elif mode == "access":
        access_control.render_access_control()
        
    elif mode == "users":
        people_db.render_people_db()
        
    elif mode == "dictionaries":
        dictionaries.render_dictionaries()
        
    else:
        st.warning(f"Nieznany tryb admina: {mode}")
        if st.button("Resetuj widok"):
            st.session_state.admin_mode = "dashboard"
            st.rerun()