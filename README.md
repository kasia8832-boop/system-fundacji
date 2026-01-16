# 🐾 System Zarządzania Fundacją dla Zwierząt

Kompleksowa aplikacja webowa typu CRM (Customer Relationship Management) stworzona do obsługi procesów adopcyjnych, medycznych i administracyjnych w fundacji pro-zwierzęcej.

---

## 🚀 Kluczowe Funkcjonalności

### 1. Rejestr Podopiecznych
* **Karta Zwierzęcia:** Pełna dokumentacja (dane, chip, zdjęcia, status).
* **Historia Medyczna:** Oś czasu zdarzeń (wizyty, zabiegi) z możliwością dodawania załączników (PDF, wyniki badań).
* **Multimedia:** Galeria zdjęć oraz integracja z YouTube (filmy promocyjne).

### 2. Moduł Administracyjny
* **Role i Uprawnienia (RBAC):**
    * `Administrator`: Pełny dostęp, zarządzanie użytkownikami i słownikami.
    * `Pracownik`: Edycja bazy danych, brak dostępu do konfiguracji kont.
    * `Wolontariusz`: Dostęp do rejestru, brak uprawnień do usuwania danych krytycznych.
    * `Dom Tymczasowy`: Dostęp tylko do podglądu przypisanych zwierząt.
* **Zarządzanie Słownikami:** Dynamiczna edycja gatunków, statusów i źródeł finansowania.

### 3. Bezpieczeństwo i Utrzymanie (DevOps)
* **Automatyczne Backupy:** System wykonuje "Hot Backup" bazy danych (SQLite) codziennie o 08:00 rano, działając w tle (Daemon Thread).
* **Off-site Storage:** Kopie bezpieczeństwa są automatycznie szyfrowane i wysyłane na zewnętrzny serwer e-mail.
* **Odzyskiwanie Dostępu:** Dwuetapowy reset hasła (kod weryfikacyjny wysyłany przez SMTP).

---

## 🛠️ Stack Technologiczny

* **Backend/Frontend:** Python 3.11 + Streamlit
* **Baza Danych:** SQLite3 (z obsługą BLOB dla plików)
* **Bezpieczeństwo:** Werkzeug (haszowanie haseł pbkdf2:sha256)
* **Usługi Tła:** Threading (asynchroniczne zadania), Smtplib (obsługa poczty)

---

## ⚙️ Instalacja i Uruchomienie

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/twoje-repo/system-fundacji.git](https://github.com/twoje-repo/system-fundacji.git)
    cd system-fundacji
    ```

2.  **Zainstaluj zależności:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Skonfiguruj środowisko:**
    Edytuj plik `services/config.py` i uzupełnij dane SMTP (Gmail App Password).

4.  **Zainicjalizuj bazę danych:**
    ```bash
    python init_db.py
    ```

5.  **Uruchom aplikację:**
    ```bash
    streamlit run app.py
    ```

---

## 🔐 Domyślne Dane Logowania

* **Administrator:** `admin@fundacja.pl`
* **Hasło:** `admin123`

---

## 📂 Struktura Projektu

* `/services` - Logika biznesowa, konfiguracja, obsługa maili i backupów.
* `/views` - Warstwa prezentacji (Frontend) podzielona na moduły.
* `/crud.py` - Warstwa dostępu do danych (Data Access Layer).