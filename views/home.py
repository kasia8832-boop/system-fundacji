"""
WIDOK: KOKPIT (HOME) - WERSJA RESPONSYWNA
-----------------------------------------
Naprawiono błąd rozjeżdżania się kolumn na dużych ekranach.
Użyto vertical_alignment="bottom" zamiast sztywnych odstępów.
"""
import streamlit as st
import crud
from datetime import date
import pandas as pd

# --- KONFIGURACJA STYLU (CSS) ---
CUSTOM_CSS = """
<style>
    /* 1. UKRYCIE SIDEBARA */
    [data-testid="stSidebar"] { display: none; }
    
    /* 2. TŁO APLIKACJI */
    [data-testid="stAppViewContainer"] {
        background: rgb(0,0,0);
        background: linear-gradient(180deg, rgba(0,0,0,1) 0%, rgba(13,27,62,1) 100%);
        color: #e0e0e0;
    }

    /* 3. PRZYCISKI PRIMARY (Błękit) */
    .stButton > button[kind="primary"] {
        background-color: #3498db !important;
        border-color: #3498db !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2980b9 !important;
        border-color: #2980b9 !important;
    }
    
    /* 4. PRZYCISKI SECONDARY (Ciemne) */
    .stButton > button[kind="secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
    }

    /* 5. KONTENERY (Karty) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-color: #2c3e50 !important;
        background-color: rgba(13, 27, 62, 0.6);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* 6. TYTUŁY I LOGO */
    .fundacja-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #3498db, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0; padding: 0;
        line-height: 1.2;
    }
    .fundacja-subtitle {
        text-align: center;
        color: #5dade2;
        font-size: 1.1em;
        margin-top: 10px;
        margin-bottom: 20px;
        opacity: 0.9;
        letter-spacing: 1px;
    }

    /* 7. STATYSTYKI (DARK MODE) */
    .stat-card-dark {
        background-color: rgba(0, 0, 0, 0.4);
        border: 1px solid #2c3e50;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border-bottom: 4px solid;
    }
    .stat-val { font-size: 28px; font-weight: bold; color: white; }
    .stat-label { font-size: 13px; color: #bdc3c7; text-transform: uppercase; letter-spacing: 1px;}
    
    .blue-b { border-bottom-color: #3498db; }
    .green-b { border-bottom-color: #2ecc71; }
    .purple-b { border-bottom-color: #9b59b6; }
    .orange-b { border-bottom-color: #e67e22; }

    /* User Info Text */
    .user-text { font-size: 13px; color: #bdc3c7; text-align: right; margin-bottom: 2px; }
</style>
"""

def render_home():
    # Wstrzyknięcie stylu
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # --- 1. NAGŁÓWEK ---
    try:
        alerty = crud.pobierz_alerty_medyczne()
        liczba = len(alerty)
    except:
        liczba = 0

    c_left, c_center, c_right = st.columns([1, 6, 2.5])

    # LEWA: Dzwoneczek
    with c_left:
        lbl = f"🔔 {liczba}" if liczba > 0 else "🔔"
        btn_type = "primary" if liczba > 0 else "secondary"
        if st.button(lbl, type=btn_type, use_container_width=False, help="Powiadomienia"):
            st.session_state.current_module = "notifications"
            st.rerun()

    # ŚRODEK: Tytuł
    with c_center:
        st.markdown("<div class='fundacja-title'>Fundacja Przyjaciele Palucha</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='fundacja-subtitle'>Panel Zarządzania Schroniskiem</div>", unsafe_allow_html=True)

    # PRAWA: User + Wyloguj
    with c_right:
        role_pl = st.session_state.user_role.upper()
        cr_text, cr_btn = st.columns([2, 1])
        with cr_text:
             st.markdown(f"<div class='user-text'>Zalogowany:<br><b>{st.session_state.user_name}</b> <span style='color:#3498db'>({role_pl})</span></div>", unsafe_allow_html=True)
        with cr_btn:
            if st.button("Wyloguj", type="secondary", use_container_width=False):
                st.session_state.logged_in = False
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. WYSZUKIWARKA ---
    with st.container(border=True):
        c_search, c_btn = st.columns([7, 1])
        with c_search:
            query = st.text_input("Szukaj", placeholder="🔍 Wpisz imię psa lub numer chip...", label_visibility="collapsed")
        with c_btn:
            if st.button("SZUKAJ", type="primary", use_container_width=True):
                if query:
                    st.session_state.current_module = "registry"
                    st.session_state.view_mode = "list"
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. UKŁAD GŁÓWNY (POPRAWIONY) ---
    # Używamy vertical_alignment="bottom", aby prawa kolumna zawsze 'siedziała' na dole,
    # równo z dolnym kafelkiem lewej kolumny (Administracja).
    
    col_main, col_quick = st.columns([3, 1], vertical_alignment="bottom")

    # === LEWA STRONA (REJESTR + ADMIN) ===
    with col_main:
        
        # Kafel 1: REJESTR
        with st.container(border=True):
            ci, ct, ca = st.columns([0.3, 3, 1])
            with ci: st.markdown("## 🐾")
            with ct: 
                st.subheader("Rejestr Zwierząt")
                st.caption("Baza podopiecznych, edycja kartotek, historia leczenia.")
            with ca: 
                st.write("") 
                if st.button("Otwórz", key="btn_reg", use_container_width=True):
                    st.session_state.current_module = "registry"
                    st.session_state.view_mode = "list"
                    st.rerun()

        st.write("") # Odstęp

        # Kafel 2: ADMIN
        is_admin = (st.session_state.user_role == "Admin")
        with st.container(border=True):
            ci, ct, ca = st.columns([0.3, 3, 1])
            with ci: st.markdown("## ⚙️" if is_admin else "## 🔒")
            with ct:
                st.subheader("Administracja")
                st.caption("Użytkownicy, Słowniki, Baza Osób, Alerty." if is_admin else "Moduł dostępny tylko dla Administratora.")
            with ca:
                st.write("")
                if st.button("Otwórz", key="btn_adm", disabled=not is_admin, use_container_width=True):
                    st.session_state.current_module = "admin"
                    st.session_state.admin_mode = "dashboard"
                    st.rerun()

    # === PRAWA STRONA (SAMODZIELNIE DOPASOWUJE SIĘ DO DOŁU) ===
    with col_quick:
        st.markdown("##### ⚡ Szybkie Akcje")
        
        # Akcja 1: Nowy pies
        with st.container(border=True):
            st.write("**Nowy pies?**")
            st.caption("Utwórz nową kartę.")
            if st.button("➕ Przyjmij", type="primary", use_container_width=True):
                st.session_state.current_module = "registry"
                st.session_state.view_mode = "admission"
                st.rerun()
                
        # Akcja 2: Raporty (NOWE!)
        with st.container(border=True):
            st.write("**Analityka**")
            st.caption("Przeglądaj raporty i statystyki.")
            if st.button("📊 Raporty", type="secondary", use_container_width=True):
                st.session_state.current_module = "reports" # Kierujemy do nowego modułu
                st.rerun()
        
        if liczba > 0:
             st.markdown(f"<div style='text-align:center; color:#e74c3c; font-size:12px; margin-top:5px;'>⚠️ Zaległości: {liczba}</div>", unsafe_allow_html=True)
    
    # --- 4. STATYSTYKI ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    
    # Pobieranie "żywych" danych z bazy!
    stats = crud.get_dashboard_stats()
    
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)

    with c_s1:
        st.markdown(f"""
        <div class='stat-card-dark blue-b'>
            <div class='stat-val'>{stats['w_fundacji']}</div>
            <div class='stat-label'>Zwierzęta w fundacji</div>
        </div>
        """, unsafe_allow_html=True)

    with c_s2:
        st.markdown(f"""
        <div class='stat-card-dark green-b'>
            <div class='stat-val'>{stats['aktywni_wolo']}</div>
            <div class='stat-label'>Aktywni Wolontariusze</div>
        </div>
        """, unsafe_allow_html=True)

    with c_s3:
        st.markdown(f"""
        <div class='stat-card-dark purple-b'>
            <div class='stat-val'>{stats['aktywne_dt']}</div>
            <div class='stat-label'>Aktywne DT</div>
        </div>
        """, unsafe_allow_html=True)

    with c_s4:
        st.markdown(f"""
        <div class='stat-card-dark orange-b'>
            <div class='stat-val'>{stats['adopcje_miesiac']}</div>
            <div class='stat-label'>Adopcje (Miesiąc)</div>
        </div>
        """, unsafe_allow_html=True)