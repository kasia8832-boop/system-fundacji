# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 1. KONFIGURACJA BAZY DANYCH
# Na razie SQLite. Aby przejść na MS SQL, zmienisz tylko ten string (DATABASE_URL).
# Format MS SQL: "mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+17+for+SQL+Server"
DATABASE_URL = "sqlite:///fundacja.db"

# 2. SILNIK (ENGINE)
# connect_args={'check_same_thread': False} jest potrzebne tylko dla SQLite w Streamlit
engine = create_engine(
    DATABASE_URL, 
    connect_args={'check_same_thread': False} if "sqlite" in DATABASE_URL else {}
)

# 3. SESJA
# SessionLocal to "fabryka" sesji. Będziemy jej używać w każdym zapytaniu.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. BAZA MODELI
# Wszystkie nasze tabele (klasy) będą dziedziczyć po tej klasie.
Base = declarative_base()

def get_db():
    """Funkcja pomocnicza do tworzenia i zamykania sesji (Context Manager)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()