# views/reports.py
import streamlit as st
import pandas as pd
import crud
from sqlalchemy import text
from datetime import date, timedelta
import plotly.express as px

# --- KONFIGURACJA STYLU (Twój dokładny CSS z domieszką kafelków statystyk) ---
CUSTOM_CSS = """
<style>
    /* 1. UKRYCIE SIDEBARA */
    [data-testid="stSidebar"] { display: none; }
    
    /* 2. TŁO APLIKACJI */
    [data-testid="stAppViewContainer"] {
        background: rgb(0,0,0);
        background: linear-gradient(180deg, rgba(0,0,0,1) 0%, rgba(13,27,62,1) 100%);
        color: #e0e0e0;
    }

    /* 3. PRZYCISKI PRIMARY (Błękit) */
    .stButton > button[kind="primary"] {
        background-color: #3498db !important;
        border-color: #3498db !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2980b9 !important;
        border-color: #2980b9 !important;
    }
    
    /* 4. PRZYCISKI SECONDARY (Ciemne) */
    .stButton > button[kind="secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
    }

    /* 5. KONTENERY (Karty) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-color: #2c3e50 !important;
        background-color: rgba(13, 27, 62, 0.6);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* 6. ZAKŁADKI (TABS) */
    .stTabs [aria-selected="true"] { color: #3498db !important; background-color: transparent !important; }
    [data-baseweb="tab-highlight"] { background-color: #3498db !important; height: 3px !important; }
    .stTabs [data-baseweb="tab"] { color: #bdc3c7 !important; background-color: transparent !important; border: none !important; }
    .stTabs [data-baseweb="tab"]:focus { outline: none !important; box-shadow: none !important; }

    /* 7. STATYSTYKI (DARK MODE) - TEGO BRAKOWAŁO! */
    .stat-card-dark {
        background-color: rgba(0, 0, 0, 0.4);
        border: 1px solid #2c3e50;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border-bottom: 4px solid;
    }
    .stat-val { font-size: 28px; font-weight: bold; color: white; }
    .stat-label { font-size: 13px; color: #bdc3c7; text-transform: uppercase; letter-spacing: 1px;}
    
    .blue-b { border-bottom-color: #3498db; }
    .green-b { border-bottom-color: #2ecc71; }
    .purple-b { border-bottom-color: #9b59b6; }
    .orange-b { border-bottom-color: #e67e22; }
</style>
"""

FUNDACJA_COLORS = ['#3498db', '#2ecc71', '#9b59b6', '#e67e22', '#f1c40f', '#1abc9c']

def apply_dark_transparent_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='#e0e0e0', size=14), 
        margin=dict(t=30, b=20, l=20, r=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=False),
        legend=dict(font=dict(color='#e0e0e0'), bgcolor='rgba(0,0,0,0)')
    )
    return fig


def render_reports():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    st.title("Raporty Analityczne")
    st.markdown("Generowanie zaawansowanych zestawień na podstawie rzeczywistych danych fundacji.")
    
    if st.button("⬅️", type="secondary"):
        st.session_state.current_module = "home"
        st.rerun()
        
    st.divider()

    def wybierz_okres(klucz_prefix):
        typ_okresu = st.radio(
            "Wybór okresu:", 
            ["Cały rok", "Własny zakres dat"], 
            horizontal=True, 
            key=f"{klucz_prefix}_radio"
        )
        
        if typ_okresu == "Cały rok":
            rok = st.selectbox("Wybierz rok:", range(date.today().year, 2019, -1), key=f"{klucz_prefix}_rok")
            start_date = date(rok, 1, 1)
            end_date = date(rok, 12, 31)
        else:
            c_od, c_do = st.columns(2)
            start_date = c_od.date_input("Data od", date.today().replace(month=1, day=1), key=f"{klucz_prefix}_od")
            end_date = c_do.date_input("Data do", date.today(), key=f"{klucz_prefix}_do")
            
        return start_date, end_date

    tab1, tab2, tab3 = st.tabs(["Analiza Przepływu", "Źródła Finansowania", "Zestawienie Medyczne"])
    db = crud.get_db_session()

    # =========================================================
    # RAPORT 1: ANALIZA PRZEPŁYWU
    # =========================================================
    with tab1:
        st.subheader("Analiza Losów Zwierząt")
        st.caption("Pokazuje, co ostatecznie stało się ze zwierzętami przyjętymi w wybranym okresie.")
        
        start_przeplyw, end_przeplyw = wybierz_okres("przeplyw")
        
        gatunek_filter = st.radio(
            "Wybierz gatunek do analizy:", 
            ["Wszystkie", "Pies", "Kot"], 
            horizontal=True
        )

        if start_przeplyw <= end_przeplyw:
            query_przeplyw = text("""
                SELECT Gatunek,
                       COUNT(IDZwierze) as Przyjete,
                       SUM(CASE WHEN StatusZwierzecia = 'Adoptowany' THEN 1 ELSE 0 END) as Adoptowane,
                       SUM(CASE WHEN StatusZwierzecia = 'Dom Tymczasowy' THEN 1 ELSE 0 END) as W_DT,
                       SUM(CASE WHEN StatusZwierzecia = 'Za Tęczowym Mostem' THEN 1 ELSE 0 END) as Zmarle
                FROM ZWIERZE
                WHERE DataPrzyjecia >= :start AND DataPrzyjecia <= :end
                GROUP BY Gatunek
            """)
            df_wynik = pd.read_sql(query_przeplyw, db.bind, params={"start": start_przeplyw, "end": end_przeplyw})

            if not df_wynik.empty:
                if gatunek_filter != "Wszystkie":
                    df_wynik = df_wynik[df_wynik['Gatunek'] == gatunek_filter]
                
                przyjete = int(df_wynik['Przyjete'].sum())
                adoptowane = int(df_wynik['Adoptowane'].sum())
                w_dt = int(df_wynik['W_DT'].sum())
                zmarle = int(df_wynik['Zmarle'].sum())
                w_schronisku = przyjete - (adoptowane + w_dt + zmarle)

                st.markdown(f"<br><b>Podsumowanie dla: {gatunek_filter.upper()} (od {start_przeplyw} do {end_przeplyw})</b>", unsafe_allow_html=True)
                
                # UŻYWAMY TWOICH WŁASNYCH KAFELKÓW W HTML!
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"<div class='stat-card-dark blue-b'><div class='stat-val'>{przyjete}</div><div class='stat-label'>Suma Przyjęć</div></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='stat-card-dark green-b'><div class='stat-val'>{adoptowane}</div><div class='stat-label'>Suma Adopcji</div></div>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"<div class='stat-card-dark purple-b'><div class='stat-val'>{w_dt}</div><div class='stat-label'>Obecnie w DT</div></div>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div class='stat-card-dark orange-b'><div class='stat-val'>{w_schronisku}</div><div class='stat-label'>Pozostało w Fundacji</div></div>", unsafe_allow_html=True)

                st.write("") 

                c_chart, c_table = st.columns([3, 2], vertical_alignment="center")
                
                with c_chart:
                    df_plot = pd.DataFrame({
                        'Status': ['Adoptowane', 'W Domu Tymczasowym', 'Za Tęczowym Mostem', 'W Schronisku'],
                        'Liczba': [adoptowane, w_dt, zmarle, w_schronisku]
                    })
                    df_plot = df_plot[df_plot['Liczba'] > 0]

                    if not df_plot.empty:
                        fig_bar = px.bar(
                            df_plot, x='Status', y='Liczba', text='Liczba', color='Status',
                            title=f"Obecny status przyjętych zwierząt",
                            color_discrete_sequence=FUNDACJA_COLORS
                        )
                        fig_bar = apply_dark_transparent_layout(fig_bar)
                        fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Ilość zwierząt")
                        fig_bar.update_traces(textposition='outside')
                        
                        st.plotly_chart(fig_bar, use_container_width=True, theme=None)
                    else:
                        st.info("Brak danych do narysowania wykresu.")

                with c_table:
                    st.dataframe(df_wynik, use_container_width=True, hide_index=True)
                    csv_przeplyw = df_wynik.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Pobierz dane (.CSV)", data=csv_przeplyw, file_name="raport_przeplyw.csv", mime="text/csv")
            else:
                st.info("Brak przyjętych zwierząt w wybranym okresie.")
        else:
            st.error("Data początkowa nie może być późniejsza niż końcowa.")

    # =========================================================
    # RAPORT 2: ŹRÓDŁA FINANSOWANIA
    # =========================================================
    with tab2:
        st.subheader("Struktura Źródeł Finansowania")
        st.caption("Pokazuje, z jakich źródeł finansowane jest utrzymanie **aktualnych** podopiecznych fundacji.")

        query_finanse = text("""
            SELECT ZrodloFinansowania, COUNT(IDZwierze) as Liczba
            FROM ZWIERZE
            WHERE StatusZwierzecia NOT IN ('Adoptowany', 'Za Tęczowym Mostem')
              AND ZrodloFinansowania IS NOT NULL AND ZrodloFinansowania != ''
            GROUP BY ZrodloFinansowania
        """)
        df_finanse = pd.read_sql(query_finanse, db.bind)

        if not df_finanse.empty:
            c_chart, c_table = st.columns([3, 2], vertical_alignment="center")
            
            with c_chart:
                fig_donut = px.pie(
                    df_finanse, values='Liczba', names='ZrodloFinansowania', 
                    hole=0.45, 
                    color_discrete_sequence=FUNDACJA_COLORS
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut = apply_dark_transparent_layout(fig_donut)
                fig_donut.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
                
                st.plotly_chart(fig_donut, use_container_width=True, theme=None)
                
            with c_table:
                st.dataframe(df_finanse, use_container_width=True, hide_index=True)
                csv_finanse = df_finanse.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Pobierz dane (.CSV)", data=csv_finanse, file_name="zrodla_finansowania.csv", mime="text/csv")
        else:
            st.info("Brak wprowadzonych źródeł finansowania dla obecnych podopiecznych.")

    # =========================================================
    # RAPORT 3: ZESTAWIENIE MEDYCZNE
    # =========================================================
    with tab3:
        st.subheader("Zestawienie Działań Medycznych i Behawioralnych")
        st.caption("Ilość przeprowadzonych interwencji w zależności od wybranej kategorii w Historii.")
        
        start_med, end_med = wybierz_okres("medycyna")

        if start_med <= end_med:
            query_med = text("""
                SELECT Kategoria, COUNT(IDHistoria) as Liczba_Zdarzen
                FROM HISTORIA_ZDARZEN
                WHERE Kategoria IN ('Wizyta Weterynaryjna', 'Szczepienie', 'Zabieg', 'Behawiorysta')
                  AND DataZdarzenia >= :start AND DataZdarzenia <= :end
                GROUP BY Kategoria
                ORDER BY Liczba_Zdarzen DESC
            """)
            df_med = pd.read_sql(query_med, db.bind, params={"start": start_med, "end": end_med})

            if not df_med.empty:
                c1, c2 = st.columns([2, 1])
                with c1:
                    fig_med = px.bar(
                        df_med, x="Kategoria", y="Liczba_Zdarzen", 
                        text="Liczba_Zdarzen", color="Kategoria",
                        color_discrete_sequence=FUNDACJA_COLORS
                    )
                    fig_med = apply_dark_transparent_layout(fig_med)
                    fig_med.update_layout(showlegend=False, xaxis_title="", yaxis_title="Ilość Zdarzeń")
                    fig_med.update_traces(textposition='outside')
                    
                    st.plotly_chart(fig_med, use_container_width=True, theme=None)
                
                with c2:
                    st.dataframe(df_med, use_container_width=True, hide_index=True)
                    csv_med = df_med.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Pobierz zestawienie (.CSV)", 
                        data=csv_med, 
                        file_name=f"medycyna_{start_med}_{end_med}.csv", 
                        mime="text/csv"
                    )
            else:
                st.info("Brak odnotowanych zdarzeń medycznych w wybranym okresie.")

    db.close()