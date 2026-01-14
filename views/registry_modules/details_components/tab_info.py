"""
KOMPONENT KARTY: ZAKŁADKA 'DANE'
--------------------------------
Wyświetla informacje o lokalizacji zwierzęcia (Schronisko lub dane Domu Tymczasowego).
"""


import streamlit as st
import pandas as pd

def render_tab(r):
    st.subheader("Lokalizacja")
    if pd.notnull(r['DT_Imie']):
        st.info(f"📍 Dom Tymczasowy: **{r['DT_Imie']} {r['DT_Nazwisko']}**\n\n📞 {r['DT_Telefon']} | 📧 {r['DT_Email']}")
    else: 
        st.write("📍 Zwierzę przebywa w schronisku.")