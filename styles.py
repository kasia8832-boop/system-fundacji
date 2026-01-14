import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #dee2e6;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

def render_login_header():
    # Prosta funkcja renderująca nagłówek logowania
    st.markdown("<h1 style='text-align: center; color: #4F8BF9;'>🔐 Witaj w Systemie</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Zaloguj się, aby kontynuować pracę.</p>", unsafe_allow_html=True)