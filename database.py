# database.py
import sqlite3
import pandas as pd
import streamlit as st

# Nazwa pliku bazy danych
DB_FILE = 'fundacja.db'

@st.cache_resource
def init_connection():
    # check_same_thread=False jest wymagane przez Streamlit przy SQLite
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def run_query(query, params=None):
    conn = init_connection()
    try:
        # SQLite wymaga krotki (tuple) nawet dla jednego parametru
        return pd.read_sql(query, conn, params=params)
    except Exception as e:
        st.error(f"Błąd SQL (Query): {e}\nZapytanie: {query}")
        return pd.DataFrame()

def run_command(command, params=None):
    conn = init_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(command, params)
        else:
            cursor.execute(command)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Błąd SQL (Command): {e}\nKomenda: {command}")
        return False