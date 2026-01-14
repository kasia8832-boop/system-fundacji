import streamlit as st
import pandas as pd
import requests
import time
from datetime import date
from streamlit_lottie import st_lottie
import warnings
import crud 
import styles 

warnings.filterwarnings('ignore') 
st.set_page_config(page_title="Fundacja - TESTOWE", layout="wide", initial_sidebar_state="collapsed")
styles.apply_custom_css()

# --- UTILS ---
@st.cache_data
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None
    
def send_email_mock(to, subj, body):
    with st.spinner(f"Wysyłanie do {to}..."): time.sleep(1) 
    st.success(f"✅ E-mail został wysłany na adres: {to}")
    st.info(f"📨 **[SYMULACJA SKRZYNKI POCZTOWEJ]**\n\n**Temat:** {subj}\n\n{body}")

# --- STAN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "User"
if 'user_role' not in st.session_state: st.session_state.user_role = "Wolontariusz"
if 'current_module' not in st.session_state: st.session_state.current_module = "home"
if 'login_mode' not in st.session_state: st.session_state.login_mode = "login"

if 'view_mode' not in st.session_state: st.session_state.view_mode = "list"
if 'active_animal_id' not in st.session_state: st.session_state.active_animal_id = None
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = "dashboard"

# --- LOGOWANIE ---
if not st.session_state.logged_in:
    styles.render_login_header()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.container(border=True)
        if st.session_state.login_mode == "login":
            st.subheader("Zaloguj się")
            email = st.text_input("Login (Email)")
            passwd = st.text_input("Hasło", type="password")
            
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("Wejdź", type="primary", use_container_width=True):
                    ok, name, role = crud.weryfikuj_logowanie(email, passwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_name = name
                        st.session_state.user_role = role
                        st.success(f"Witaj {name}!")
                        time.sleep(0.5); st.rerun()
                    else: st.error("Błąd logowania.")
            with cb2:
                if st.button("Reset hasła", use_container_width=True):
                    st.session_state.login_mode = "forgot"; st.rerun()
        
        elif st.session_state.login_mode == "forgot":
            st.subheader("Reset hasła")
            em = st.text_input("Email")
            if st.button("Wyślij nowe hasło", type="primary", use_container_width=True):
                ok, res = crud.resetuj_haslo(em)
                if ok:
                    send_email_mock(em, "Reset hasła", f"Nowe hasło: {res}")
                    st.session_state.login_mode = "login"; st.rerun()
                else: st.error(res)
            if st.button("Wróć"):
                st.session_state.login_mode = "login"; st.rerun()
    st.stop()

def go_home():
    st.session_state.current_module = "home"
    st.session_state.view_mode = "list"
    st.session_state.admin_mode = "dashboard"
    st.rerun()

# --- HOME ---
if st.session_state.current_module == "home":
    st.title("🏠 Panel Główny")
    role_color = "red" if st.session_state.user_role == "Admin" else "green"
    st.markdown(f"Zalogowany jako: **{st.session_state.user_name}** <span style='background-color:{role_color}; color:white; padding: 2px 6px; border-radius: 4px; font-size: 12px;'>{st.session_state.user_role.upper()}</span>", unsafe_allow_html=True)
    st.divider()
    
    if st.session_state.user_role == "Admin":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🐾 Rejestr Podopiecznych")
            if st.button("Otwórz Rejestr ➡️", key="b1", use_container_width=True, type="primary"):
                st.session_state.current_module = "registry"; st.rerun()
        with col2:
            st.subheader("⚙️ Panel Administracyjny")
            if st.button("Otwórz Panel ➡️", key="b2", use_container_width=True):
                st.session_state.current_module = "admin"; st.rerun()
    else:
        c_l, c_c, c_r = st.columns([1, 2, 1])
        with c_c:
            st.subheader("🐾 Rejestr Podopiecznych")
            if st.button("Otwórz Rejestr ➡️", key="b1_vol", use_container_width=True, type="primary"):
                st.session_state.current_module = "registry"; st.rerun()
            st.info("ℹ️ Nie masz uprawnień do Panelu Administracyjnego.")

    st.divider()
    if st.button("Wyloguj"): st.session_state.logged_in = False; st.rerun()

# --- REJESTR ---
elif st.session_state.current_module == "registry":
    col_nav, col_title = st.columns([1, 6])
    with col_nav:
        if st.button("🏠 Menu", use_container_width=True): go_home()
    with col_title: st.subheader("Moduł: Rejestr Zwierząt")

    if st.session_state.view_mode == "list":
        sl_gat = crud.pobierz_liste_slownika("SLOWNIK_GATUNEK")
        sl_stat = crud.pobierz_liste_slownika("SLOWNIK_STATUS")
        c_filt, c_act = st.columns([4, 1])
        with c_act:
             if st.button("➕ Przyjmij", type="primary", use_container_width=True):
                st.session_state.view_mode = "admission"; st.rerun()
        with c_filt:
            c1, c2, c3 = st.columns(3)
            with c1: f_gat = st.multiselect("Gatunek", sl_gat, default=sl_gat)
            with c2: f_stat = st.multiselect("Status", sl_stat, default=sl_stat)
            with c3: f_txt = st.text_input("Szukaj")
        df = crud.pobierz_zwierzeta_filtrowane(f_gat, f_stat, f_txt)
        if not df.empty:
            st.dataframe(df[['Imie', 'Gatunek', 'Plec', 'StatusZwierzecia', 'NrChip']], width="stretch", on_select="rerun", selection_mode="single-row", hide_index=True, key="df_reg")
            if len(st.session_state.df_reg.selection.rows) > 0:
                st.session_state.active_animal_id = df.iloc[st.session_state.df_reg.selection.rows[0]]["ID_Zwierze"]
                st.session_state.view_mode = "details"; st.rerun()
        else: st.warning("Brak wyników.")

    elif st.session_state.view_mode == "details":
        id_zw = st.session_state.active_animal_id
        r = crud.pobierz_pelna_karte(id_zw).iloc[0]
        
        nav_col, action_col = st.columns([1, 4])
        with nav_col:
            if st.button("⬅️ Wróć", use_container_width=True): st.session_state.view_mode = "list"; st.rerun()
        st.divider()

        col_left, col_right = st.columns([1, 2])
        with col_left:
            img_src = r['ZdjecieProfilowe'] if r['ZdjecieProfilowe'] else "https://place.dog/400/400"
            st.image(img_src, caption=r['Imie'], use_container_width=True)
            status = r['StatusZwierzecia']
            if status == 'Adoptowany': st.success(f"🏠 {status}")
            elif status == 'Do adopcji': st.info(f"🟢 {status}")
            else: st.warning(f"⚠ {status}")
            
            wiek = date.today().year - pd.to_datetime(r['DataUrodzenia']).year if r['DataUrodzenia'] else "?"
            m1, m2 = st.columns(2)
            m1.metric("Płeć", "Samiec" if r['Plec'] == 'M' else "Samica")
            m2.metric("Wiek", f"ok. {wiek} lat")
            st.metric("Nr Chip", r['NrChip'] if r['NrChip'] else "Brak")

        with col_right:
            head_c1, head_c2 = st.columns([3, 2])
            with head_c1:
                st.title(r['Imie'])
                st.caption(f"Gatunek: {r['Gatunek']} | ID: {id_zw}")
            with head_c2:
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("✏️ Edytuj", use_container_width=True): st.session_state.view_mode = "edit"; st.rerun()
                with c_btn2:
                    if r['StatusZwierzecia'] == 'Do adopcji':
                        if st.button("🏠 Adoptuj", type="primary", use_container_width=True): st.session_state.view_mode = "adoption_process"; st.rerun()

            t1, t2, t3, t4 = st.tabs(["📄 Dane", "💉 Zdrowie", "📷 Galeria & Wideo", "📜 Historia"])
            with t1:
                st.subheader("Lokalizacja")
                if pd.notnull(r['DT_Imie']):
                    st.info(f"📍 DT: **{r['DT_Imie']} {r['DT_Nazwisko']}**\n\n📞 {r['DT_Telefon']} | 📧 {r['DT_Email']}")
                else: st.write("📍 Zwierzę przebywa w schronisku.")
            with t2:
                med_data = {
                    "Zabieg/Szczepienie": ["Kastracja", "Wścieklizna", "Zakaźne", "Odrobaczenie"],
                    "Status": [
                        f"{'Tak' if r['CzyKastrowany'] else 'Nie'} ({r['DataKastracji']})" if r['CzyKastrowany'] else "Nie",
                        str(r['SzczepienieWscieklizna'] or "Brak"),
                        str(r['SzczepienieZakazne'] or "Brak"),
                        str(r['Odrobaczenie'] or "Brak")
                    ]
                }
                st.dataframe(pd.DataFrame(med_data), hide_index=True, use_container_width=True)
                if r['UwagiMedyczne']: st.error(f"⚠ Uwagi: {r['UwagiMedyczne']}")
            with t3:
                st.subheader("🎬 Wideo")
                if r['YouTubeURL']: st.video(r['YouTubeURL'])
                else: st.info("Brak filmu.")
                st.divider()
                st.subheader("📷 Galeria")
                df_pics = crud.pobierz_galerie(id_zw)
                if not df_pics.empty:
                    cols = st.columns(3)
                    for index, row in df_pics.iterrows():
                        with cols[index % 3]:
                            st.image(row['ZdjecieURL'], use_container_width=True)
                            if row['Opis']: st.caption(row['Opis'])
                else: st.write("Brak zdjęć.")
            with t4:
                c_hist, c_add = st.columns([2, 1])
                with c_hist:
                    df_h = crud.pobierz_historie_zdarzen(id_zw)
                    if not df_h.empty: st.dataframe(df_h[['DataZdarzenia','Kategoria','Opis','Autor']], use_container_width=True, hide_index=True)
                    else: st.caption("Brak wpisów.")
                with c_add:
                    with st.container(border=True):
                        with st.form("new_history_entry"):
                            sl_k = crud.pobierz_liste_slownika("SLOWNIK_KATEGORIA")
                            kt = st.selectbox("Typ", sl_k)
                            dt = st.date_input("Data", date.today())
                            dfa = crud.pobierz_wszystkie_osoby()
                            amp = {f"{x['Imie']} {x['Nazwisko']}": x['ID_Osoba'] for i,x in dfa.iterrows()}
                            current_user = st.session_state.user_name
                            def_idx = list(amp.keys()).index(current_user) if current_user in amp else 0
                            asu = st.selectbox("Autor", list(amp.keys()), index=def_idx)
                            de = st.text_area("Opis")
                            if st.form_submit_button("Dodaj", type="primary"):
                                crud.dodaj_wpis_historii(id_zw, amp[asu], dt, kt, de)
                                st.success("Dodano!"); time.sleep(0.5); st.rerun()

    elif st.session_state.view_mode == "edit":
        if st.button("❌ Anuluj"): st.session_state.view_mode = "details"; st.rerun()
        st.header("✏️ Edycja Profilu")
        id_zw = st.session_state.active_animal_id
        r = crud.pobierz_dane_do_edycji(id_zw).iloc[0]
        
        tab_main, tab_media, tab_med = st.tabs(["Podstawowe", "Multimedia", "Medyczne"])
        with st.form("ed_form"):
            with tab_main:
                c1, c2 = st.columns(2)
                with c1:
                    ni = st.text_input("Imię", r['Imie'])
                    nc = st.text_input("Nr Chip", r['NrChip'] or "")
                with c2:
                    sl_stat = crud.pobierz_liste_slownika("SLOWNIK_STATUS")
                    c_idx = sl_stat.index(r['StatusZwierzecia']) if r['StatusZwierzecia'] in sl_stat else 0
                    ns = st.selectbox("Status", sl_stat, index=c_idx)
            with tab_media:
                n_img = st.text_input("Link do zdjęcia profilowego (URL)", r['ZdjecieProfilowe'] or "")
                n_yt = st.text_input("Link do filmu na YouTube", r['YouTubeURL'] or "")
            with tab_med:
                k = st.checkbox("Kastracja", bool(r['CzyKastrowany']))
                dk = st.date_input("Data Kastracji", pd.to_datetime(r['DataKastracji']) if r['DataKastracji'] else None)
                w = st.date_input("Wścieklizna", pd.to_datetime(r['SzczepienieWscieklizna']) if r['SzczepienieWscieklizna'] else None)
                z = st.date_input("Zakaźne", pd.to_datetime(r['SzczepienieZakazne']) if r['SzczepienieZakazne'] else None)
                o = st.date_input("Odrobaczenie", pd.to_datetime(r['Odrobaczenie']) if r['Odrobaczenie'] else None)
                u = st.text_area("Uwagi Weterynarza", r['UwagiMedyczne'] or "")
            
            if st.form_submit_button("💾 Zapisz", type="primary"):
                crud.zapisz_edycje_i_profil(id_zw, ni, nc, ns, k, dk, w, z, o, u, n_img, n_yt)
                st.success("Zapisano!"); time.sleep(1); st.session_state.view_mode = "details"; st.rerun()
        
        st.divider(); st.subheader("➕ Dodaj do galerii")
        with st.form("add_gallery"):
            c1, c2 = st.columns([3,1])
            with c1: url = st.text_input("URL")
            with c2: 
                st.write("")
                st.write("")
                sub = st.form_submit_button("Dodaj")
            if sub and url:
                crud.dodaj_zdjecie_galerii(id_zw, url, "")
                st.success("Dodano"); st.rerun()

    elif st.session_state.view_mode == "admission":
        if st.button("❌ Anuluj"): st.session_state.view_mode = "list"; st.rerun()
        st.header("📝 Przyjęcie")
        sl_gat = crud.pobierz_liste_slownika("SLOWNIK_GATUNEK")
        sl_stat = crud.pobierz_liste_slownika("SLOWNIK_STATUS")
        sl_zrodlo = crud.pobierz_liste_slownika("SLOWNIK_ZRODLO")
        df_dt = crud.pobierz_liste_dt()
        dt_opts = {"Brak": None}
        for i, r in df_dt.iterrows(): dt_opts[f"{r['Imie']} {r['Nazwisko']}"] = r['ID_Osoba']
        with st.form("adm"):
            c1, c2 = st.columns(2)
            with c1:
                im = st.text_input("Imię")
                gt = st.selectbox("Gatunek", sl_gat)
                pl = st.radio("Płeć", ["Samiec", "Samica"], horizontal=True)
                ch = st.text_input("Chip")
                dt = st.selectbox("DT", list(dt_opts.keys()))
            with c2:
                ur = st.date_input("Urodzenie", date(2020,1,1))
                stt = st.selectbox("Status", sl_stat)
                src = st.selectbox("Źródło", sl_zrodlo)
                olx = st.checkbox("OLX"); www = st.checkbox("WWW")
            if st.form_submit_button("Zapisz", type="primary"):
                if im:
                    crud.dodaj_zwierze(im, gt, pl, ch, ur, stt, src, olx, www, dt_opts[dt])
                    st.success("Dodano!"); time.sleep(1); st.session_state.view_mode = "list"; st.rerun()
                else: st.error("Brak imienia")

    elif st.session_state.view_mode == "adoption_process":
        if st.button("❌ Anuluj"): st.session_state.view_mode = "details"; st.rerun()
        st.header("📝 Adopcja")
        id_zw = st.session_state.active_animal_id
        df_l = crud.pobierz_wszystkie_osoby()
        op_l = {f"{r['Imie']} {r['Nazwisko']}": r['ID_Osoba'] for i,r in df_l.iterrows()}
        with st.form("adpt"):
            per = st.selectbox("Osoba", list(op_l.keys()))
            dat = st.date_input("Data", date.today())
            chk = st.checkbox("Umowa podpisana")
            if st.form_submit_button("Zatwierdź", type="primary"):
                if chk:
                    crud.adoptuj_zwierze(id_zw, op_l[per], dat)
                    st.balloons(); time.sleep(2); st.session_state.view_mode = "details"; st.rerun()
                else: st.error("Potwierdź umowę.")

# --- ADMIN ---
elif st.session_state.current_module == "admin":
    if st.session_state.user_role != "Admin":
        st.error("⛔ BRAK DOSTĘPU"); st.stop()
    c_n, c_t = st.columns([1, 6])
    with c_n: 
        if st.button("🏠 Menu", use_container_width=True): go_home()
    with c_t: st.subheader("Panel Administracyjny")
    
    if st.session_state.admin_mode == "dashboard":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("🔐 Dostęp")
            if st.button("Zarządzaj Dostępem", use_container_width=True): st.session_state.admin_mode = "access"; st.rerun()
        with c2:
            st.subheader("👥 Baza Osób")
            if st.button("Zarządzaj Osobami", use_container_width=True): st.session_state.admin_mode = "users"; st.rerun()
        with c3:
            st.subheader("📚 Słowniki")
            st.info("Opcja dostępna w pełnej wersji.")

    elif st.session_state.admin_mode == "access":
        if st.button("⬅️ Wróć"): st.session_state.admin_mode = "dashboard"; st.rerun()
        st.header("🔐 Dostęp")
        t1, t2 = st.tabs(["Lista", "Dodaj"])
        with t1:
            df_u = crud.pobierz_liste_uzytkownikow()
            if not df_u.empty:
                st.dataframe(df_u, width="stretch", hide_index=True)
                st.divider()
                st.write("Zmiana roli:")
                c_u, c_r, c_b = st.columns([2,1,1])
                with c_u: 
                    u_map = {f"{r['Imie']} {r['Nazwisko']}": r['ID'] for i,r in df_u.iterrows()}
                    s_u = st.selectbox("User", list(u_map.keys()))
                with c_r: s_r = st.selectbox("Rola", ["Wolontariusz", "Admin"])
                with c_b:
                    st.write("")
                    if st.button("Zmień"):
                        crud.zmien_role_uzytkownika(u_map[s_u], s_r)
                        st.success("OK"); time.sleep(0.5); st.rerun()
        with t2:
            with st.form("new_acc"):
                ni = st.text_input("Imię"); nn = st.text_input("Nazwisko"); ne = st.text_input("Email"); nr = st.selectbox("Rola", ["Wolontariusz", "Admin"])
                if st.form_submit_button("Utwórz"):
                    ok, msg = crud.dodaj_uzytkownika_systemu(ni, nn, ne, nr)
                    if ok: st.success(f"Hasło: {msg}"); st.info("Zapisz je!")
                    else: st.error(msg)
    
    elif st.session_state.admin_mode == "users":
        if st.button("⬅️ Wróć"): st.session_state.admin_mode = "dashboard"; st.rerun()
        st.header("👥 Baza Osób (DT / Adoptujący)")
        t1, t2 = st.tabs(["Lista", "Dodaj"])
        with t1:
             df_os = crud.pobierz_wszystkie_osoby()
             st.dataframe(df_os, width="stretch")
        with t2:
             with st.form("add_os"):
                 im = st.text_input("Imię"); nz = st.text_input("Nazwisko"); tel = st.text_input("Telefon"); em = st.text_input("Email")
                 mi = st.text_input("Miasto"); ul = st.text_input("Ulica"); dt = st.checkbox("Jest DT?")
                 if st.form_submit_button("Dodaj"):
                     crud.dodaj_osobe(im, nz, tel, em, mi, ul, dt)
                     st.success("Dodano!"); st.rerun()