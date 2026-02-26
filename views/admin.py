"""
ROUTER MODUŁU: ADMIN
--------------------
Wersja ostateczna v3: Celowanie w [data-testid="stFormSubmitButton"] aby zabić czerwień w formularzu.
"""
import streamlit as st
from views.admin_modules import dashboard, access_control, people_db, dictionaries, alerts_config
from views import reports

# --- GLOBALNY STYL (NOCNE NIEBO) ---
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
        font-size: 2.2em; font-weight: 800; color: #ecf0f1;
        margin: 0; padding: 0; text-transform: uppercase; letter-spacing: 2px; text-align: center;
    }
    .user-info-top {
        text-align: right; font-size: 0.85em; color: #7f8c8d;
        margin-bottom: -15px; font-family: monospace;
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: rgba(13, 27, 62, 0.6);
        border: 1px solid #2c3e50;
        border-radius: 10px;
        padding: 20px;
    }

    /* --- ZAKŁADKI (TO JUŻ DZIAŁA, NIE RUSZAMY) --- */
    .stTabs [aria-selected="true"] { color: #3498db !important; background-color: transparent !important; }
    [data-baseweb="tab-highlight"] { background-color: #3498db !important; height: 3px !important; }
    .stTabs [data-baseweb="tab"] { color: #7f8c8d !important; background-color: transparent !important; border: none !important; }
    .stTabs [data-baseweb="tab"]:focus { outline: none !important; box-shadow: none !important; }


    /* --- WALKA Z PRZYCISKIEM FORMULARZA (NOWOŚĆ) --- */

    /* 1. Celujemy w ZWYKŁE przyciski ORAZ przyciski FORMULARZA */
    .stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button {
        background-color: #3498db !important;
        border-color: #3498db !important;
        color: white !important;
    }

    /* 2. Obsługa najechania (Hover), kliknięcia (Active) i focusu */
    .stButton > button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] > button:hover,
    .stButton > button[kind="primary"]:active,
    [data-testid="stFormSubmitButton"] > button:active,
    .stButton > button[kind="primary"]:focus,
    [data-testid="stFormSubmitButton"] > button:focus {
         background-color: #2980b9 !important; /* Ciemniejszy niebieski */
         border-color: #2980b9 !important;
         box-shadow: none !important;
         color: white !important;
         outline: none !important;
    }

    /* Przyciski Secondary */
    .stButton > button[kind="secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
    }

    /* Inputy */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: rgba(0,0,0,0.3);
        color: white;
    }
</style>
"""

def render_admin():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    role = st.session_state.user_role
    mode = st.session_state.admin_mode
    
    if role == "DT": 
        st.error("⛔ BRAK DOSTĘPU")
        if st.button("Wróć"):
            st.session_state.current_module = "home"
            st.rerun()
        st.stop()
        
    tytuly_modulow = {
        "dashboard": "Panel Administracyjny",
        "access": "Dostęp i Konta",
        "users": "Baza Osób",
        "dictionaries": "Słowniki Danych",
        "alerts": "Konfiguracja Alertów",
        "reports": "Raporty Analityczne" # <--- Dodana linijka
    }
    aktualny_tytul = tytuly_modulow.get(mode, "Panel Administracyjny")

    # NAGŁÓWEK
    c_dummy, c_user = st.columns([8, 2])
    with c_user:
        st.markdown(f"<div class='user-info-top'>Zalogowano jako: {role}</div>", unsafe_allow_html=True)
        
    c_nav, c_title, c_void = st.columns([1.5, 7, 1.5], vertical_alignment="center")
    
    with c_nav:
        if st.button("🏠 Menu", help="Wróć do głównego ekranu", type="secondary", use_container_width=True):
            st.session_state.current_module = "home"
            st.rerun()
            
        if mode != "dashboard":
            if st.button("⬅️ Panel Adm.", help="Wróć do pulpitu admina", type="secondary", use_container_width=True):
                st.session_state.admin_mode = "dashboard"
                st.rerun()
            
    with c_title:
        st.markdown(f"<div class='admin-title'>{aktualny_tytul}</div>", unsafe_allow_html=True)

    st.divider()

    if mode == "dashboard": dashboard.render_dashboard()
    elif mode == "access":
        if role != "Admin": st.error("⛔ Tylko Admin.")
        else: access_control.render_access_control()
    elif mode == "users": people_db.render_people_db()
    elif mode == "dictionaries": dictionaries.render_dictionaries()
    elif mode == "alerts": alerts_config.render_alerts_config()
    else: st.warning(f"Nieznany tryb: {mode}")
"""
ROUTER MODUŁU: ADMIN
--------------------
Wersja ostateczna v3: Celowanie w [data-testid="stFormSubmitButton"] aby zabić czerwień w formularzu.
"""
import streamlit as st
from views.admin_modules import dashboard, access_control, people_db, dictionaries, alerts_config

# --- GLOBALNY STYL (NOCNE NIEBO) ---
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
        font-size: 2.2em; font-weight: 800; color: #ecf0f1;
        margin: 0; padding: 0; text-transform: uppercase; letter-spacing: 2px; text-align: center;
    }
    .user-info-top {
        text-align: right; font-size: 0.85em; color: #7f8c8d;
        margin-bottom: -15px; font-family: monospace;
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: rgba(13, 27, 62, 0.6);
        border: 1px solid #2c3e50;
        border-radius: 10px;
        padding: 20px;
    }

    /* --- ZAKŁADKI (TO JUŻ DZIAŁA, NIE RUSZAMY) --- */
    .stTabs [aria-selected="true"] { color: #3498db !important; background-color: transparent !important; }
    [data-baseweb="tab-highlight"] { background-color: #3498db !important; height: 3px !important; }
    .stTabs [data-baseweb="tab"] { color: #7f8c8d !important; background-color: transparent !important; border: none !important; }
    .stTabs [data-baseweb="tab"]:focus { outline: none !important; box-shadow: none !important; }


    /* --- WALKA Z PRZYCISKIEM FORMULARZA (NOWOŚĆ) --- */

    /* 1. Celujemy w ZWYKŁE przyciski ORAZ przyciski FORMULARZA */
    .stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button {
        background-color: #3498db !important;
        border-color: #3498db !important;
        color: white !important;
    }

    /* 2. Obsługa najechania (Hover), kliknięcia (Active) i focusu */
    .stButton > button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] > button:hover,
    .stButton > button[kind="primary"]:active,
    [data-testid="stFormSubmitButton"] > button:active,
    .stButton > button[kind="primary"]:focus,
    [data-testid="stFormSubmitButton"] > button:focus {
         background-color: #2980b9 !important; /* Ciemniejszy niebieski */
         border-color: #2980b9 !important;
         box-shadow: none !important;
         color: white !important;
         outline: none !important;
    }

    /* Przyciski Secondary */
    .stButton > button[kind="secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
    }

    /* Inputy */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: rgba(0,0,0,0.3);
        color: white;
    }
</style>
"""

def render_admin():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    role = st.session_state.user_role
    mode = st.session_state.admin_mode
    
    if role == "DT": 
        st.error("⛔ BRAK DOSTĘPU")
        if st.button("Wróć"):
            st.session_state.current_module = "home"
            st.rerun()
        st.stop()
        
    tytuly_modulow = {
        "dashboard": "Panel Administracyjny",
        "access": "Dostęp i Konta",
        "users": "Baza Osób",
        "dictionaries": "Słowniki Danych",
        "alerts": "Konfiguracja Alertów"
    }
    aktualny_tytul = tytuly_modulow.get(mode, "Panel Administracyjny")

    # NAGŁÓWEK
    c_dummy, c_user = st.columns([8, 2])
    with c_user:
        st.markdown(f"<div class='user-info-top'>Zalogowano jako: {role}</div>", unsafe_allow_html=True)
        
    c_nav, c_title, c_void = st.columns([1.5, 7, 1.5], vertical_alignment="center")
    
    with c_nav:
        if st.button("🏠 Menu", help="Wróć do głównego ekranu", type="secondary", use_container_width=True):
            st.session_state.current_module = "home"
            st.rerun()
            
        if mode != "dashboard":
            if st.button("⬅️ Panel Adm.", help="Wróć do pulpitu admina", type="secondary", use_container_width=True):
                st.session_state.admin_mode = "dashboard"
                st.rerun()
            
    with c_title:
        st.markdown(f"<div class='admin-title'>{aktualny_tytul}</div>", unsafe_allow_html=True)

    st.divider()

    if mode == "dashboard": dashboard.render_dashboard()
    elif mode == "access":
        if role != "Admin": st.error("⛔ Tylko Admin.")
        else: access_control.render_access_control()
    elif mode == "users": people_db.render_people_db()
    elif mode == "dictionaries": dictionaries.render_dictionaries()
    elif mode == "alerts": alerts_config.render_alerts_config()
    elif mode == "reports": reports.render_reports() # <--- Dodana linijka
    else: st.warning(f"Nieznany tryb: {mode}")