# styles.py
import streamlit as st

def apply_custom_css():
    MAIN_COLOR = "#FF4B4B"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; }}
        .stButton button[kind="primary"] {{
            background-color: {MAIN_COLOR}; color: white !important;
            border-radius: 12px; border: none; padding: 10px 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: all 0.3s ease;
        }}
        .stButton button[kind="primary"]:hover {{ transform: translateY(-2px); box-shadow: 0 6px 10px rgba(255, 75, 75, 0.4); }}
        [data-testid="stMetric"] {{
            background-color: #ffffff; padding: 15px; border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; border: 1px solid #ddd;
        }}
        [data-testid="stMetricLabel"] {{ color: #444 !important; font-size: 14px; }}
        [data-testid="stMetricValue"] {{ color: {MAIN_COLOR} !important; font-weight: 600; }}
        </style>
    """, unsafe_allow_html=True)

def render_login_header():
    st.markdown("<div style='text-align: center; padding: 20px;'><h1 style='color: #FF4B4B;'>🔐 System Fundacji</h1></div>", unsafe_allow_html=True)