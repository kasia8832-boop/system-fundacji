"""
KOMPONENT KARTY: PANEL BOCZNY (SIDE PANEL)
------------------------------------------
Wyświetla główne zdjęcie (BLOB) oraz kluczowe metryki (Wiek, Płeć, Chip).
Wersja 2.0: Obsługa zdjęć binarnych i nowych formatów danych.
"""
import streamlit as st
import pandas as pd
from datetime import date

def render_side_panel(r):
    # 1. ZDJĘCIE (Obsługa pola BLOB 'Zdjecie')
    photo_data = r.get('Zdjecie')
    
    if photo_data:
        # Streamlit potrafi wyświetlić bajty bezpośrednio
        st.image(photo_data, caption=r.get('Imie'), use_container_width=True)
    else:
        # Placeholder, jeśli brak zdjęcia
        st.image("https://place.dog/400/400", caption="Brak zdjęcia", use_container_width=True)
    
    st.divider()

    # 2. STATUS
    status = r.get('StatusZwierzecia', 'Nieznany')
    if status == 'Adoptowany': 
        st.success(f"🏠 {status}")
    elif status == 'Gotowy do adopcji' or status == 'Do adopcji': 
        st.success(f"🟢 {status}")
    elif status == 'W trakcie leczenia':
        st.warning(f"💊 {status}")
    else: 
        st.info(f"ℹ️ {status}")
    
    # 3. METRYKI
    # Obliczanie wieku (zabezpieczone przed brakiem daty)
    data_ur = r.get('DataUrodzenia')
    wiek_str = "?"
    
    if data_ur:
        try:
            # Konwersja na datetime, jeśli to string
            dt_ur = pd.to_datetime(data_ur)
            lata = date.today().year - dt_ur.year
            wiek_str = f"ok. {lata} lat"
        except:
            wiek_str = "?"
            
    # Jeśli obliczenie się nie uda, sprawdźmy pole opisowe
    if wiek_str == "?" and r.get('WiekOpisowy'):
        wiek_str = r['WiekOpisowy']

    # Wyświetlanie kafelków (Metrics)
    m1, m2 = st.columns(2)
    
    # Płeć: W nowej bazie mamy pełne słowa ("Samiec", "Samica"), więc wyświetlamy wprost
    plec = r.get('Plec', 'Nieznana')
    m1.metric("Płeć", plec)
    
    m2.metric("Wiek", wiek_str)
    
    chip = r.get('NrChip')
    st.metric("Nr Chip", chip if chip else "Brak")