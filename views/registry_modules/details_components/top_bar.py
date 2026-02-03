"""
KOMPONENT KARTY: NAGŁÓWEK
-------------------------
Lewa: Wróć.
Środek: IMIĘ ZWIERZĘCIA.
Prawa: Adoptuj (jeśli dostępny) + Edytuj.
"""
import streamlit as st

def render_top_bar(r, id_zw):
    # Zmieniamy proporcje: [Mała, Duża, Bardzo Duża na przyciski]
    c_back, c_title, c_actions = st.columns([1, 5, 3], vertical_alignment="center")
    
    with c_back:
        # Strzałka powrotu
        if st.button("⬅️", help="Wróć do listy", type="secondary", use_container_width=False):
            st.session_state.view_mode = "list"
            st.rerun()

    with c_title:
        # Imię na środku
        imie = r.get('Imie', 'BEZ IMIENIA').upper()
        st.markdown(f"<div class='animal-title'>{imie}</div>", unsafe_allow_html=True)

    with c_actions:
        # Układ przycisków po prawej stronie (Adoptuj + Edytuj)
        # Tworzymy pod-kolumny, żeby przyciski były obok siebie
        ca1, ca2 = st.columns([1, 1])
        
        status = r.get('StatusZwierzecia')
        
        with ca1:
            # Przycisk ADOPTUJ (Tylko jeśli pies nie jest adoptowany ani nieżyjący)
            if status not in ["Adoptowany", "Za Tęczowym Mostem"]:
                # Zielony przycisk dla adopcji wyróżnia się pozytywnie
                # Używamy triku z help, bo streamlit native nie ma koloru zielonego wprost, 
                # ale 'primary' (błękit) też będzie ok, lub zostawiamy secondary.
                # Zrobimy Secondary z emoji domku.
                if st.button("🏠 Adoptuj", help="Rozpocznij proces adopcji", use_container_width=True):
                    st.session_state.view_mode = "adoption_process"
                    st.rerun()
            else:
                # Jeśli adoptowany, można wyświetlić info lub pustkę
                pass

        with ca2:
            # Przycisk EDYTUJ
            if st.button("✏️ Edytuj", help="Edytuj dane", type="secondary", use_container_width=True):
                 st.session_state.view_mode = "edit"
                 st.rerun()
             
    st.divider()