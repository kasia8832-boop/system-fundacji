"""
MODUŁ: REJESTR ZWIERZĄT
-----------------------
Lista podopiecznych z zaawansowanym filtrowaniem (Gatunek, Status, Osoby).
Wersja 2.2: Dodano filtry Opiekuna i Nadzorcy.
"""
import streamlit as st
import pandas as pd
import crud
from datetime import date
from views.registry_modules import admission, details, editing, adoption

# --- KONFIGURACJA STYLU (Gradient Nocny + Błękit) ---
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
    
    /* 4. PRZYCISKI SECONDARY (Mała strzałka) */
    .stButton > button[kind="secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
    }

    /* 5. TYTUŁ NA ŚRODKU */
    .registry-title {
        text-align: center;
        font-size: 2.2em;
        font-weight: 700;
        color: #ecf0f1;
        margin-bottom: 5px;
        margin-top: -10px;
    }

    /* 6. TABELA (DATAFRAME) */
    [data-testid="stDataFrame"] {
        background-color: rgba(13, 27, 62, 0.6);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2c3e50;
    }
    
    /* 7. EXPANDER (Filtry) */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #bdc3c7;
    }
</style>
"""

# Funkcja pomocnicza do obliczania wieku
def oblicz_wiek(data_ur):
    if not data_ur:
        return "-"
    try:
        dt = pd.to_datetime(data_ur)
        lata = date.today().year - dt.year
        return f"{lata} lat"
    except:
        return "-"

def render_registry():
    # Wstrzyknięcie stylu
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Inicjalizacja stanu
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "list"
    if 'active_animal_id' not in st.session_state:
        st.session_state.active_animal_id = None

    # --- ROUTING WIDOKÓW ---
    mode = st.session_state.view_mode

    if mode == "list":
        render_list_view()
    elif mode == "details":
        details.render_details()
    elif mode == "admission":
        admission.render_admission()
    elif mode == "edit":
        editing.render_edit()
    elif mode == "adoption_process":
        adoption.render_adoption()

def render_list_view():
    # --- 1. NAGŁÓWEK ---
    c_back, c_title, c_void = st.columns([1, 6, 1])
    
    with c_back:
        if st.button("⬅️", help="Wróć do Kokpitu", use_container_width=False, type="secondary"):
            st.session_state.current_module = "home"
            st.rerun()
            
    with c_title:
        st.markdown("<div class='registry-title'>Rejestr Zwierząt</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. PASEK NARZĘDZI ---
    c_search, c_add = st.columns([5, 1.5], vertical_alignment="bottom")
    
    with c_search:
        search_query = st.text_input("Szukaj", placeholder="Wpisz imię, rasę lub nr chip...", label_visibility="collapsed")
    
    with c_add:
        if st.button("➕ Przyjmij", type="primary", use_container_width=True):
            st.session_state.view_mode = "admission"
            st.rerun()

    # --- 3. POBRANIE DANYCH ---
    # Pobieramy dane TUTAJ, żeby użyć ich do zbudowania list w filtrach
    df = crud.pobierz_rejestr_rozszerzony()

    if df.empty:
        st.info("Baza jest pusta. Dodaj pierwsze zwierzę.")
        return

    # Obliczanie wieku
    df['Wiek'] = df['DataUrodzenia'].apply(oblicz_wiek)

    # --- 4. FILTRY ZAAWANSOWANE (Gatunek, Status, Opiekun, Nadzór) ---
    with st.expander("🔍 Filtry", expanded=False):
        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        
        # Kolumna 1: Gatunek (ze słownika)
        with c_f1:
            try:
                opcje_gat = crud.pobierz_slownik("gatunek")
            except:
                opcje_gat = ["Pies", "Kot"]
            sel_gatunek = st.multiselect("Gatunek", opcje_gat)
            
        # Kolumna 2: Status (ze słownika)
        with c_f2:
            try:
                opcje_stat = crud.pobierz_slownik("status")
            except:
                opcje_stat = ["Do adopcji", "W trakcie leczenia", "Adoptowany"]
            sel_status = st.multiselect("Status", opcje_stat)

        # Kolumna 3: Opiekun (z danych w tabeli - tylko ci co mają psy)
        with c_f3:
            # Wyciągamy unikalne nazwiska opiekunów z obecnej bazy, usuwamy puste (None)
            lista_opiekunow = sorted(df['OpiekunNazwa'].dropna().unique().tolist())
            sel_opiekun = st.multiselect("Opiekun (Adopcja)", lista_opiekunow)

        # Kolumna 4: Nadzorca (z danych w tabeli)
        with c_f4:
            lista_nadzorcow = sorted(df['NadzorcaNazwa'].dropna().unique().tolist())
            sel_nadzor = st.multiselect("Nadzór / Wolo.", lista_nadzorcow)

    st.write("") # Odstęp

    # --- 5. LOGIKA FILTROWANIA ---
    
    # A. Wyszukiwarka tekstowa
    if search_query:
        q = search_query.lower()
        mask = (
            df['Imie'].str.lower().str.contains(q, na=False) |
            df['Rasa'].str.lower().str.contains(q, na=False) |
            df['NrChip'].str.lower().str.contains(q, na=False)
        )
        df = df[mask]
        
    # B. Filtry z expandera
    if sel_gatunek:
        df = df[df['Gatunek'].isin(sel_gatunek)]
        
    if sel_status:
        df = df[df['StatusZwierzecia'].isin(sel_status)]

    if sel_opiekun:
        df = df[df['OpiekunNazwa'].isin(sel_opiekun)]
        
    if sel_nadzor:
        df = df[df['NadzorcaNazwa'].isin(sel_nadzor)]

    # --- 6. TABELA ---
    column_cfg = {
        "IDZwierze": None,         
        "DataUrodzenia": None,     
        "NrChip": None,            
        
        "Imie": st.column_config.TextColumn("Imię", width="medium"),
        "Gatunek": st.column_config.TextColumn("Gatunek", width="small"),
        "Rasa": st.column_config.TextColumn("Rasa", width="medium"),
        "Plec": st.column_config.TextColumn("Płeć", width="small"),
        "Wiek": st.column_config.TextColumn("Wiek", width="small"),
        
        "StatusZwierzecia": st.column_config.TextColumn("Status", width="medium"),
        
        "OpiekunNazwa": st.column_config.TextColumn("🏠 Opiekun", width="medium"),
        "NadzorcaNazwa": st.column_config.TextColumn("🩺 Nadzór", width="medium"),
    }
    
    cols_to_show = ["Imie", "Gatunek", "Rasa", "Plec", "Wiek", "StatusZwierzecia", "OpiekunNazwa", "NadzorcaNazwa", "IDZwierze"]
    
    event = st.dataframe(
        df[cols_to_show],
        column_config=column_cfg,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # --- 7. KLIKNIĘCIE W WIERSZ ---
    if event.selection.rows:
        idx = event.selection.rows[0]
        selected_id = df.iloc[idx]['IDZwierze']
        
        st.session_state.active_animal_id = int(selected_id)
        st.session_state.view_mode = "details"
        st.rerun()