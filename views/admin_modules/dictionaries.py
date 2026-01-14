"""
MODUŁ ADMINA: SŁOWNIKI SYSTEMOWE
--------------------------------
Pozwala na edycję list rozwijanych używanych w systemie, takich jak:
- Lista Gatunków (Pies, Kot...)
- Lista Statusów (Do adopcji, Leczenie...)
- Źródła pochodzenia
"""
import streamlit as st

def render_dictionaries():
    if st.button("⬅️ Wróć do Pulpitu"): 
        st.session_state.admin_mode = "dashboard"
        st.rerun()
        
    st.header("📚 Słowniki Systemowe")
    st.info("Ta funkcja będzie dostępna w kolejnej wersji systemu.")
    st.write("Tutaj administrator będzie mógł dodawać nowe gatunki zwierząt lub typy zabiegów medycznych.")