"""
MODUŁ REJESTRU: PROCES ADOPCJI
------------------------------
Wizard (kreator) finalizacji adopcji.
Pozwala wybrać osobę adoptującą z bazy, ustawić datę i zmienić status zwierzęcia na 'Adoptowany'.
"""
import streamlit as st
from datetime import date
import time
import crud

def render_adoption():
    # Przycisk Anuluj
    if st.button("❌ Anuluj"): 
        st.session_state.view_mode = "details"
        st.rerun()
        
    st.header("📝 Adopcja")
    
    # Pobieramy ID zwierzęcia
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Błąd ID zwierzęcia")
        st.stop()

    # Pobieramy listę osób do wyboru
    df_l = crud.pobierz_wszystkie_osoby()
    
    if df_l.empty:
        st.warning("Baza osób jest pusta. Najpierw dodaj osobę w Panelu Admina.")
        return

    # Mapa: "Jan Kowalski" -> ID
    op_l = {f"{r['Imie']} {r['Nazwisko']} (ID: {r['ID_Osoba']})": r['ID_Osoba'] for i,r in df_l.iterrows()}
    
    with st.form("adpt"):
        st.info("Wybierz osobę, która adoptuje zwierzę.")
        per = st.selectbox("Osoba Adoptująca", list(op_l.keys()))
        dat = st.date_input("Data Adopcji", date.today())
        
        st.divider()
        chk = st.checkbox("✅ Potwierdzam, że umowa adopcyjna została podpisana.")
        
        if st.form_submit_button("Zatwierdź Adopcję", type="primary"):
            if chk:
                # Wykonanie adopcji w bazie
                crud.adoptuj_zwierze(id_zw, op_l[per], dat)
                
                st.balloons()
                st.success("Gratulacje! Zwierzę zostało adoptowane.")
                time.sleep(2)
                
                # Powrót do szczegółów
                st.session_state.view_mode = "details"
                st.rerun()
            else: 
                st.error("Musisz potwierdzić podpisanie umowy.")