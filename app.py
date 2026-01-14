import streamlit as st
import pandas as pd
import time
import crud
import styles

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Fundacja - System", page_icon="🐾", layout="wide")

# Ładowanie stylów CSS
styles.apply_custom_css()

# --- STAN APLIKACJI (SESSION STATE) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""
if 'active_page' not in st.session_state:
    st.session_state.active_page = "dashboard"
if 'active_animal_id' not in st.session_state:
    st.session_state.active_animal_id = None
if 'login_mode' not in st.session_state:
    st.session_state.login_mode = "login"

# --- LOGOWANIE (POPRAWIONE: ZAPAMIĘTYWANIE HASŁA) ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>🔐 System Fundacji</h1>", unsafe_allow_html=True)
        st.container(border=True)
        
        if st.session_state.login_mode == "login":
            st.subheader("Zaloguj się")
            
            # --- POPRAWKA: Używamy formularza, żeby przeglądarka pamiętała hasło ---
            with st.form("login_form"):
                email = st.text_input("Login (Email)", autocomplete="username")
                passwd = st.text_input("Hasło", type="password", autocomplete="current-password")
                
                # Przycisk musi być wewnątrz formularza
                submitted = st.form_submit_button("Wejdź", type="primary", use_container_width=True)
                
                if submitted:
                    ok, name, role = crud.weryfikuj_logowanie(email, passwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_name = name
                        st.session_state.user_role = role
                        st.success(f"Witaj {name}!")
                        time.sleep(0.5)
                        st.rerun()
                    else: 
                        st.error("Błąd logowania. Sprawdź dane.")

            if st.button("Zapomniałem hasła", use_container_width=True):
                st.session_state.login_mode = "forgot"
                st.rerun()
        
        else:
            st.subheader("Reset hasła")
            st.info("Skontaktuj się z administratorem, aby zresetować hasło.")
            if st.button("Wróć do logowania"):
                st.session_state.login_mode = "login"
                st.rerun()
    st.stop()

# --- SIDEBAR (MENU) ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    st.caption(f"Rola: {st.session_state.user_role}")
    st.divider()
    
    if st.button("📊 Panel Główny", use_container_width=True):
        st.session_state.active_page = "dashboard"
        st.session_state.active_animal_id = None
        st.rerun()
        
    if st.button("🐶 Rejestr Podopiecznych", use_container_width=True):
        st.session_state.active_page = "rejestr"
        st.session_state.active_animal_id = None
        st.rerun()
        
    if st.session_state.user_role == "Admin":
        if st.button("👥 Baza Osób (DT/Adopcje)", use_container_width=True):
            st.session_state.active_page = "osoby"
            st.rerun()

    st.divider()
    if st.button("Wyloguj"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.rerun()

# --- STRONA: DASHBOARD ---
if st.session_state.active_page == "dashboard":
    st.title("📊 Statystyki Fundacji")
    
    # Pobieramy świeże dane
    df = crud.run_query("SELECT * FROM ZWIERZE")
    
    if df.empty:
        st.warning("Baza danych jest pusta. Dodaj zwierzęta w rejestrze.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Wszystkie Zwierzęta", len(df))
        m1.metric("Psy", len(df[df['Gatunek'] == 'Pies']))
        m2.metric("Do Adopcji", len(df[df['StatusZwierzecia'] == 'Do adopcji']))
        m2.metric("Koty", len(df[df['Gatunek'] == 'Kot']))
        m3.metric("W Leczeniu", len(df[df['StatusZwierzecia'] == 'Leczenie']))
        m4.metric("Adoptowane", len(df[df['StatusZwierzecia'] == 'Adoptowany']))
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Statusy")
            st.bar_chart(df['StatusZwierzecia'].value_counts())
        with c2:
            st.subheader("Gatunki")
            st.bar_chart(df['Gatunek'].value_counts())

# --- STRONA: BAZA OSÓB (TYLKO ADMIN) ---
elif st.session_state.active_page == "osoby":
    st.title("👥 Baza Osób (DT i Adoptujący)")
    
    tab1, tab2 = st.tabs(["Lista Osób", "Dodaj Osobę"])
    
    with tab1:
        df_osoby = crud.pobierz_wszystkie_osoby()
        st.dataframe(df_osoby, use_container_width=True)
    
    with tab2:
        with st.form("dodaj_osobe"):
            c1, c2 = st.columns(2)
            imie = c1.text_input("Imię")
            nazwisko = c2.text_input("Nazwisko")
            tel = c1.text_input("Telefon")
            email = c2.text_input("Email")
            miasto = c1.text_input("Miasto")
            ulica = c2.text_input("Ulica/Nr")
            czy_dt = st.checkbox("Czy to Dom Tymczasowy (DT)?")
            
            if st.form_submit_button("Zapisz Osobę"):
                crud.dodaj_osobe(imie, nazwisko, tel, email, miasto, ulica, czy_dt)
                st.success("Dodano osobę!")
                time.sleep(1)
                st.rerun()

# --- STRONA: REJESTR PODOPIECZNYCH ---
elif st.session_state.active_page == "rejestr":
    
    # WIDOK 1: LISTA (GRID)
    if st.session_state.active_animal_id is None:
        st.title("🐶 Rejestr Podopiecznych")
        
        # Filtry
        with st.expander("🔍 Filtrowanie i Szukanie", expanded=True):
            c1, c2, c3 = st.columns([1,1,2])
            f_gatunek = c1.multiselect("Gatunek", crud.pobierz_liste_slownika("SLOWNIK_GATUNEK"))
            f_status = c2.multiselect("Status", crud.pobierz_liste_slownika("SLOWNIK_STATUS"))
            f_szukaj = c3.text_input("Szukaj (Imię lub Chip)")
        
        # Pobieranie danych
        df = crud.pobierz_zwierzeta_filtrowane(f_gatunek, f_status, f_szukaj)
        
        # Przycisk dodawania
        if st.button("➕ Przyjmij nowe zwierzę"):
            st.session_state.active_animal_id = "NEW"
            st.rerun()
            
        st.divider()
        
        # Wyświetlanie kafelków (Grid)
        if df.empty:
            st.info("Brak wyników.")
        else:
            cols = st.columns(3)
            for index, row in df.iterrows():
                with cols[index % 3]:
                    st.container(border=True)
                    # Zdjęcie (jeśli brak, dajemy placeholder)
                    img = row['ZdjecieProfilowe'] if row['ZdjecieProfilowe'] else "https://via.placeholder.com/300?text=Brak+Zdjecia"
                    st.image(img, use_container_width=True)
                    
                    st.subheader(f"{row['Imie']}")
                    st.caption(f"ID: {row['ID_Zwierze']} | {row['Gatunek']}")
                    st.write(f"**Status:** {row['StatusZwierzecia']}")
                    
                    if st.button(f"KARTA: {row['Imie']}", key=f"btn_{row['ID_Zwierze']}"):
                        st.session_state.active_animal_id = row['ID_Zwierze']
                        st.rerun()

    # WIDOK 2: FORMULARZ DODAWANIA NOWEGO
    elif st.session_state.active_animal_id == "NEW":
        st.button("⬅️ Wróć do listy", on_click=lambda: st.session_state.update(active_animal_id=None))
        st.header("Przyjęcie nowego zwierzęcia")
        
        with st.form("nowe_zwierze"):
            c1, c2 = st.columns(2)
            imie = c1.text_input("Imię *")
            gatunek = c2.selectbox("Gatunek", crud.pobierz_liste_slownika("SLOWNIK_GATUNEK"))
            plec = c1.radio("Płeć", ["Samiec", "Samica"], horizontal=True)
            chip = c2.text_input("Nr Chip")
            data_ur = c1.date_input("Data Urodzenia (przybliżona)")
            status = c2.selectbox("Status", crud.pobierz_liste_slownika("SLOWNIK_STATUS"))
            zrodlo = c1.selectbox("Źródło", crud.pobierz_liste_slownika("SLOWNIK_ZRODLO"))
            
            # Pobieramy listę DT do wyboru
            lista_dt = crud.pobierz_liste_dt()
            opcje_dt = {row['ID_Osoba']: f"{row['Imie']} {row['Nazwisko']}" for i, row in lista_dt.iterrows()}
            wybor_dt = c2.selectbox("Opiekun Tymczasowy", options=[None] + list(opcje_dt.keys()), format_func=lambda x: opcje_dt[x] if x else "Brak")
            
            if st.form_submit_button("Zapisz w bazie"):
                if imie:
                    crud.dodaj_zwierze(imie, gatunek, plec, chip, data_ur, status, zrodlo, 0, 0, wybor_dt)
                    st.success("Dodano!")
                    st.session_state.active_animal_id = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Imię jest wymagane!")

    # WIDOK 3: KARTA SZCZEGÓŁOWA (EDYCJA)
    else:
        # --- POPRAWKA: BEZPIECZNE POBIERANIE DANYCH ---
        id_zw = st.session_state.active_animal_id
        
        if st.button("⬅️ Wróć do listy"):
            st.session_state.active_animal_id = None
            st.rerun()

        # Pobieramy dane karty
        details = crud.pobierz_pelna_karte(id_zw)

        # SPRAWDZAMY CZY ZWIERZĘ ISTNIEJE
        if details.empty:
            st.error(f"❌ Nie znaleziono zwierzęcia o ID {id_zw}. Prawdopodobnie baza została zaktualizowana, a Twoja przeglądarka pamięta stare dane.")
            st.info("Kliknij 'Wróć do listy' i odśwież stronę (Ctrl+R), aby załadować nową listę.")
            st.stop() # Zatrzymujemy działanie, żeby nie było błędu index out of bounds

        # Jeśli istnieje, przypisujemy dane
        r = details.iloc[0]

        st.divider()
        col1, col2 = st.columns([1, 2])
        
        # LEWA KOLUMNA: ZDJĘCIE I INFO
        with col1:
            img = r['ZdjecieProfilowe'] if r['ZdjecieProfilowe'] else "https://via.placeholder.com/300"
            st.image(img, use_container_width=True)
            st.info(f"Status: {r['StatusZwierzecia']}")
            if r['NrChip']: st.caption(f"Chip: {r['NrChip']}")
            
            # Szybka akcja: ADOPCJA
            if r['StatusZwierzecia'] != 'Adoptowany':
                with st.expander("🏠 Finalizacja Adopcji"):
                    with st.form("adopcja_form"):
                        df_osoby = crud.pobierz_wszystkie_osoby()
                        opcje_osob = {row['ID_Osoba']: f"{row['Imie']} {row['Nazwisko']} ({row['Miasto']})" for i, row in df_osoby.iterrows()}
                        adoptujacy = st.selectbox("Wybierz Adoptującego", options=list(opcje_osob.keys()), format_func=lambda x: opcje_osob[x])
                        data_adopcji = st.date_input("Data Adopcji")
                        
                        if st.form_submit_button("Zatwierdź Adopcję"):
                            crud.adoptuj_zwierze(id_zw, adoptujacy, data_adopcji)
                            st.balloons()
                            st.success("Gratulacje! Adopcja zapisana.")
                            time.sleep(2)
                            st.rerun()

        # PRAWA KOLUMNA: TABY
        with col2:
            st.title(f"{r['Imie']}")
            t1, t2, t3, t4 = st.tabs(["📋 Dane & Edycja", "💉 Zdrowie", "📜 Historia", "📷 Galeria & Wideo"])
            
            with t1:
                with st.form("edycja_danych"):
                    n_imie = st.text_input("Imię", value=r['Imie'])
                    n_chip = st.text_input("Chip", value=r['NrChip'] if r['NrChip'] else "")
                    n_status = st.selectbox("Status", crud.pobierz_liste_slownika("SLOWNIK_STATUS"), index=crud.pobierz_liste_slownika("SLOWNIK_STATUS").index(r['StatusZwierzecia']) if r['StatusZwierzecia'] in crud.pobierz_liste_slownika("SLOWNIK_STATUS") else 0)
                    n_img = st.text_input("URL Zdjęcia Profilowego", value=r['ZdjecieProfilowe'] if r['ZdjecieProfilowe'] else "")
                    n_yt = st.text_input("Link YouTube", value=r['YouTubeURL'] if r['YouTubeURL'] else "")
                    
                    st.markdown("### Dane Medyczne (Skrót)")
                    c_kast = st.checkbox("Kastracja?", value=bool(r['CzyKastrowany']))
                    d_kast = st.date_input("Data kastracji", value=pd.to_datetime(r['DataKastracji']) if r['DataKastracji'] else None)
                    
                    if st.form_submit_button("Zapisz Zmiany"):
                        # Tutaj wywołujemy funkcję UPDATE z crud.py
                        # Dla uproszczenia w tym pliku zakładam, że crud.zapisz_edycje_i_profil obsługuje te pola
                        # Przekazujemy aktualne wartości z bazy dla pól, których tu nie edytujemy szczegółowo
                        crud.zapisz_edycje_i_profil(id_zw, n_imie, n_chip, n_status, c_kast, d_kast, 
                                                    r['SzczepienieWscieklizna'], r['SzczepienieZakazne'], 
                                                    r['Odrobaczenie'], r['UwagiMedyczne'], n_img, n_yt)
                        st.success("Zapisano!")
                        st.rerun()

            with t2:
                st.write(f"**Szczepienie Wścieklizna:** {r['SzczepienieWscieklizna'] if r['SzczepienieWscieklizna'] else 'Brak'}")
                st.write(f"**Szczepienie Zakaźne:** {r['SzczepienieZakazne'] if r['SzczepienieZakazne'] else 'Brak'}")
                st.info(f"Uwagi weterynarza: {r['UwagiMedyczne']}")

            with t3:
                # Wyświetlanie historii
                historia = crud.pobierz_historie_zdarzen(id_zw)
                if historia.empty:
                    st.write("Brak wpisów w historii.")
                else:
                    for i, h in historia.iterrows():
                        st.text(f"{h['DataZdarzenia']} | {h['Kategoria']} | {h['Autor']}")
                        st.caption(h['Opis'])
                        st.divider()
                
                # Dodawanie wpisu
                with st.expander("Dodaj zdarzenie"):
                    with st.form("nowe_zdarzenie"):
                        zd_data = st.date_input("Data")
                        zd_kat = st.selectbox("Typ", ["Wizyta", "Zabieg", "Inne", "Profilaktyka"])
                        zd_opis = st.text_area("Opis")
                        # Zakładamy, że zalogowany user to autor (dla uproszczenia ID=1 jeśli nie mamy systemu userów w bazie osób)
                        # W pełnej wersji: pobralibyśmy ID zalogowanego usera z tabeli OSOBA
                        if st.form_submit_button("Dodaj wpis"):
                            crud.dodaj_wpis_historii(id_zw, 1, zd_data, zd_kat, zd_opis)
                            st.success("Dodano!")
                            st.rerun()
            
            with t4:
                # Wideo
                if r['YouTubeURL']:
                    st.video(r['YouTubeURL'])
                
                # Galeria
                galeria = crud.pobierz_galerie(id_zw)
                if not galeria.empty:
                    g_cols = st.columns(3)
                    for i, g in galeria.iterrows():
                        with g_cols[i % 3]:
                            st.image(g['ZdjecieURL'], caption=g['Opis'])
                
                # Dodawanie zdjęcia
                with st.expander("Dodaj zdjęcie do galerii"):
                    with st.form("nowe_foto"):
                        url_f = st.text_input("URL zdjęcia")
                        opis_f = st.text_input("Opis")
                        if st.form_submit_button("Dodaj"):
                            crud.dodaj_zdjecie_galerii(id_zw, url_f, opis_f)
                            st.rerun()