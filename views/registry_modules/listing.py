"""
MODUŁ REJESTRU: LISTA ZWIERZĄT
------------------------------
Wyświetla tabelę ze wszystkimi zwierzętami.
Zawiera filtry (Gatunek, Status) oraz pasek wyszukiwania.
Pozwala wybrać zwierzę, aby przejść do szczegółów.
"""


import streamlit as st
import crud

def render_list():
    role = st.session_state.user_role
    user_email = st.session_state.get('user_email', '')

    # --- KONFIGURACJA UPRAWNIEŃ DLA LISTY ---
    # Tylko Admin, Pracownik i Wolontariusz widzą przycisk "Przyjmij"
    # Dom Tymczasowy NIE widzi przycisku
    
    sl_gat = crud.pobierz_liste_slownika("SLOWNIK_GATUNEK")
    sl_stat = crud.pobierz_liste_slownika("SLOWNIK_STATUS")
    
    c_filt, c_act = st.columns([4, 1])
    
    with c_act:
        # Blokada przycisku dodawania dla DT
        if role in ["Administrator", "Pracownik", "Wolontariusz"]:
             if st.button("➕ Przyjmij", type="primary", use_container_width=True):
                st.session_state.view_mode = "admission"
                st.rerun()
        else:
             st.write("") # Pusty placeholder dla DT

    with c_filt:
        c1, c2, c3 = st.columns(3)
        with c1: f_gat = st.multiselect("Gatunek", sl_gat, default=sl_gat)
        with c2: f_stat = st.multiselect("Status", sl_stat, default=sl_stat)
        with c3: f_txt = st.text_input("Szukaj")
    
    # --- LOGIKA FILTROWANIA PO ROLI ---
    dt_id_filter = None
    
    if role == "Dom Tymczasowy":
        # Znajdź ID osoby na podstawie maila logowania
        dt_id = crud.pobierz_id_osoby_po_emailu(user_email)
        if dt_id:
            dt_id_filter = dt_id
        else:
            st.error("Błąd konfiguracji konta: Twój email logowania nie pasuje do żadnej osoby w bazie DT.")
            return

    # Przekazujemy parametr dt_id_filter do crud
    df = crud.pobierz_zwierzeta_filtrowane(f_gat, f_stat, f_txt, id_dt_only=dt_id_filter)
    
    if not df.empty:
        event = st.dataframe(df[['Imie', 'Gatunek', 'Plec', 'StatusZwierzecia', 'NrChip']], width=1000, on_select="rerun", selection_mode="single-row", hide_index=True, key="df_reg")
        if len(event.selection.rows) > 0:
            st.session_state.active_animal_id = df.iloc[event.selection.rows[0]]["ID_Zwierze"]
            st.session_state.view_mode = "details"
            st.rerun()
    else: 
        st.info("Brak zwierząt do wyświetlenia. (Jeśli jesteś DT, widzisz tylko przypisane do siebie).")