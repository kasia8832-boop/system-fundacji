"""
KOMPONENT: SZCZEGÓŁY ZDARZENIA (HISTORIA)
-----------------------------------------
Wyświetla pełne informacje o jednym zdarzeniu z historii.
Pozwala przeglądać, pobierać, dodawać i USUWAĆ załączniki oraz CAŁE ZDARZENIE.
"""
import streamlit as st
import pandas as pd
import time
import crud

# Konfiguracja limitów
MAX_FILE_SIZE_MB = 100
ALLOWED_EXT = ['jpg', 'png', 'xlsx', 'xls', 'doc', 'docx', 'csv', 'pdf', 'txt']

# --- MODAL 1: USUWANIE POJEDYNCZEGO PLIKU ---
@st.dialog("⚠️ Potwierdzenie usunięcia pliku")
def potwierdz_usuniecie_pliku(id_pliku, nazwa_pliku):
    st.write(f"Czy na pewno chcesz usunąć plik: **{nazwa_pliku}**?")
    st.warning("Tej operacji nie można cofnąć.")
    
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Tak, usuń plik", type="primary", use_container_width=True):
            crud.usun_zalacznik(id_pliku)
            st.toast(f"🗑️ Usunięto: {nazwa_pliku}")
            time.sleep(0.5)
            st.rerun()
            
    with col_no:
        if st.button("Anuluj", use_container_width=True):
            st.rerun()

# --- MODAL 2: USUWANIE CAŁEGO ZDARZENIA (NOWOŚĆ) ---
@st.dialog("🚨 Usuwanie zdarzenia")
def potwierdz_usuniecie_calego_zdarzenia(id_historia):
    st.write("Czy na pewno chcesz usunąć **cały wpis historii**?")
    st.error("⚠️ Zostanie usunięty wpis oraz wszystkie dołączone do niego pliki!")
    
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Tak, usuń wszystko", type="primary", use_container_width=True):
            ok, msg = crud.usun_wpis_historii(id_historia)
            if ok:
                st.success("Usunięto zdarzenie.")
                time.sleep(1)
                # Resetujemy ID aktywnego zdarzenia, żeby wrócić do listy
                st.session_state.active_history_event_id = None
                st.rerun()
            else:
                st.error(f"Błąd: {msg}")
            
    with col_no:
        if st.button("Nie usuwaj", use_container_width=True):
            st.rerun()

# --- GŁÓWNA FUNKCJA WIDOKU ---
def render_event_details(event_id):
    # GÓRNY PASEK AKCJI (Wróć + Usuń Wpis)
    c_nav, c_del_main = st.columns([5, 2])
    
    with c_nav:
        if st.button("⬅️ Wróć do listy zdarzeń"):
            st.session_state.active_history_event_id = None
            st.rerun()
            
    with c_del_main:
        # Przycisk usuwania całego zdarzenia
        if st.button("🗑️ Usuń ten wpis", type="primary", use_container_width=True):
            potwierdz_usuniecie_calego_zdarzenia(event_id)
        
    # Pobieranie danych zdarzenia
    conn = crud.create_connection()
    query = f"""
        SELECT h.*, o.Imie || ' ' || o.Nazwisko as Autor
        FROM HISTORIA_ZDARZEN h
        LEFT JOIN OSOBA o ON h.ID_Osoba = o.ID_Osoba
        WHERE h.ID_Historia = {event_id}
    """
    try:
        event_data = pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Błąd SQL: {e}")
        conn.close()
        return
    finally:
        conn.close()
    
    if event_data.empty:
        st.error("Nie znaleziono zdarzenia.")
        return

    evt = event_data.iloc[0]
    
    st.markdown(f"### 📅 {evt['DataZdarzenia']} | {evt['Kategoria']}")
    st.caption(f"Autor wpisu: {evt['Autor']}")
    
    st.info(evt['Opis'])
    
    st.divider()
    
    # --- SEKCJA 1: LISTA ZAŁĄCZNIKÓW ---
    st.subheader("📎 Załączniki")
    files_df = crud.pobierz_zalaczniki(event_id)
    
    if not files_df.empty:
        for index, file in files_df.iterrows():
            col_icon, col_name, col_down, col_del = st.columns([0.5, 4.5, 1.5, 1])
            
            with col_icon: 
                st.write("📄")
            
            with col_name: 
                size_kb = file['RozmiarBajt'] / 1024
                st.write(f"**{file['NazwaPliku']}** ({size_kb:.1f} KB)")
            
            with col_down:
                file_data = crud.pobierz_plik_content(file['ID_Zalacznik'])
                if file_data:
                    st.download_button(
                        label="⬇️ Pobierz",
                        data=file_data[1],
                        file_name=file_data[0],
                        mime=file_data[2],
                        key=f"dl_{file['ID_Zalacznik']}",
                        use_container_width=True
                    )
            
            with col_del:
                if st.button("🗑️", key=f"del_{file['ID_Zalacznik']}", help="Usuń plik"):
                    potwierdz_usuniecie_pliku(file['ID_Zalacznik'], file['NazwaPliku'])

    else:
        st.caption("Brak załączników.")

    st.divider()

    # --- SEKCJA 2: DODAWANIE PLIKÓW ---
    st.subheader("➕ Dodaj pliki")
    
    with st.form("upload_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Wybierz pliki", 
            type=ALLOWED_EXT, 
            accept_multiple_files=True
        )
        
        if st.form_submit_button("Wyślij pliki"):
            if uploaded_files:
                total_size = sum([f.size for f in uploaded_files]) / (1024 * 1024)
                
                if total_size > MAX_FILE_SIZE_MB:
                    st.error(f"Łączny rozmiar plików ({total_size:.2f} MB) przekracza limit {MAX_FILE_SIZE_MB} MB!")
                else:
                    bledy = []
                    for f in uploaded_files:
                        ok, komunikat = crud.dodaj_zalacznik(event_id, f)
                        if not ok:
                            bledy.append(f"{f.name}: {komunikat}")
                    
                    if bledy:
                        st.error("Błędy:")
                        for b in bledy: st.write(f"❌ {b}")
                    else:
                        st.success("Dodano!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("Wybierz pliki.")