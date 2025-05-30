from abc import ABC, abstractmethod
from tkinter import messagebox

import mysql.connector


class Database:
    def __init__(self, host="localhost", user="root", password="dupa", database="sys"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Łączenie z bazą danych"""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset="utf8mb4",
                    collation="utf8mb4_general_ci"
                )
                self.cursor = self.connection.cursor()
                print("Połączenie z bazą danych nawiązane.")
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Nie można połączyć z bazą danych: {e}")

    def close(self):
        """Zamykanie połączenia z bazą danych"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Połączenie z bazą danych zamknięte.")
        self.connection = None
        self.cursor = None

    def execute_query(self, query, params=None):
        """Wykonanie zapytania do bazy danych"""
        if not self.connection or not self.connection.is_connected():
            self.connect()  # Ponowne połączenie, jeśli zostało utracone

        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd zapytania: {e}")
            return None

    def reconnect(self):
        """Ponowne połączenie z bazą danych"""
        self.close()
        self.connect()

    def get_cursor(self):
        """Zwraca aktywny kursor do wykonywania zapytań"""
        if not self.cursor:
            self.connect()  # Otwórz połączenie, jeśli kursor jest nieaktywny
        return self.cursor

    def get_connection(self):
        """Zwraca aktywne połączenie do bazy"""
        if not self.connection or not self.connection.is_connected():
            self.connect()  # Otwórz połączenie, jeśli jest nieaktywne
        return self.connection

# utworzenie klas reprezentujących najważniejsze encje — lekarzy, pacjentów, wizyt i danych logowania
class Pacjent:
    def __init__(self, id, imie, nazwisko, plec, data_urodzenia, email, pesel, waga=0, wzrost=0):
        self.id = id
        self.imie = imie
        self.nazwisko = nazwisko
        self.plec = plec
        self.data_urodzenia = data_urodzenia
        self.email = email
        self.pesel = pesel
        self.waga = waga
        self.wzrost = wzrost



class Lekarz:
    def __init__(self, id, imie, nazwisko,plec,data_urodzenia, specjalnosc=None):  # Dodanie domyślnej wartości dla specjalnosc
        self.id = id
        self.imie = imie
        self.nazwisko = nazwisko
        self.specjalnosc = specjalnosc
        self.plec = plec
        self.data_urodzenia = data_urodzenia



class Wizyta:
    def __init__(self, id_wizyty, id_lekarza, id_pacjenta, id_zabiegu, godz_rozp, godz_zak):
        self.id_wizyty = id_wizyty
        self.id_lekarza = id_lekarza
        self.id_pacjenta = id_pacjenta
        self.id_zabiegu = id_zabiegu
        self.godz_rozp = godz_rozp
        self.godz_zak = godz_zak


class DaneLogowania:
    def __init__(self, id_uzytkownika, login, email, haslo):
        self.id = id_uzytkownika
        self.login = login  # nazwa użytkownika lub PESEL w zależności od użytkownika
        self.email = email
        self.haslo = haslo


# utworzenie obiektów dostępu do danych DAO (Data Access Object)
class PacjentDAO:
    def __init__(self, database):
        self.database = database


    def pobierz_pacjenta(self, id_pacjenta):
        query = "SELECT * FROM PACJENT WHERE id = %s"
        cursor = self.database.execute_query(query, (id_pacjenta,))
        if cursor:
            result = cursor.fetchall()
            if result:
                return Pacjent(*result[0])  # Return the first result if available
        return None

    def dodaj_pacjenta(self, imie, nazwisko, plec, data_urodzenia, waga=None, wzrost=None):
        query = """
            INSERT INTO PACJENT (imie, nazwisko, plec, data_urodzenia, waga, wzrost)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            self.database.execute_query(query, (imie, nazwisko, plec, data_urodzenia, waga, wzrost))
            self.database.get_connection().commit()
            print("Pacjent został dodany.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd dodawania pacjenta: {e}")

    def aktualizuj_pacjenta(self, id_pacjenta, imie=None, nazwisko=None, waga=None, wzrost=None):
        columns = []
        values = []

        if imie is not None:
            columns.append("imie = %s")
            values.append(imie)
        if nazwisko is not None:
            columns.append("nazwisko = %s")
            values.append(nazwisko)
        if waga is not None:
            columns.append("waga = %s")
            values.append(waga)
        if wzrost is not None:
            columns.append("wzrost = %s")
            values.append(wzrost)

        if columns:
            query = f"""
                UPDATE PACJENT
                SET {', '.join(columns)}
                WHERE id = %s
            """
            values.append(id_pacjenta)
            try:
                self.database.execute_query(query, tuple(values))
                self.database.get_connection().commit()
                print(f"Dane pacjenta o ID {id_pacjenta} zostały zaktualizowane.")
            except mysql.connector.Error as e:
                messagebox.showerror("Query Error", f"Błąd aktualizacji pacjenta: {e}")

class LekarzDAO:
    def __init__(self, database):
        self.znajdz_lekarzy = None
        self.database = database

    def pobierz_lekarza(self, id_lekarza):
        """Pobieranie danych lekarza z bazy danych"""
        query = """
            SELECT lekarz.id, lekarz.imie, lekarz.nazwisko, GROUP_CONCAT(specjalnosc.nazwa_specjalnosci SEPARATOR ', ') AS specjalnosci
            FROM lekarz
            LEFT JOIN lekarz_specjalnosc ON lekarz.id = lekarz_specjalnosc.id_lekarza
            LEFT JOIN specjalnosc ON lekarz_specjalnosc.id_specjalnosci = specjalnosc.id
            WHERE lekarz.id = %s
            GROUP BY lekarz.id
        """
        cursor = self.database.execute_query(query, (id_lekarza,))

        if cursor:
            result = cursor.fetchall()
            if result:
                wynik = result[0]
                if len(wynik) == 4:  # Sprawdzamy, czy wszystkie wymagane argumenty są dostępne
                    return Lekarz(*wynik)
                else:
                    raise ValueError(f"Niekompletne dane dla lekarza o id {id_lekarza}: {wynik}")
        return None

    def aktualizuj_lekarza(self, id_lekarza, imie=None, nazwisko=None):
        columns = []
        values = []

        if imie is not None:
            columns.append("imie = %s")
            values.append(imie)
        if nazwisko is not None:
            columns.append("nazwisko = %s")
            values.append(nazwisko)

        if columns:
            query = f"""
                UPDATE LEKARZ
                SET {', '.join(columns)}
                WHERE id_lekarza = %s
            """
            values.append(id_lekarza)
            try:
                self.database.execute_query(query, tuple(values))
                self.database.get_connection().commit()
                print(f"Dane lekarza o ID {id_lekarza} zostały zaktualizowane.")
            except mysql.connector.Error as e:
                messagebox.showerror("Query Error", f"Błąd aktualizacji lekarza: {e}")

class WizytaDAO:
    def __init__(self, database):
        self.database = database

    def pobierz_wizyty_pacjenta(self, id_pacjenta):
        query = "SELECT * FROM WIZYTA WHERE id_pacjenta = %s"
        cursor = self.database.execute_query(query, (id_pacjenta,))
        if cursor:
            return cursor.fetchall()
        return None

    def pobierz_wizyty_lekarza(self, id_lekarza):
        query = "SELECT * FROM WIZYTA WHERE id_lekarza = %s"
        cursor = self.database.execute_query(query, (id_lekarza,))
        if cursor:
            return cursor.fetchall()
        return None

    def dodaj_wizyte(self, id_lekarza, id_pacjenta, id_zabiegu, godz_rozp, godz_zak):
        query = """
            INSERT INTO WIZYTA (id_lekarza, id_pacjenta, id_zabiegu, wizyta.godzina_rozpoczecia, godzina_zakonczenia)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.database.execute_query(query, (id_lekarza, id_pacjenta, id_zabiegu, godz_rozp, godz_zak))
            self.database.get_connection().commit()
            print("Wizyta została dodana.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd dodawania wizyty: {e}")

    def aktualizuj_wizyte(self, id_wizyty, godz_rozp, godz_zak):
        query = """
            UPDATE WIZYTA
            SET godzina_rozpoczecia = %s, godzina_zakonczenia = %s
            WHERE id = %s
        """
        try:
            self.database.execute_query(query, (godz_rozp, godz_zak, id_wizyty))
            self.database.get_connection().commit()
            print("Wizyta została zaktualizowana.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd aktualizacji wizyty: {e}")

    def usun_wizyte(self, id_wizyty):
        query = "DELETE FROM WIZYTA WHERE id = %s"
        try:
            self.database.execute_query(query, (id_wizyty,))
            self.database.get_connection().commit()
            print("Wizyta została usunięta.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd usuwania wizyty: {e}")

class DaneLogowaniaDAO:
    def __init__(self):
        self.database = None

    def pobierz_dane_pacjenta(self, id_pacjenta):
        query = "SELECT numer_PESEL, haslo FROM DANE_LOGOWANIA_PACJENCI WHERE id_pacjenta = %s"
        cursor = self.database.execute_query(query, (id_pacjenta,))
        if cursor:
            result = cursor.fetchall()
            if result:
                return result[0]  # Zwracamy pierwszy wynik, jeśli istnieje
        return None

    def pobierz_dane_lekarza(self, id_lekarza):
        query = "SELECT nazwa_uzytkownika, haslo FROM DANE_LOGOWANIA_LEKARZE WHERE id_lekarza = %s"
        cursor = self.database.execute_query(query, (id_lekarza,))
        if cursor:
            result = cursor.fetchall()
            if result:
                return result[0]  # Zwracamy pierwszy wynik, jeśli istnieje
        return None

    def aktualizuj_haslo_pacjenta(self, id_pacjenta, nowe_haslo):
        query = "UPDATE DANE_LOGOWANIA_PACJENCI SET haslo = %s WHERE id_pacjenta = %s"
        try:
            self.database.execute_query(query, (nowe_haslo, id_pacjenta))
            print(f"Hasło pacjenta o ID {id_pacjenta} zostało zaktualizowane.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd podczas aktualizacji hasła pacjenta: {e}")

    def aktualizuj_haslo_lekarza(self, id_lekarza, nowe_haslo):
        query = "UPDATE DANE_LOGOWANIA_LEKARZE SET haslo = %s WHERE id_lekarza = %s"
        try:
            self.database.execute_query(query, (nowe_haslo, id_lekarza))
            print(f"Hasło lekarza o ID {id_lekarza} zostało zaktualizowane.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd podczas aktualizacji hasła lekarza: {e}")

# klasy aktualizacji i pobierania danych
class IAktualizacjaDanych(ABC):
    @abstractmethod
    def utworz_pacjenta(self, imie, nazwisko, plec, data_urodzenia, email, pesel, haslo):
        pass

    @abstractmethod
    def utworz_wizyte(self, id_lekarza, id_pacjenta, id_zabiegu, godz_rozp, godz_zak):
        pass

    @abstractmethod
    def aktualizuj_wizyte(self, id_wizyty, dzien, godz_rozp, godz_zak):
        pass

    @abstractmethod
    def aktualizuj_uzytkownika(self, id_uzytkownika, rola_uzytkownika, imie=None, nazwisko=None, waga=None, wzrost=None):
        pass

    @abstractmethod
    def aktualizuj_haslo(self, id_uzytkownika, rola_uzytkownika, nowe_haslo):
        pass

    @abstractmethod
    def usun_wizyte(self, id_wizyty):
        pass

class AktualizacjaDanych(IAktualizacjaDanych):
    def __init__(self, database):
        self.database = database

    def utworz_pacjenta(self, imie, nazwisko, plec, data_urodzenia, email, pesel, haslo):
        print(f"Pacjent {imie} {nazwisko} został.")
        query = """
            INSERT INTO PACJENT (imie, nazwisko, plec, data_urodzenia)
            VALUES (%s, %s, %s, %s);
            INSERT INTO DANE_LOGOWANIA_PACJENCI (adres_email, numer_PESEL, haslo)
            VALUES (%s, %s, %s)
        """
        try:
            self.database.execute_query(query, (imie, nazwisko, plec, data_urodzenia, email, pesel, haslo))
            self.database.get_connection().commit()
            print(f"Pacjent {imie} {nazwisko} został utworzony.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd podczas tworzenia pacjenta: {e}")

    def utworz_wizyte(self, id_lekarza, id_pacjenta, id_zabiegu, godz_rozp, godz_zak):
        query = """
            INSERT INTO WIZYTA (id_lekarza, id_pacjenta, id_zabiegu, godzina_rozpoczecia, godzina_zakonczenia)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.database.execute_query(query, (id_lekarza, id_pacjenta, id_zabiegu, godz_rozp, godz_zak))
            self.database.get_connection().commit()
            print(f"Wizyta została utworzona dla pacjenta {id_pacjenta}.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd podczas tworzenia wizyty: {e}")

    def aktualizuj_wizyte(self, id_wizyty, dzien, godz_rozp, godz_zak):
        query = """
            UPDATE WIZYTA
            SET godzina_rozpoczecia = %s, godzina_zakonczenia = %s, dzien = %s
            WHERE id = %s
        """
        try:
            self.database.execute_query(query, (godz_rozp, godz_zak, dzien, id_wizyty))
            self.database.get_connection().commit()
            print(f"Wizyta {id_wizyty} została zaktualizowana. Dzień: {dzien}")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd podczas aktualizacji wizyty: {e}")

    def aktualizuj_uzytkownika(self, id_uzytkownika, rola_uzytkownika, imie=None, nazwisko=None, waga=None,
                               wzrost=None):
        columns = []
        values = []

        if imie is not None:
            columns.append("imie = %s")
            values.append(imie)
        if nazwisko is not None:
            columns.append("nazwisko = %s")
            values.append(nazwisko)
        if waga is not None:
            columns.append("waga = %s")
            values.append(waga)
        if wzrost is not None:
            columns.append("wzrost = %s")
            values.append(wzrost)

        if columns:
            if rola_uzytkownika == 'pacjent':
                query = f"""
                    UPDATE PACJENT
                    SET {', '.join(columns)}
                    WHERE id = %s
                """
            elif rola_uzytkownika == 'lekarz':
                query = f"""
                    UPDATE LEKARZ
                    SET {', '.join(columns)}
                    WHERE id_lekarza = %s
                """
            else:
                return

            values.append(id_uzytkownika)
            try:
                self.database.execute_query(query, tuple(values))
                self.database.get_connection().commit()
                print(f"Dane użytkownika {id_uzytkownika} zostały zaktualizowane.")
            except mysql.connector.Error as e:
                messagebox.showerror("Query Error", f"Błąd aktualizacji użytkownika: {e}")

    def aktualizuj_haslo(self, id_uzytkownika, rola_uzytkownika, nowe_haslo):
        query = ""
        if rola_uzytkownika == 'pacjent':
            query = "UPDATE DANE_LOGOWANIA_PACJENCI SET haslo = %s WHERE id_pacjenta = %s"
        elif rola_uzytkownika == 'lekarz':
            query = "UPDATE DANE_LOGOWANIA_LEKARZE SET haslo = %s WHERE id_lekarza = %s"

        if query:
            try:
                self.database.execute_query(query, (nowe_haslo, id_uzytkownika))
                self.database.get_connection().commit()
                print(f"Hasło użytkownika o ID {id_uzytkownika} zostało zaktualizowane.")
            except mysql.connector.Error as e:
                messagebox.showerror("Query Error", f"Błąd podczas aktualizacji hasła: {e}")

    def usun_wizyte(self, id_wizyty):
        query = "DELETE FROM WIZYTA WHERE id = %s"
        try:
            self.database.execute_query(query, (id_wizyty,))
            self.database.get_connection().commit()
            print(f"Wizyta {id_wizyty} została usunięta.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd podczas usuwania wizyty: {e}")



class IPobieranieDanych(ABC):
    @abstractmethod
    def pobierz_pacjenta(self, id_pacjenta):
        pass

    def pobierz_lekarza(self, id_lekarza):
        pass

    def pobierz_wizyty(self, id_uzytkownika, rola_uzytkownika):
        pass

    def pobierz_dane_logowania(self, id_uzytkownika, rola_uzytkownika):
        pass

    def weryfikacja_uzytkownika(self, login, haslo, rola_uzytkownika):
        pass

    def znajdz_lekarzy(self, kryterium):
        pass

    def dodaj_specjalnosc_lekarzowi(self, id_lekarza, id_specjalnosci):
        pass


class PobieranieDanych(IPobieranieDanych):
    def __init__(self, database):
        self.database = database  # Przekazujemy instancję klasy Database

    def weryfikacja_uzytkownika(self, login, haslo, rola_uzytkownika):
        """Weryfikacja danych logowania użytkownika"""
        if rola_uzytkownika == 'pacjent':
            query = "SELECT id_pacjenta, haslo FROM DANE_LOGOWANIA_PACJENCI WHERE adres_email = %s"
        elif rola_uzytkownika == 'lekarz':
            query = "SELECT id_lekarza, haslo FROM DANE_LOGOWANIA_LEKARZE WHERE adres_email = %s"
        else:
            return None

        cursor = self.database.execute_query(query, (login,))

        if cursor:
            result = cursor.fetchall()
            print("result", result, result[0][0])
            if result:
                return result[0][0]  # Logowanie powiodło się
        return False  # Logowanie nie powiodło się

    def pobierz_pacjenta(self, id_pacjenta):
        """Pobieranie danych pacjenta z bazy danych"""
        query = "SELECT * FROM PACJENT WHERE id = %s"
        cursor = self.database.execute_query(query, (id_pacjenta,))

        if cursor:
            result = cursor.fetchall()
            if result:
                return Pacjent(*result[0])  # Zwracamy pierwszy wynik, jeśli istnieje
        return None

    def pobierz_lekarza(self, id_lekarza):
        """Pobieranie danych lekarza z bazy danych"""
        query = "SELECT * FROM LEKARZ WHERE id= %s"
        cursor = self.database.execute_query(query, (id_lekarza,))

        if cursor:
            result = cursor.fetchall()
            if result:
                return Lekarz(*result[0])  # Zwracamy pierwszy wynik, jeśli istnieje
        return None

    def pobierz_wizyty(self, id_uzytkownika, rola_uzytkownika):
        """Pobieranie wizyt na podstawie użytkownika i jego roli"""
        if rola_uzytkownika == 'pacjent':
            query = "SELECT * FROM WIZYTA WHERE id_pacjenta = %s"
            cursor = self.database.execute_query(query, (id_uzytkownika,))
        elif rola_uzytkownika == 'lekarz':
            query = "SELECT * FROM WIZYTA WHERE id_lekarza = %s"
            cursor = self.database.execute_query(query, (id_uzytkownika,))
        else:
            return None

        if cursor:
            result = cursor.fetchall()
            return result
        return None

    def pobierz_dane_logowania(self, id_uzytkownika, rola_uzytkownika):
        """Pobieranie danych logowania na podstawie roli użytkownika"""
        if rola_uzytkownika == 'pacjent':
            query = "SELECT * FROM DANE_LOGOWANIA_PACJENCI WHERE numer_PESEL = %s"
        elif rola_uzytkownika == 'lekarz':
            query = "SELECT * FROM DANE_LOGOWANIA_LEKARZE WHERE nazwa_uzytkownika = %s"
        else:
            return None

        cursor = self.database.execute_query(query, (id_uzytkownika,))

        if cursor:
            result = cursor.fetchall()
            if result:
                return result[0]  # Zwracamy pierwszy wynik, jeśli istnieje
        return None


    def znajdz_lekarzy(self, kryterium):
        """
        Wyszukiwanie lekarzy w bazie danych na podstawie kryterium.
        """
        query = """
            SELECT l.imie, l.nazwisko, s.nazwa_specjalnosci FROM LEKARZ l
            JOIN LEKARZ_SPECJALNOSC ls ON l.id = ls.id_lekarza
            JOIN SPECJALNOSC s ON ls.id_specjalnosci = s.id
            WHERE LOWER(l.imie) LIKE %s OR LOWER(l.nazwisko) LIKE %s OR LOWER(s.nazwa_specjalnosci) LIKE %s
        """
        wildcard_kryterium = f"%{kryterium.lower()}%"
        cursor = self.database.execute_query(query, (wildcard_kryterium, wildcard_kryterium, wildcard_kryterium))
        if cursor:
            # Konwersja wyników zapytania na obiekty Lekarz
            return [{"imie": row[0], "nazwisko": row[1], "specjalnosc": row[2]} for row in cursor.fetchall()]

        return []

    def dodaj_specjalnosc_lekarzowi(self, id, nazwa_specjalnosci):
        """
        Funkcja dodaje specjalność do lekarza na podstawie nazwy specjalności.
        """
        # Zapytanie SQL do pobrania id_specjalnosci na podstawie nazwy specjalności
        query_get_id_specjalnosci = """
            SELECT id FROM SPECJALNOSC WHERE nazwa_specjalnosci = %s
        """
        try:
            # Znalezienie id_specjalnosci na podstawie nazwy
            result = self.database.execute_query(query_get_id_specjalnosci, (nazwa_specjalnosci,))
            id_specjalnosci = result.fetchone()

            if id_specjalnosci is None:
                messagebox.showerror("Błąd",
                                     f"Specjalność o nazwie '{nazwa_specjalnosci}' nie istnieje w bazie danych.")
                return

            # Pobranie właściwego ID jako liczby
            id_specjalnosci = id_specjalnosci[0]

            # Zapytanie SQL do dodania specjalności dla lekarza
            query_insert = """
                INSERT INTO LEKARZ_SPECJALNOSC (id_lekarza, id_specjalnosci)
                VALUES (%s, %s)
            """
            # Wykonanie zapytania i zatwierdzenie zmian w bazie danych
            self.database.execute_query(query_insert, (id, id_specjalnosci))
            self.database.get_connection().commit()
            print(
                f"Specjalność '{nazwa_specjalnosci}' (ID: {id_specjalnosci}) została dodana do lekarza o ID {id}.")
            messagebox.showinfo("Sukces", f"Specjalność '{nazwa_specjalnosci}' została przypisana do lekarza.")
        except mysql.connector.Error as e:
            messagebox.showerror("Query Error", f"Błąd podczas dodawania specjalności do lekarza: {e}")


# klasa fabryki
class FabrykaModelu:
    def utworz_model(self):
        """
        Zwraca krotkę (pobieranie, aktualizacja) zamiast listy.
        """
        database = Database()
        pobieranie = PobieranieDanych(database)
        aktualizacja = AktualizacjaDanych(database)

        return pobieranie, aktualizacja  # Krotka


    def utworz_obsluge_uzytkownika(self, typ, sterowanie, uzytkownik):
        """
        Tworzy i zwraca odpowiedni obiekt obsługi użytkownika w zależności od typu użytkownika.

        :param typ: Str typ użytkownika ('pacjent' lub 'lekarz')
        :param sterowanie: Obiekt klasy Sterowanie
        :param uzytkownik: Obiekt użytkownika (Pacjent lub Lekarz)
        :return: Obiekt obsługi użytkownika (ObslugaPacjenta lub ObslugaLekarza)
        """

        class ObslugaPacjenta:
            def __init__(self, sterowanie, uzytkownik):
                self.sterowanie = sterowanie
                self.uzytkownik = uzytkownik

            def panel_pacjenta(self):
                pass

        class ObslugaLekarza:
            def __init__(self, sterowanie, uzytkownik):
                self.sterowanie = sterowanie
                self.uzytkownik = uzytkownik

            def panel_lekarza(self):
                pass

        if typ.lower() == "pacjent":
            obsluga = ObslugaPacjenta(sterowanie, uzytkownik)
            obsluga.panel_pacjenta()
            return obsluga
        elif typ.lower() == "lekarz":
            obsluga = ObslugaLekarza(sterowanie, uzytkownik)
            obsluga.panel_lekarza()
            return obsluga
        else:
            raise ValueError(f"Nieznany typ użytkownika: {typ}")
