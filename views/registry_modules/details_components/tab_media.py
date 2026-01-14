"""
KOMPONENT KARTY: ZAKŁADKA 'MEDIA'
---------------------------------
Obsługuje galerię zdjęć oraz odtwarzacz wideo YouTube.
Zawiera formularz do dodawania nowych zdjęć (linków URL) do galerii.
"""
import streamlit as st
# ...

import streamlit as st
import crud

def render_tab(r, id_zw):
    # Sekcja Wideo
    st.subheader("🎬 Wideo")
    if r['YouTubeURL']: 
        st.video(r['YouTubeURL'])
    else: 
        st.info("Brak filmu.")
    
    st.divider()
    
    # Sekcja Galerii
    st.subheader("📷 Galeria")
    df_pics = crud.pobierz_galerie(id_zw)
    
    if not df_pics.empty:
        cols = st.columns(3)
        for index, row in df_pics.iterrows():
            with cols[index % 3]:
                st.image(row['ZdjecieURL'], use_container_width=True)
                if row['Opis']: st.caption(row['Opis'])
    else: 
        st.write("Brak zdjęć w galerii.")
    
    # Formularz dodawania
    with st.expander("➕ Dodaj zdjęcie"):
        with st.form("add_gallery"):
            c1, c2 = st.columns([3,1])
            with c1: url = st.text_input("URL do zdjęcia")
            with c2: 
                st.write("")
                st.write("")
                sub = st.form_submit_button("Dodaj")
            if sub and url:
                crud.dodaj_zdjecie_galerii(id_zw, url, "")
                st.success("Dodano"); st.rerun()