"""
ROUTER MODUŁU: ADMIN
--------------------
Główny punkt wejścia do panelu administracyjnego.
Weryfikuje uprawnienia (Security Check) i kieruje do odpowiedniego pod-modułu
(Dashboard, Dostęp, Ludzie, Słowniki).
"""
import streamlit as st
# Importujemy nasze nowe pod-moduły
from views.admin_modules import dashboard, access_control, people_db, dictionaries, alerts_config

def render_admin():
    role = st.session_state.user_role
    
    # 1. SECURITY CHECK - Dom Tymczasowy w ogóle tu nie wchodzi
    if role == "Dom Tymczasowy":
        st.error("⛔ BRAK DOSTĘPU - Ten moduł jest niedostępny dla Domów Tymczasowych.")
        if st.button("Wróć"):
            st.session_state.current_module = "home"
            st.rerun()
        st.stop()
        
    # 2. Pasek nawigacji
    c_n, c_t = st.columns([1, 6])
    with c_n: 
        if st.button("🏠 Menu Gł.", use_container_width=True): 
            st.session_state.current_module = "home"
            st.rerun()
    with c_t: 
        st.subheader(f"Panel Administracyjny ({role})")
    
    st.divider()

    # 3. Router Admina
    mode = st.session_state.admin_mode
    # --- PRZYCISK POWROTU DO PULPITU ADMINA ---
    # Jeśli jesteśmy w jakimkolwiek pod-module (nie dashboard), pokaż przycisk powrotu
    if mode != "dashboard":
        if st.button("⬅️ Wróć do Pulpitu Admina"):
            st.session_state.admin_mode = "dashboard"
            st.rerun()
        st.write("") # Odstęp
    # --------------------------------------------------
    if mode == "dashboard":
        dashboard.render_dashboard()
        
    elif mode == "access":
        # DODATKOWE ZABEZPIECZENIE: Tylko Admin wchodzi w hasła
        if role != "Administrator": # Pracownik i Wolontariusz nie mogą
            st.error("⛔ Brak uprawnień do zarządzania kontami.")
        else:
            access_control.render_access_control()
        
    elif mode == "users":
        people_db.render_people_db()
        
    elif mode == "dictionaries":
        dictionaries.render_dictionaries()

    elif mode == "alerts":
        alerts_config.render_alerts_config()
        
    else:
        st.warning(f"Nieznany tryb admina: {mode}")