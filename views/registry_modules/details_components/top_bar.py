"""
KOMPONENT KARTY: NAGŁÓWEK
-------------------------
Wyświetla imię zwierzęcia, ID oraz przycisk edycji.
Wersja 2.0: Usunięto przycisk adopcji (ze względu na zmiany w bazie).
Dodano wyświetlanie numeru Chip.
"""
"""
KOMPONENT KARTY: NAGŁÓWEK
-------------------------
"""
import streamlit as st

def render_top_bar(r, id_zw):
    imie = r.get('Imie', 'Bez Imienia')
    st.title(imie)
    
    gatunek = r.get('Gatunek', 'Nieznany')
    chip = r.get('NrChip')
    chip_txt = f"Chip: {chip}" if chip else "Brak Chipa"
        
    st.caption(f"Gatunek: {gatunek} | ID: {id_zw} | {chip_txt}")
    st.divider()

    c_btn1, c_btn2, c_space = st.columns([1, 1, 3])
    
    with c_btn1:
        if st.button("✏️ Edytuj Dane", use_container_width=True): 
            st.session_state.view_mode = "edit"
            st.rerun()

    with c_btn2:
        # LOGIKA PRZYCISKU ADOPCJI
        status = r.get('StatusZwierzecia', '')
        
        # Przycisk pokazujemy, jeśli zwierzę NIE jest adoptowane i NIE jest za Tęczowym Mostem
        if status not in ['Adoptowany', 'Za Tęczowym Mostem']:
            # Ten przycisk uruchamia proces adopcji (adoption.py)
            if st.button("🏠 Przeprowadź Adopcję", type="primary", use_container_width=True):
                st.session_state.view_mode = "adoption_process"
                st.rerun()