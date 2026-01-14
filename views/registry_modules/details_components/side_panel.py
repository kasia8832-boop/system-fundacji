"""
MODUŁ REJESTRU: PROCES ADOPCJI
------------------------------
Wizard (kreator) finalizacji adopcji.
Pozwala wybrać osobę adoptującą z bazy, ustawić datę i zmienić status zwierzęcia na 'Adoptowany'.
"""
import streamlit as st
# ...

import streamlit as st
import pandas as pd
from datetime import date

def render_side_panel(r):
    # Zdjęcie
    img_src = r['ZdjecieProfilowe'] if r['ZdjecieProfilowe'] else "https://place.dog/400/400"
    st.image(img_src, caption=r['Imie'], use_container_width=True)
    
    # Status (kolorowe komunikaty)
    status = r['StatusZwierzecia']
    if status == 'Adoptowany': st.success(f"🏠 {status}")
    elif status == 'Do adopcji': st.info(f"🟢 {status}")
    else: st.warning(f"⚠ {status}")
    
    # Metryki (Wiek, Płeć)
    wiek = date.today().year - pd.to_datetime(r['DataUrodzenia']).year if r['DataUrodzenia'] else "?"
    m1, m2 = st.columns(2)
    m1.metric("Płeć", "Samiec" if r['Plec'] == 'M' else "Samica")
    m2.metric("Wiek", f"ok. {wiek} lat")
    st.metric("Nr Chip", r['NrChip'] if r['NrChip'] else "Brak")