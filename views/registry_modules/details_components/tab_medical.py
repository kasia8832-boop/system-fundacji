
"""
KOMPONENT KARTY: ZAKŁADKA 'ZDROWIE'
-----------------------------------
Tabela z informacjami medycznymi: Kastracja, Szczepienia, Odrobaczenie.
Wyświetla również uwagi weterynarza na czerwono/żółto.
"""

import streamlit as st
import pandas as pd

def render_tab(r):
    med_data = {
        "Zabieg/Szczepienie": ["Kastracja", "Wścieklizna", "Zakaźne", "Odrobaczenie"],
        "Status": [
            f"{'Tak' if r['CzyKastrowany'] else 'Nie'} ({r['DataKastracji']})" if r['CzyKastrowany'] else "Nie",
            str(r['SzczepienieWscieklizna'] or "Brak"),
            str(r['SzczepienieZakazne'] or "Brak"),
            str(r['Odrobaczenie'] or "Brak")
        ]
    }
    st.dataframe(pd.DataFrame(med_data), hide_index=True, use_container_width=True)
    
    if r['UwagiMedyczne']: 
        st.error(f"⚠ Uwagi Weterynarza: {r['UwagiMedyczne']}")