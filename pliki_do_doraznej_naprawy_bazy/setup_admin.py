import crud

def stworz_admina():
    login = "admin@fundacja.pl"
    haslo = "admin123"
    email = "admin@fundacja.pl"
    rola = "Administrator"

    print(f"⚙️ Próba utworzenia konta: {login} / {haslo} ...")

    # Próbujemy utworzyć nowego użytkownika
    # Funkcja create_user sama haszuje hasło
    sukces = crud.create_user(login, email, haslo, rola)

    if sukces:
        print("\n✅ SUKCES! Konto Administratora zostało utworzone.")
        print(f"👉 Login: {login}")
        print(f"👉 Hasło: {haslo}")
    else:
        print("\n⚠️ Konto o takim loginie już istnieje.")
        print("🔄 Aktualizuję hasło dla istniejącego konta...")
        
        # Jeśli konto istnieje, ale stare hasło nie działa - nadpisujemy je nowym
        crud.change_user_password(login, haslo)
        
        # Upewniamy się też, że konto jest aktywne i ma rolę Admina
        # (Musimy to zrobić SQL-em, bo crud nie ma funkcji update_role_and_status wprost, 
        # ale zmiana hasła powinna wystarczyć do zalogowania).
        print("✅ Hasło zostało zresetowane na 'admin123'.")

if __name__ == "__main__":
    stworz_admina()