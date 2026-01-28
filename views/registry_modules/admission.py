"""
MODUŁ REJESTRU: PRZYJĘCIE (Z OPTYMALIZACJĄ ZDJĘĆ)
-------------------------------------------------
Formularz dodawania nowego podopiecznego.
Wersja 4.0:
- Automatycznie zmniejsza zdjęcia przed zapisem (Max 800px).
- Drastycznie oszczędza miejsce w bazie i przyspiesza aplikację.
"""
import streamlit as st
import time
import io
from PIL import Image # Do obróbki zdjęć
import crud

def compress_image(uploaded_file):
    """
    Funkcja pomocnicza: Zmniejsza zdjęcie do max 800x800 px
    i kompresuje je do formatu JPEG, aby zajmowało mało miejsca.
    """
    if uploaded_file is None:
        return None
    
    try:
        # Otwieramy obraz z bufora
        image = Image.open(uploaded_file)
        
        # Konwertujemy na RGB (na wypadek gdyby to był PNG z przezroczystością)
        if image.mode in ("RGBA", "P"): 
            image = image.convert("RGB")
            
        # Zmieniamy rozmiar (zachowując proporcje)
        image.thumbnail((800, 800)) 
        
        # Zapisujemy do bufora bajtów jako lekki JPEG
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="JPEG", quality=70) # Quality 70 to dobry balans
        
        return output_buffer.getvalue()
    except Exception as e:
        st.error(f"Błąd przetwarzania zdjęcia: {e}")
        return None

def render_admission():
    # Przycisk Anuluj
    if st.button("❌ Anuluj"): 
        st.session_state.view_mode = "list"
        st.rerun()
        
    st.header("📝 Przyjęcie nowego podopiecznego")
    st.info("Zdjęcia są automatycznie zmniejszane, aby baza działała szybko.")

    # 1. Pobieranie słowników
    try:
        gatunki = crud.pobierz_slownik('gatunek')
        statusy = crud.pobierz_slownik('status')
    except Exception:
        gatunki = ["Pies", "Kot", "Inne"]
        statusy = ["Do Adopcji", "Kwarantanna"]
    
    # 2. Formularz
    with st.form("adm_form"):
        c1, c2 = st.columns(2)
        
        with c1:
            imie = st.text_input("Imię *")
            gatunek = st.selectbox("Gatunek", gatunki)
            plec = st.radio("Płeć", ["Samiec", "Samica", "Nieznana"], horizontal=True)
            
            st.markdown("---")
            st.write("Ogłoszenia:")
            olx = st.checkbox("Ogłoszenie OLX")
            www = st.checkbox("Ogłoszenie WWW")
            
        with c2:
            status = st.selectbox("Status", statusy)
            # --- ZDJĘCIE ---
            st.write("Zdjęcie profilowe:")
            uploaded_file = st.file_uploader("Wybierz plik", type=['jpg', 'png', 'jpeg'])

        st.markdown("---")
        submitted = st.form_submit_button("💾 Zapisz i przejdź do karty", type="primary")
        
        if submitted:
            if not imie:
                st.error("Imię jest wymagane!")
            else:
                # KROK 1: Tworzenie rekordu
                id_nadzorcy = st.session_state.get('user_id_osoba')
                new_id = crud.dodaj_nowe_zwierze(imie, gatunek, plec, status, id_nadzorca=id_nadzorcy)
                
                if new_id:
                    # KROK 2: Checkboxy
                    dane_dodatkowe = {}
                    if olx: dane_dodatkowe['CzyOgloszenieOLX'] = True
                    if www: dane_dodatkowe['CzyOgloszenieWWW'] = True
                    
                    if dane_dodatkowe:
                        crud.aktualizuj_dane_podstawowe(new_id, dane_dodatkowe)
                    
                    # KROK 3: ZDJĘCIE Z KOMPRESJĄ
                    if uploaded_file is not None:
                        # Tu dzieje się magia optymalizacji!
                        compressed_data = compress_image(uploaded_file)
                        if compressed_data:
                            crud.aktualizuj_zdjecie(new_id, compressed_data)

                    st.success(f"Dodano zwierzaka: {imie} (ID: {new_id})")
                    time.sleep(1)
                    
                    st.session_state.active_animal_id = new_id
                    st.session_state.view_mode = "details"
                    st.rerun()
                else:
                    st.error("Wystąpił błąd podczas zapisu do bazy.")