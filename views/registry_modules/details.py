"""
MODUŁ REJESTRU: SZCZEGÓŁY (LAYOUT)
----------------------------------
Wersja 3.2: Większy tytuł, styl mikro-kart (Info Tiles) pod zdjęciem.
"""
import streamlit as st
import crud
from views.registry_modules.details_components import side_panel, top_bar, tab_info, tab_medical, tab_history

# --- KONFIGURACJA STYLU (Gradient Nocny) ---
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

    /* 3. PRZYCISKI */
    .stButton > button[kind="primary"] {
        background-color: #3498db !important;
        border-color: #3498db !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton > button[kind="secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
        padding: 5px 15px;
    }

    /* 4. TYTUŁ ZWIERZĘCIA (JESZCZE WIĘKSZY) */
    .animal-title {
        text-align: center;
        text-transform: uppercase;
        font-size: 3.5em; /* Powiększono z 2.5em */
        font-weight: 900;
        letter-spacing: 3px;
        background: -webkit-linear-gradient(45deg, #ecf0f1, #bdc3c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0; padding: 0;
        line-height: 1.1;
    }

    /* 5. RAMKA ZDJĘCIA (Czarna, prosta) */
    .profile-photo {
        border: 4px solid #080808;
        border-radius: 4px; /* Mniejsze zaokrąglenie, bardziej pro */
        padding: 0;
        margin-bottom: 15px;
        background-color: transparent;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    
    /* 6. MIKRO-KARTY (INFO TILES) - NOWOŚĆ */
    .info-tile {
        background-color: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #3498db; /* Błękitny akcent */
        border-radius: 4px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .info-label {
        font-size: 11px;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 2px;
    }
    .info-value {
        font-size: 14px;
        color: #ecf0f1;
        font-weight: 500;
    }

    /* 7. ZAKŁADKI */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 5px;
        color: #bdc3c7;
        padding: 5px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
</style>
"""

def render_details():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # 1. Weryfikacja ID
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Błąd: Brak ID zwierzęcia.")
        st.button("Wróć", on_click=lambda: st.session_state.update(view_mode="list"))
        st.stop()
        
    # 2. Pobieranie danych
    zwierze_obj = crud.pobierz_szczegoly_zwierzecia(id_zw)
    if not zwierze_obj: 
        st.error("Nie znaleziono zwierzęcia.")
        return
    
    # Konwersja na słownik
    r = {k: v for k, v in vars(zwierze_obj).items() if not k.startswith('_')}
    r['ID_Zwierze'] = zwierze_obj.IDZwierze 

    # --- UKŁAD STRONY ---
    top_bar.render_top_bar(r, id_zw)

    col_left, col_right = st.columns([1.5, 3.5])

    with col_left:
        side_panel.render_side_panel(r)

    with col_right:
        t1, t2, t3 = st.tabs(["📄 Dane", "💉 Zdrowie", "📜 Historia"])
        with t1: tab_info.render_tab(r)
        with t2: tab_medical.render_tab(r)
        with t3: tab_history.render_tab(id_zw)