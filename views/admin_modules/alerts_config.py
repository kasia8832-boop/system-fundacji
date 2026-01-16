"""
PODMODUŁ ADMINA: KONFIGURACJA ALERTÓW
-------------------------------------
Pozwala administratorowi definiować, po ilu dniach zabiegi stają się przeterminowane.
"""
import streamlit as st
import crud
import pandas as pd

def render_alerts_config():
    st.subheader("🔔 Konfiguracja Powiadomień")
    st.markdown("""
    Zdefiniuj zasady, według których system ma ostrzegać o przeterminowanych zabiegach.
    Możesz zmieniać liczbę dni ważności lub całkowicie wyłączyć powiadomienie dla danego typu.
    """)
    
    st.divider()

    # 1. Pobranie danych
    df_config = crud.pobierz_konfiguracje_alertow()

    if df_config.empty:
        st.error("Błąd: Tabela konfiguracji jest pusta. Uruchom skrypt 'update_alerts_db.py'.")
        return

    # 2. Edytowalna tabela (Data Editor)
    # Konfigurujemy kolumny, żeby wyglądały profesjonalnie (checkboxy, liczby)
    edited_df = st.data_editor(
        df_config,
        column_config={
            "KodPola": st.column_config.TextColumn(
                "Pole techniczne", 
                help="Nazwa kolumny w bazie danych (nieedytowalne)",
                disabled=True
            ),
            "Etykieta": st.column_config.TextColumn(
                "Nazwa wyświetlana",
                help="Jak ten alert ma się nazywać w powiadomieniach?"
            ),
            "DniWaznosci": st.column_config.NumberColumn(
                "Ważność (dni)",
                help="Ile dni od zabiegu jest ważny?",
                min_value=0,
                max_value=3650,
                step=1
            ),
            "CzyAktywny": st.column_config.CheckboxColumn(
                "Aktywny?",
                help="Odznacz, aby wyłączyć ten typ alertu."
            )
        },
        hide_index=True,
        use_container_width=True,
        key="alerts_editor_table"
    )

    # 3. Przycisk zapisu
    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        if st.button("💾 Zapisz zmiany", type="primary"):
            if crud.zapisz_konfiguracje_alertow(edited_df):
                st.success("Zapisano!")
                st.rerun()
            else:
                st.error("Wystąpił błąd podczas zapisu.")