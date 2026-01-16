"""
PLIK KONFIGURACYJNY (config.py)
-------------------------------
To jest jedyne miejsce w projekcie, gdzie wpisujemy hasła i loginy.
Reszta plików (maintenance.py, email_service.py) będzie pobierać dane stąd.

ZALETY:
1. Bezpieczeństwo: Łatwiej ukryć jeden plik niż szukać haseł w całym kodzie.
2. Wygoda: Gdy zmienisz hasło do Gmaila, aktualizujesz je tylko tutaj.
"""

# === DANE SERWERA POCZTOWEGO (GMAIL) ===
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# === TWOJE DANE LOGOWANIA ===
# Tutaj wpisz swój adres e-mail (nadawcy)
EMAIL_SENDER = "testowafundacja@gmail.com"

# Tutaj wpisz 16-znakowe HASŁO APLIKACJI wygenerowane w Google
# (Nie wpisuj tu swojego zwykłego hasła do logowania!)
EMAIL_PASSWORD = "guhu ivul cmtz kopp"

# === ADRES DOCELOWY DLA BACKUPÓW ===
# Na ten adres będą wysyłane automatyczne kopie bazy danych.
# Może to być ten sam adres co nadawcy.
EMAIL_BACKUP_TARGET = "testowafundacja@gmail.com"

# === INNE USTAWIENIA ===
# Godzina wykonania automatycznego backupu (czas polski)
BACKUP_HOUR = 8