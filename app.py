import streamlit as st
import warnings
import styles
from services import maintenance


# Importujemy nasze nowe widoki
from views import login, home, registry, admin

# --- KONFIGURACJA STARTOWA ---
warnings.filterwarnings('ignore') 
st.set_page_config(page_title="Fundacja - SYSTEM", layout="wide")

# ==========================================
# 🕒 AUTOMATYCZNY BACKUP W TLE (NOWOŚĆ)
# ==========================================
@st.cache_resource
def init_backup_system():
    """Uruchamia wątek backupu tylko raz przy starcie serwera"""
    maintenance.start_background_backup()
    return True

init_backup_system()
# ==========================================

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