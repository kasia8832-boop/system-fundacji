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
    role = st.session_state.user_role
    
    if role == "Wolontariusz":
        st.info("ℹ️ Jako Wolontariusz masz tylko podgląd słowników. Edycja jest zablokowana.")
        # Tu możesz wyświetlić listy (read-only)
    else:
        st.write("Tutaj administrator i pracownik mogą edytować słowniki.")