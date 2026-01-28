"""
PODMODUŁ ADMINA: KONFIGURACJA ALERTÓW
-------------------------------------
Pozwala administratorowi definiować, po ilu dniach zabiegi stają się przeterminowane.
"""
import streamlit as st
import crud
import pandas as pd

def render_alerts_config():
    # Przycisk powrotu
    if st.button("⬅️ Wróć"):
        st.session_state.admin_mode = "dashboard"
        st.rerun()

    st.subheader("🔔 Konfiguracja Powiadomień")
    st.markdown("Zdefiniuj, po ilu dniach zabiegi stają się przeterminowane.")
    
    st.divider()

    # 1. Pobranie danych (Teraz ta funkcja już jest w crud.py)
    try:
        df_config = crud.pobierz_konfiguracje_alertow()
    except AttributeError:
        st.error("W pliku crud.py nadal brakuje funkcji 'pobierz_konfiguracje_alertow'. Zapisz plik crud.py!")
        return

    if df_config.empty:
        st.warning("Tabela konfiguracji jest pusta. Uruchom skrypt 'setup_alerts.py', aby dodać domyślne reguły.")
        return

    # 2. Edytowalna tabela
    edited_df = st.data_editor(
        df_config,
        column_config={
            "KodPola": st.column_config.TextColumn("Pole systemowe", disabled=True),
            "Etykieta": st.column_config.TextColumn("Nazwa wyświetlana"),
            "DniWaznosci": st.column_config.NumberColumn("Ważność (dni)", min_value=0, max_value=3650),
            "CzyAktywny": st.column_config.CheckboxColumn("Aktywny?")
        },
        hide_index=True,
        use_container_width=True,
        key="alerts_editor_table"
    )

    # 3. Zapis
    if st.button("💾 Zapisz zmiany", type="primary"):
        if crud.zapisz_konfiguracje_alertow(edited_df):
            st.success("Zapisano konfigurację!")
            st.rerun()
        else:
            st.error("Wystąpił błąd zapisu.")