"""
KOMPONENT KARTY: ZAKŁADKA 'ZDROWIE'
-----------------------------------
Tabela z informacjami medycznymi.
Wersja 2.0: Dodano obsługę ochrony przeciw kleszczom.
"""
import streamlit as st
import pandas as pd
from datetime import date

def render_tab(r):
    # Logika wyświetlania kastracji
    data_kast = r.get('DataKastracji')
    if data_kast:
        status_kast = f"Tak ({data_kast})"
    else:
        status_kast = "Nie / Brak danych"

    # Przygotowanie danych do tabeli
    med_data = {
        "Rodzaj Profilaktyki": [
            "Kastracja / Sterylizacja", 
            "Szczepienie: Wścieklizna", 
            "Szczepienie: Choroby Zakaźne", 
            "Odrobaczenie",
            "🛡️ Ochrona p/kleszczom (Ważna do)"  # <--- NOWE POLE
        ],
        "Ostatnia Data / Status": [
            status_kast,
            str(r.get('SzczepienieWscieklizna') or "Brak"),
            str(r.get('SzczepienieZakazne') or "Brak"),
            str(r.get('Odrobaczenie') or "Brak"),
            str(r.get('OchronaKleszczeDo') or "Brak ochrony") # <--- NOWE POLE
        ]
    }
    
    # Wyświetlenie tabeli
    st.dataframe(
        pd.DataFrame(med_data), 
        hide_index=True, 
        use_container_width=True
    )
    
    st.divider()
    
    # Wyświetlenie uwag (W nowym CRUD pole nazywa się OpisZdrowia)
    uwagi = r.get('OpisZdrowia')
    if uwagi: 
        st.markdown("#### 🩺 Opis Zdrowia / Uwagi Weterynarza")
        st.error(uwagi)
    else:
        st.caption("Brak uwag o stanie zdrowia.")