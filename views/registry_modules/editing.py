"""
MODUŁ REJESTRU: EDYCJA DANYCH
-----------------------------
Formularz edycji danych zwierzęcia.
Wersja 3.1: Dodano możliwość zmiany ZDJĘCIA PROFILOWEGO (z kompresją).
"""

import streamlit as st
import time
import crud
import io
from datetime import date
from PIL import Image

# Funkcja do kompresji (ta sama co w admission.py)
def compress_image(uploaded_file):
    if uploaded_file is None: return None
    try:
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "P"): image = image.convert("RGB")
        image.thumbnail((800, 800)) 
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="JPEG", quality=70)
        return output_buffer.getvalue()
    except Exception as e:
        st.error(f"Błąd zdjęcia: {e}")
        return None

def render_edit():
    # Przycisk Anuluj
    if st.button("❌ Anuluj"): 
        st.session_state.view_mode = "details"
        st.rerun()
        
    st.header("✏️ Edycja Profilu")
    
    try:
        id_zw = int(st.session_state.active_animal_id)
    except:
        st.error("Brak ID zwierzęcia")
        st.stop()
    
    zwierze = crud.pobierz_szczegoly_zwierzecia(id_zw)
    if zwierze is None:
        st.error("Błąd danych.")
        return

    # Słowniki
    try:
        sl_gat = crud.pobierz_slownik("gatunek")
        sl_stat = crud.pobierz_slownik("status")
    except:
        sl_gat = ["Pies", "Kot"]
        sl_stat = ["Do Adopcji"]

    # Zakładki edycji
    tab_main, tab_med = st.tabs(["📋 Dane Podstawowe", "🏥 Dane Medyczne"])
    
    with st.form("ed_form"):
        # --- ZAKŁADKA 1: PODSTAWOWE ---
        with tab_main:
            c1, c2 = st.columns(2)
            with c1:
                ni = st.text_input("Imię", value=zwierze.Imie or "")
                
                obecny_gat = zwierze.Gatunek or sl_gat[0]
                idx_gat = sl_gat.index(obecny_gat) if obecny_gat in sl_gat else 0
                ng = st.selectbox("Gatunek", sl_gat, index=idx_gat)
                
                nr = st.text_input("Rasa", value=zwierze.Rasa or "")
                dp = st.date_input("Data Przyjęcia", value=zwierze.DataPrzyjecia or date.today())

            with c2:
                opcje_plec = ["Samiec", "Samica", "Nieznana"]
                obecna_plec = zwierze.Plec or "Nieznana"
                idx_plec = opcje_plec.index(obecna_plec) if obecna_plec in opcje_plec else 2
                np_val = st.radio("Płeć", opcje_plec, index=idx_plec, horizontal=True)

                nc = st.text_input("Nr Chip", value=zwierze.NrChip or "")
                du = st.date_input("Data Urodzenia", value=zwierze.DataUrodzenia or None)
                
                obecny_stat = zwierze.StatusZwierzecia or sl_stat[0]
                idx_stat = sl_stat.index(obecny_stat) if obecny_stat in sl_stat else 0
                ns = st.selectbox("Status", sl_stat, index=idx_stat)
                
                st.markdown("---")
                olx = st.checkbox("OLX", value=bool(zwierze.CzyOgloszenieOLX))
                www = st.checkbox("WWW", value=bool(zwierze.CzyOgloszenieWWW))

            no = st.text_area("Opis ogólny", value=zwierze.Opis or "")

            # --- NOWOŚĆ: ZMIANA ZDJĘCIA W EDYCJI ---
            st.markdown("### 📷 Zmień zdjęcie profilowe")
            new_photo = st.file_uploader("Wgraj nowe zdjęcie (zastąpi obecne)", type=['jpg', 'png', 'jpeg'])

        # --- ZAKŁADKA 2: MEDYCZNE ---
        with tab_med:
            st.info("Daty ważności zabiegów")
            cm1, cm2 = st.columns(2)
            with cm1:
                w = st.date_input("Wścieklizna", value=zwierze.SzczepienieWscieklizna or None)
                z = st.date_input("Zakaźne", value=zwierze.SzczepienieZakazne or None)
            with cm2:
                o = st.date_input("Odrobaczenie", value=zwierze.Odrobaczenie or None)
                kl = st.date_input("🛡️ Kleszcze (Ważne do)", value=zwierze.OchronaKleszczeDo or None)

            st.divider()
            dk = st.date_input("Data Kastracji", value=zwierze.DataKastracji or None)
            u = st.text_area("Opis Zdrowia", value=zwierze.OpisZdrowia or "")
        
        # --- ZAPIS ---
        if st.form_submit_button("💾 Zapisz Zmiany", type="primary"):
            dane_do_zapisu = {
                "Imie": ni, "Gatunek": ng, "Rasa": nr, "DataPrzyjecia": dp,
                "Plec": np_val, "NrChip": nc, "DataUrodzenia": du, "StatusZwierzecia": ns,
                "CzyOgloszenieOLX": olx, "CzyOgloszenieWWW": www, "Opis": no,
                "SzczepienieWscieklizna": w, "SzczepienieZakazne": z,
                "Odrobaczenie": o, "OchronaKleszczeDo": kl,
                "DataKastracji": dk, "OpisZdrowia": u
            }

            if crud.aktualizuj_dane_podstawowe(id_zw, dane_do_zapisu):
                # Aktualizacja zdjęcia (jeśli wgrano nowe)
                if new_photo:
                    compressed = compress_image(new_photo)
                    if compressed:
                        crud.aktualizuj_zdjecie(id_zw, compressed)

                st.success("Zapisano!")
                time.sleep(1)
                st.session_state.view_mode = "details"
                st.rerun()
            else:
                st.error("Błąd zapisu.")