"""
KOMPONENT KARTY: ZAKŁADKA 'DANE'
--------------------------------
Wyświetla szczegółowe dane metryczkowe zwierzęcia.
Wersja 3.0: Usunięto nieistniejące pole 'DaneAdoptujacego'.
"""
import streamlit as st
import pandas as pd

def render_tab(r):
    st.subheader("📋 Metryczka")
    
    # Układ w dwóch kolumnach
    c1, c2 = st.columns(2)
    
    with c1:
        # DATA PRZYJĘCIA
        data_przyjecia = r.get('DataPrzyjecia')
        if not data_przyjecia:
            data_przyjecia = "Brak danych"
            
        st.markdown(f"**📅 Data Przyjęcia:** {data_przyjecia}")
        st.markdown(f"**🎂 Data Urodzenia:** {r.get('DataUrodzenia', 'Nieznana')}")
        st.markdown(f"**⏳ Wiek (opis):** {r.get('WiekOpisowy', '-')}")

    with c2:
        st.markdown(f"**🐕 Rasa:** {r.get('Rasa', 'Mieszaniec')}")
        st.markdown(f"**⚧ Płeć:** {r.get('Plec', '-')}")
        
        # Status
        status = r.get('StatusZwierzecia', 'Nieznany')
        if status == "W trakcie leczenia":
            st.warning(f"**Status:** {status}")
        elif status == "Adoptowany":
            st.success(f"**Status:** {status}")
        else:
            st.info(f"**Status:** {status}")

    st.divider()
    
    st.subheader("📝 Opis / Notatki")
    opis = r.get('Opis')
    if opis:
        st.write(opis)
    else:
        st.caption("Brak dodatkowego opisu.")

    st.divider()
    
    # Sekcja Adopcji - uproszczona (bo dane są teraz w tabeli Osoba)
    if r.get('StatusZwierzecia') == 'Adoptowany':
        st.subheader("🏠 Informacje o Adopcji")
        # IDOpiekun to liczba (ID osoby w bazie)
        id_opiekuna = r.get('IDOpiekun')
        if id_opiekuna:
            st.info(f"Zwierzę ma przypisanego opiekuna w systemie (ID Osoby: {id_opiekuna}). Szczegóły kontaktu znajdziesz w Panelu Admina -> Baza Osób.")
        else:
            st.warning("Status to 'Adoptowany', ale nie przypisano ID opiekuna w bazie.")