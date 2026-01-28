"""
MODUŁ REJESTRU: PROCES ADOPCJI
------------------------------
Finalizacja adopcji.
Wersja 3.0 (ORM): 
- Wymaga wybrania osoby z bazy (Tabela OSOBA).
- Przypisuje IDOpiekun i zmienia status.
"""
import streamlit as st
from datetime import date
import time
import crud

def render_adoption():
    try:
        id_zw = int(st.session_state.active_animal_id)
        zwierz = crud.pobierz_szczegoly_zwierzecia(id_zw)
        imie = zwierz.Imie
    except:
        st.error("Błąd ID zwierzęcia")
        st.button("Wróć", on_click=lambda: setattr(st.session_state, 'view_mode', 'list'))
        st.stop()

    st.header(f"🏠 Adopcja: {imie}")
    st.info("Wybierz nowego właściciela z bazy osób. Jeśli osoby nie ma na liście, dodaj ją najpierw w Panelu Admina.")

    # 1. Pobieramy listę osób do wyboru
    df_osoby = crud.pobierz_wszystkie_osoby()
    
    if df_osoby.empty:
        st.warning("Baza osób jest pusta! Nie można przeprowadzić adopcji.")
        st.info("💡 Dodaj osobę w: Panel Admina -> Baza Osób")
        if st.button("❌ Anuluj"):
            st.session_state.view_mode = "details"
            st.rerun()
        return

    # Tworzymy słownik do selectboxa: { "Jan Kowalski (Warszawa)": ID_Osoba }
    # df_osoby ma kolumny: IDOsoba, Display
    opcje_osoby = dict(zip(df_osoby['Display'], df_osoby['IDOsoba']))

    with st.form("adoption_form"):
        wybrana_osoba_label = st.selectbox("Wybierz Adoptującego", options=opcje_osoby.keys())
        
        # Checkbox umowy
        chk = st.checkbox("✅ Potwierdzam, że umowa adopcyjna została podpisana.")
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.form_submit_button("Anuluj"):
                st.session_state.view_mode = "details"
                st.rerun()
        with col_btn2:
            submitted = st.form_submit_button("🎉 Finalizuj Adopcję", type="primary")
            
        if submitted:
            if not chk:
                st.error("Musisz potwierdzić podpisanie umowy!")
            else:
                # Pobieramy ID wybranej osoby
                id_nowy_wlasciciel = int(opcje_osoby[wybrana_osoba_label])
                
                # Wykonanie adopcji w bazie
                # Funkcja crud.adoptuj_zwierze(id_zwierze, id_nowy_wlasciciel)
                if crud.adoptuj_zwierze(id_zw, id_nowy_wlasciciel):
                    
                    # Opcjonalnie: Dodajemy wpis do historii
                    user_id = st.session_state.get('user_id_osoba') # Jeśli user jest w tabeli Osoba
                    # Tutaj mały hack - potrzebujemy ID_User do historii, a mamy ID_Osoba w sesji...
                    # Ale crud.adoptuj_zwierze zmienia status.
                    # Możemy dodać wpis historii osobno, jeśli chcemy być precyzyjni.
                    
                    st.balloons()
                    st.success(f"Gratulacje! {imie} ma nowego opiekuna: {wybrana_osoba_label}")
                    time.sleep(3)
                    st.session_state.view_mode = "details"
                    st.rerun()
                else:
                    st.error("Wystąpił błąd bazy danych podczas zapisu.")