"""
KOMPONENT KARTY: ZAKŁADKA 'DANE'
--------------------------------
Wyświetla szczegółowe dane metryczkowe zwierzęcia.
Wersja 2.0: Dostosowana do nowej bazy (DataPrzyjecia, brak danych DT).
"""
import streamlit as st
import pandas as pd

def render_tab(r):
    st.subheader("📋 Metryczka")
    
    # Układ w dwóch kolumnach dla lepszej czytelności
    c1, c2 = st.columns(2)
    
    with c1:
        # DATA PRZYJĘCIA - To jest to nowe pole, o które prosiłeś
        data_przyjecia = r.get('DataPrzyjecia')
        if not data_przyjecia:
            data_przyjecia = "Brak danych"
            
        st.markdown(f"**📅 Data Przyjęcia:** {data_przyjecia}")
        st.markdown(f"**🎂 Data Urodzenia:** {r.get('DataUrodzenia', 'Nieznana')}")
        st.markdown(f"**⏳ Wiek (opis):** {r.get('WiekOpisowy', '-')}")

    with c2:
        st.markdown(f"**🐕 Rasa:** {r.get('Rasa', 'Mieszaniec')}")
        st.markdown(f"**⚧ Płeć:** {r.get('Plec', '-')}")
        
        # Wyświetlamy status w ładnym kolorze
        status = r.get('StatusZwierzecia', 'Nieznany')
        if status == "W trakcie leczenia":
            st.warning(f"**Status:** {status}")
        elif status == "Gotowy do adopcji":
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

    # Informacja o lokalizacji (DT) została usunięta, 
    # ponieważ w nowym modelu bazy nie ma bezpośredniego powiązania w tabeli ZWIERZE.
    st.divider()
    
    # Wyświetlamy dane adopcyjne tylko jeśli są dostępne
    if r.get('StatusZwierzecia') == 'Adoptowany':
        st.subheader("🏠 Informacje o Adopcji")
        st.markdown(f"**Data Adopcji:** {r.get('DataAdopcji', 'Brak daty')}")
        st.markdown("**Dane Adoptującego:**")
        st.info(r.get('DaneAdoptujacego', 'Brak danych'))