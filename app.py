import streamlit as st
import warnings
import styles

# Importujemy nasze nowe widoki
from views import login, home, registry, admin

# Konfiguracja
warnings.filterwarnings('ignore') 
st.set_page_config(page_title="Fundacja - SYSTEM", layout="wide", initial_sidebar_state="collapsed")
styles.apply_custom_css()

# --- STAN APLIKACJI (Inicjalizacja) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "User"
if 'user_role' not in st.session_state: st.session_state.user_role = "Wolontariusz"
if 'current_module' not in st.session_state: st.session_state.current_module = "home"
if 'login_mode' not in st.session_state: st.session_state.login_mode = "login"
if 'view_mode' not in st.session_state: st.session_state.view_mode = "list"
if 'active_animal_id' not in st.session_state: st.session_state.active_animal_id = None
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = "dashboard"

# --- GŁÓWNY ROUTER (Kierownik Ruchu) ---

def main():
    # 1. Jeśli niezalogowany -> Pokaż Login
    if not st.session_state.logged_in:
        login.render_login()
        return

    # 2. Jeśli zalogowany -> Sprawdź jaki moduł wybrać
    module = st.session_state.current_module
    
    if module == "home":
        home.render_home()
        
    elif module == "registry":
        registry.render_registry()
        
    elif module == "admin":
        admin.render_admin()
        
    else:
        st.error(f"Nieznany moduł: {module}")
        if st.button("Reset"):
            st.session_state.current_module = "home"
            st.rerun()

if __name__ == "__main__":
    main()