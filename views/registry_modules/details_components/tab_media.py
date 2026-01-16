"""
KOMPONENT KARTY: ZAKŁADKA 'MEDIA'
---------------------------------
Wersja 2.0: Obsługuje zarządzanie Głównym Zdjęciem Profilowym (BLOB).
Usunięto: YouTube (brak kolumny) oraz Galerię URL (uproszczenie systemu).
"""
import streamlit as st
import crud

def render_tab(r, id_zw):
    st.subheader("📷 Zdjęcie Profilowe")
    st.info("Tutaj możesz zarządzać głównym zdjęciem, które wyświetla się w lewym panelu.")

    # 1. Wyświetlanie aktualnego zdjęcia (z danych binarnych BLOB)
    # W nowym CRUD pole nazywa się 'Zdjecie', a nie 'ZdjecieProfilowe' czy 'ZdjecieURL'
    photo_data = r.get('Zdjecie')

    col_view, col_upload = st.columns([1, 1])

    with col_view:
        if photo_data:
            st.image(photo_data, caption="Aktualne zdjęcie w bazie", width=300)
        else:
            st.warning("Brak zdjęcia profilowego.")

    # 2. Upload nowego zdjęcia
    with col_upload:
        st.write("#### 🔄 Zmień zdjęcie")
        uploaded_file = st.file_uploader("Wybierz plik (JPG, PNG)", type=['png', 'jpg', 'jpeg'])

        if uploaded_file:
            # Podgląd przed zapisem
            st.image(uploaded_file, caption="Podgląd nowego", width=150)

            if st.button("💾 Zapisz zdjęcie w bazie", type="primary"):
                # Konwersja pliku na bajty
                bytes_data = uploaded_file.getvalue()
                
                # Wywołanie nowej funkcji z CRUD
                crud.update_animal_photo(id_zw, bytes_data)
                
                st.success("Zdjęcie zaktualizowane!")
                st.rerun()