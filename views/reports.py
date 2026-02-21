# views/reports.py
import streamlit as st
import pandas as pd
import crud
from sqlalchemy import text
from datetime import date, timedelta

def show():
    # Sprawdzamy czy to wywołanie z Panelu Głównego
    is_standalone = st.session_state.get('current_module') == 'reports'
    
    if is_standalone:
        st.title("📊 Raporty Analityczne")
        st.markdown("Generowanie zestawień i statystyk fundacji na podstawie rzeczywistych danych.")
        if st.button("⬅️ Wróć do Panelu Głównego", type="secondary"):
            st.session_state.current_module = "home"
            st.rerun()
        st.divider()
    else:
        st.header("📊 Generowanie Raportów")
        st.caption("Eksport danych do CSV i analiza skuteczności.")

    # Trzy zakładki dla różnych typów raportów
    tab1, tab2, tab3 = st.tabs(["🏡 Statystyki Adopcji", "🐾 Status Podopiecznych", "💉 Zdarzenia Medyczne"])

    db = crud.get_db_session()

    # ---------------------------------------------------------
    # RAPORT 1: ADOPCJE
    # ---------------------------------------------------------
    with tab1:
        st.subheader("Skuteczność Adopcji")
        col_od, col_do = st.columns(2)
        start_date = col_od.date_input("Data od (Adopcje)", date.today() - timedelta(days=365))
        end_date = col_do.date_input("Data do (Adopcje)", date.today())

        if start_date > end_date:
            st.error("Data początkowa nie może być późniejsza niż końcowa.")
        else:
            # Zapytanie SQL (Pandas) pobierające tylko adopcje w zadanym czasie
            query = text("""
                SELECT h.DataZdarzenia, z.Imie, z.Rasa, z.NrChip, u.LoginName as Odpowiedzialny
                FROM HISTORIA_ZDARZEN h
                JOIN ZWIERZE z ON h.IDZwierze = z.IDZwierze
                LEFT JOIN UZYTKOWNIK u ON h.IDUser = u.IDUser
                WHERE h.Kategoria = 'Adopcja' 
                  AND h.DataZdarzenia >= :start AND h.DataZdarzenia <= :end
                ORDER BY h.DataZdarzenia DESC
            """)
            df_adopcje = pd.read_sql(query, db.bind, params={"start": start_date, "end": end_date})

            if not df_adopcje.empty:
                st.metric("Liczba sfinalizowanych adopcji w okresie", len(df_adopcje))
                
                # Przygotowanie danych do wykresu słupkowego
                df_adopcje['Miesiąc'] = pd.to_datetime(df_adopcje['DataZdarzenia']).dt.to_period('M').astype(str)
                adopcje_miesiac = df_adopcje.groupby('Miesiąc').size().reset_index(name='Liczba Adopcji')
                
                st.bar_chart(data=adopcje_miesiac, x='Miesiąc', y='Liczba Adopcji', color="#2ecc71")

                st.markdown("**Dane szczegółowe:**")
                st.dataframe(df_adopcje.drop(columns=['Miesiąc']), use_container_width=True, hide_index=True)
                
                # Generowanie CSV (Bonus do obrony projektu!)
                csv = df_adopcje.drop(columns=['Miesiąc']).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Pobierz raport (.CSV)", 
                    data=csv, 
                    file_name=f"raport_adopcje_{start_date}_{end_date}.csv", 
                    mime="text/csv"
                )
            else:
                st.info("Brak adopcji w wybranym okresie.")

    # ---------------------------------------------------------
    # RAPORT 2: STATUS PODOPIECZNYCH
    # ---------------------------------------------------------
    with tab2:
        st.subheader("Aktualny Struktura Schroniska")
        st.caption("Zestawienie liczby zwierząt według przypisanego statusu (Stan na dziś).")
        
        df_zwierzeta = crud.pobierz_liste_zwierzat()
        if not df_zwierzeta.empty:
            status_counts = df_zwierzeta['StatusZwierzecia'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Liczba']
            
            c_chart, c_data = st.columns([2, 1])
            with c_chart:
                st.bar_chart(data=status_counts, x='Status', y='Liczba', color="#3498db")
            with c_data:
                st.dataframe(status_counts, use_container_width=True, hide_index=True)
                
                csv_status = df_zwierzeta.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Pobierz pełną listę (.CSV)", 
                    data=csv_status, 
                    file_name="lista_zwierzat_fundacji.csv", 
                    mime="text/csv"
                )
        else:
            st.info("Brak aktywnych zwierząt w systemie.")

    # ---------------------------------------------------------
    # RAPORT 3: MEDYCYNA
    # ---------------------------------------------------------
    with tab3:
        st.subheader("Zestawienie Działań Medycznych")
        c1, c2 = st.columns(2)
        start_med = c1.date_input("Data od (Zabiegi)", date.today() - timedelta(days=30))
        end_med = c2.date_input("Data do (Zabiegi)", date.today())

        if start_med <= end_med:
            query_med = text("""
                SELECT h.DataZdarzenia, h.Kategoria, z.Imie as Pacjent, h.Opis
                FROM HISTORIA_ZDARZEN h
                JOIN ZWIERZE z ON h.IDZwierze = z.IDZwierze
                WHERE h.Kategoria IN ('Wizyta Weterynaryjna', 'Szczepienie', 'Zabieg')
                  AND h.DataZdarzenia >= :start AND h.DataZdarzenia <= :end
                ORDER BY h.DataZdarzenia DESC
            """)
            df_med = pd.read_sql(query_med, db.bind, params={"start": start_med, "end": end_med})

            if not df_med.empty:
                kat_counts = df_med['Kategoria'].value_counts().reset_index()
                kat_counts.columns = ['Typ Zabiegu', 'Liczba Zdarzeń']
                
                st.bar_chart(data=kat_counts, x='Typ Zabiegu', y='Liczba Zdarzeń', color="#e74c3c")
                
                st.markdown("**Lista zabiegów:**")
                st.dataframe(df_med, use_container_width=True, hide_index=True)
                
                csv_med = df_med.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Pobierz historię leczenia (.CSV)", 
                    data=csv_med, 
                    file_name="raport_medyczny.csv", 
                    mime="text/csv"
                )
            else:
                st.info("Brak odnotowanych zdarzeń medycznych w wybranym okresie.")

    db.close()