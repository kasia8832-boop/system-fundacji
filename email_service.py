# email_service.py
import smtplib
from email.mime.text import MIMEText
import streamlit as st

# === KONFIGURACJA ===
SIMULATION_MODE = False  # <--- TERAZ IDZIEMY NA ŻYWO!

# Dane do Gmaila
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ======================================================
# 🛑 TU WPISZ SWOJE DANE (NIE POKAZUJ TEGO NA PROJEKTORZE!)
# ======================================================
SENDER_EMAIL = "testowafundacja@gmail.com"  # <--- Podaj swój adres Gmail
SENDER_PASSWORD = "eulv lsly wchb ctyx" # <--- Podaj 16-znakowe hasło aplikacji (może być ze spacjami lub bez)

def wyslij_email_resetu(odbiorca, kod_resetu):
    """
    Wysyła kod resetujący. 
    """
    temat = "Fundacja - Reset Hasła"
    tresc = f"""
    Witaj!
    
    Otrzymaliśmy prośbę o reset hasła w Systemie Fundacji.
    Twój kod weryfikacyjny to:
    
    {kod_resetu}
    
    Wpisz ten kod w aplikacji, aby ustawić nowe hasło.
    Jeśli to nie Ty, zignoruj tę wiadomość.
    """

    if SIMULATION_MODE:
        st.toast(f"📧 [SYMULACJA] Kod: {kod_resetu}", icon="📩")
        print(f"📧 [SYMULACJA] Do: {odbiorca} | Kod: {kod_resetu}")
        return True, "Kod wysłany (Symulacja)"
    else:
        # --- WERSJA PRAWDZIWA (SMTP) ---
        try:
            # Tworzenie wiadomości
            msg = MIMEText(tresc, 'plain', 'utf-8') # utf-8 dla polskich znaków
            msg['Subject'] = temat
            msg['From'] = SENDER_EMAIL
            msg['To'] = odbiorca

            # Łączenie z serwerem
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls() # Szyfrowanie połączenia
            
            # Logowanie (usuwamy spacje z hasła dla pewności)
            clean_password = SENDER_PASSWORD.replace(" ", "")
            server.login(SENDER_EMAIL, clean_password)
            
            # Wysyłka
            server.sendmail(SENDER_EMAIL, odbiorca, msg.as_string())
            server.quit()
            
            print(f"✅ Wysłano maila do: {odbiorca}")
            return True, "Email z kodem został wysłany!"
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Błąd logowania! Sprawdź email i Hasło Aplikacji.")
            return False, "Błąd autoryzacji Gmail (złe hasło aplikacji?)"
            
        except Exception as e:
            print(f"❌ Błąd wysyłania: {e}")
            return False, "Błąd połączenia z serwerem pocztowym."