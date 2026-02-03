"""
ROUTER MODUŁU: ADMIN
--------------------
Główny punkt wejścia do panelu administracyjnego.
Styl: Nocne Niebo (Gradient + Błękit).
Funkcja: Narzuca styl globalny dla wszystkich pod-modułów admina.
"""
import streamlit as st
# Importujemy pod-moduły
from views.admin_modules import dashboard, access_control, people_db, dictionaries, alerts_config

# --- GLOBALNY STYL DLA CAŁEGO ADMINA ---
CUSTOM_CSS = """
<style>
    /* Ukrycie Sidebara */
    [data-testid="stSidebar"] { display: none; }

    /* Tło Gradientowe */
    [data-testid="stAppViewContainer"] {
        background: rgb(0,0,0);
        background: linear-gradient(180deg, rgba(0,0,0,1) 0%, rgba(13,27,62,1) 100%);
        color: #e0e0e0;
    }

    /* Nagłówek Admina */
    .admin-title {
        font-size: 2.2em;
        font-weight: 800;
        color: #ecf0f1;
        margin: 0;
        padding: 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .admin-subtitle {
        font-size: 1em;
        color: #3498db; /* Błękitny akcent */
        margin-top: -5px;
        margin-bottom: 20px;
        font-weight: 500;
    }

    /* Kontenery (Karty) - Dotyczy wszystkich podmodułów */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: rgba(13, 27, 62, 0.6);
        border: 1px solid #2c3e50;
        border-radius: 10px;
        padding: 20px;
    }

    /* Przyciski */
    .stButton > button[kind="primary"] {
        background-color: #3498db !important;
        border-color: #3498db !important;
        color: white !important;
        font-weight: bold;
    }
    .stButton > button[kind="secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
    }
    
    /* Inputy i Tabele - poprawa czytelności na ciemnym tle */
    .stTextInput > div > div > input {
        background-color: rgba(0,0,0,0.3);
        color: white;
    }
    .stSelectbox > div > div > div {
        background-color: rgba(0,0,0,0.3);
        color: white;
    }
</style>
"""

def render_admin():
    # Wstrzyknięcie stylu
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    role = st.session_state.user_role
    
    # 1. SECURITY CHECK - Dom Tymczasowy w ogóle tu nie wchodzi
    if role == "DT": 
        st.error("⛔ BRAK DOSTĘPU - Ten moduł jest niedostępny dla Domów Tymczasowych.")
        if st.button("Wróć"):
            st.session_state.current_module = "home"
            st.rerun()
        st.stop()
        
    # 2. NAGŁÓWEK PANELU
    c_back, c_title = st.columns([1, 6], vertical_alignment="center")
    with c_back: 
        if st.button("⬅️ Menu", help="Wróć do głównego menu", type="secondary", use_container_width=True): 
            st.session_state.current_module = "home"
            st.rerun()
            
    with c_title: 
        st.markdown(f"""
        <div class="admin-title">Panel Administracyjny</div>
        <div class="admin-subtitle">Zalogowano jako: {role}</div>
        """, unsafe_allow_html=True)
    
    st.divider()

    # 3. ROUTER ADMINA
    mode = st.session_state.admin_mode
    
    # Przycisk powrotu do pulpitu admina (jeśli jesteśmy w podmodule)
    if mode != "dashboard":
        if st.button("⬅️ Wróć do Pulpitu Admina", type="secondary"):
            st.session_state.admin_mode = "dashboard"
            st.rerun()
        st.write("") # Odstęp

    # --- LOGIKA MODUŁÓW ---
    
    # Renderujemy odpowiedni moduł - dzięki CUSTOM_CSS powyżej, 
    # wszystkie one będą miały ciemne tło i błękitne przyciski!
    
    if mode == "dashboard":
        dashboard.render_dashboard()
        
    elif mode == "access":
        # Tylko "Admin" ma dostęp do haseł i kont
        if role != "Admin": 
            st.error("⛔ Brak uprawnień do zarządzania kontami (Tylko Admin).")
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