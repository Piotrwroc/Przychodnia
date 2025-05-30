from datetime import datetime

from Model import FabrykaModelu, IPobieranieDanych, IAktualizacjaDanych, Lekarz, Pacjent, Wizyta, DaneLogowania
from Widok import FabrykaWidokow

from abc import ABC, abstractmethod


class AkcjeUzytkownika(ABC):
    @abstractmethod
    def pobierz_lekarza_zabieg(self, id_wizyty):
        pass

    @abstractmethod
    def pobierz_dni_pracy(self, id_lekarza):
        pass

    @abstractmethod
    def pobierz_godziny_pracy(self, id_lekarza, zabieg, dzien):
        pass


class Sterowanie:
    def __init__(self, fabrykaModelu, fabrykaWidokow):
        self.obecnyWidok = None
        self.AktualizacjaDanych = None
        self.PobieranieDanych = None
        self.fabrykaModelu = fabrykaModelu
        self.fabrykaWidokow = fabrykaWidokow

        # Rozpakowanie krotki na dwie zmienne
        self.pobieranieDanych, self.aktualizacjaDanych = self.fabrykaModelu.utworz_model()

        # Sprawdzanie zgodności z interfejsami
        if not isinstance(self.pobieranieDanych, IPobieranieDanych):
            raise TypeError("pobieranieDanych must implement IPobieranieDanych interface.")

        if not isinstance(self.aktualizacjaDanych, IAktualizacjaDanych):
            raise TypeError("aktualizacjaDanych must implement IAktualizacjaDanych interface.")

    def uruchom(self):
        # Rozpoczęcie działania aplikacji
        self.zaloguj()

    def zaloguj(self):
        self.obecnyWidok = self.fabrykaWidokow.utworz_widok(self, "logowanie")
        self.obecnyWidok.wyswietl_widok()

        dane_logowania = self.obecnyWidok.dane
        [self.pobieranieDanych, self.aktualizacjaDanych] = self.fabrykaModelu.utworz_model()

        id_uzytkownika = self.pobieranieDanych.weryfikacja_uzytkownika(dane_logowania[0], dane_logowania[1],
                                                                       dane_logowania[2])
        print("elo", id_uzytkownika)
        if id_uzytkownika == -1:
            self.obecnyWidok.wyswietl_blad("Niepoprawne dane logowania!")
            self.zaloguj()
        else:
            if dane_logowania[2] == "pacjent":
                print("id_uzytkownika", id_uzytkownika)
                pacjent = self.pobieranieDanych.pobierz_pacjenta(id_uzytkownika)
                print("pacjent", pacjent)
                self.obslugaUzytkownika = ObslugaPacjenta(self, pacjent)
                self.obslugaUzytkownika.panel_pacjenta()
            elif dane_logowania[2] == "lekarz":
                lekarz = self.pobieranieDanych.pobierz_lekarza(id_uzytkownika)
                self.obslugaUzytkownika = ObslugaLekarza(self, lekarz)
                self.obslugaUzytkownika.panel_lekarza()
    def zarejestruj(self):
        print("rejestracja1")
        self.obecnyWidok = self.fabrykaWidokow.utworz_widok(self, "rejestracja")
        self.obecnyWidok.wyswietl_widok()

    def zarejestruj_2(self):
        print("Rejestracja użytkownika rozpoczęta.")

        # Sprawdź, czy dane zostały przypisane
        if not hasattr(self, "dane") or not self.dane:
            raise ValueError("Nie przypisano danych do obiektu przed rejestracją.")

        print(f"Rejestrowanie użytkownika z danymi: {self.dane}")

        dane_pacjenta = self.obecnyWidok.dane

        # Sprawdź, czy dane_pacjenta są prawidłowe
        if not dane_pacjenta:
            raise ValueError("Dane pacjenta są puste.")
        if not isinstance(dane_pacjenta, list):
            raise ValueError("Dane pacjenta są nieprawidłowe.")

        if len(dane_pacjenta) < 7:
            raise ValueError(
                f"Dane użytkownika są niekompletne. Oczekiwano 7 elementów, otrzymano {len(dane_pacjenta)}.")

        try:
            # Konwersja daty urodzenia na format MM/DD/YY

            # Wywołaj metodę utworz_pacjenta z poprawioną datą
            dodany = self.fabrykaModelu.utworz_pacjenta(
                dane_pacjenta[0],  # imię
                dane_pacjenta[1],  # nazwisko
                dane_pacjenta[2],  # płeć
                dane_pacjenta[3],  # data urodzenia jako YYYY-MM-DD
                dane_pacjenta[4],  # email
                dane_pacjenta[5],  # PESEL
                dane_pacjenta[6]  # hasło
            )

            # Sprawdzenie wyniku rejestracji
            if dodany == -1:
                self.obecnyWidok.wyswietl_blad("Istnieje już konto przypisane do adresu e-mail lub numeru PESEL.")
            elif dodany is None:
                print("Uwaga: Metoda utworz_pacjenta zwróciła wartość None. Sprawdź logikę tej metody.")
            else:
                print("Rejestracja zakończona sukcesem.")
                self.zaloguj()

        except Exception as ex:
            print(f"Nieoczekiwany błąd podczas rejestracji: {ex}")

    def pobierz_lekarza_zabieg(self, id_wizyty):
        """
        Pobiera lekarza i zabieg na podstawie ID wizyty.
        """
        # Przykładowa implementacja:
        wizyta = self.pobieranieDanych.pobierz_wizyte(id_wizyty)
        if wizyta:
            lekarz = self.pobieranieDanych.pobierz_lekarza(wizyta.id_lekarza)
            zabieg = self.pobieranieDanych.pobierz_zabieg(wizyta.id_zabiegu)
            return lekarz, zabieg
        return None, None

    def pobierz_dni_pracy(self, id_lekarza):
        """
        Pobiera dostępne dni pracy lekarza.
        """
        # Przykładowa implementacja:
        return self.pobieranieDanych.pobierz_dni_pracy_lekarza(id_lekarza)

    def pobierz_godziny_pracy(self, id_lekarza, zabieg, dzien):
        """
        """
        # Przykładowa implementacja:
        return self.pobieranieDanych.pobierz_godziny_pracy_lekarza(id_lekarza, zabieg, dzien)

    def szukaj_lekarzy(self, kryterium):
        """
        Obsługuje logikę wyszukiwania lekarzy na podstawie kryterium.
        """
        if not self.pobieranieDanych:
            raise ValueError("Brak obiektu pobieranieDanych.")

        znalezieni_lekarze = self.pobieranieDanych.znajdz_lekarzy(kryterium)
        if not znalezieni_lekarze:
            # Obsłuż brak wyników
            self.obecnyWidok.wyswietl_blad("Nie znaleziono lekarzy spełniających kryterium.")
        else:
            # Wyświetl listę znalezionych lekarzy
            self.obecnyWidok.wyswietl_lekarzy(znalezieni_lekarze)

    def dodaj_specjalnosc_do_lekarza(self, id, nazwa_specjalnosci):
        """
        Wywołuje metodę w fabryka_modelu, aby dodać specjalność.
        """
        return self.AktualizacjaDanych.dodaj_specjalnosc_lekarzowi(id, nazwa_specjalnosci)


class ObslugaUzytkownika(ABC):
    pass

class ObslugaLekarza(ObslugaUzytkownika):
    def __init__(self, sterowanie, lekarz):
        self.sterowanie = sterowanie
        self.lekarz = lekarz
        self.wizyty = self.sterowanie.pobieranieDanych.pobierz_wizyty(lekarz.id, "lekarz")

    def panel_lekarza(self):
        self.sterowanie.obecnyWidok = self.sterowanie.fabrykaWidokow.utworz_widok(self.sterowanie, "panel_lekarza")
        self.sterowanie.obecnyWidok.wyswietl_widok([self.lekarz, self.wizyty])


class ObslugaPacjenta(ObslugaUzytkownika):
    def __init__(self, sterowanie, pacjent):
        self.sterowanie = sterowanie
        self.pacjent = pacjent
        self.wizyty = self.sterowanie.pobieranieDanych.pobierz_wizyty(pacjent.id, "pacjent")

    def panel_pacjenta(self):
        self.sterowanie.obecnyWidok = self.sterowanie.fabrykaWidokow.utworz_widok(self.sterowanie, "panel_pacjenta")
        self.sterowanie.obecnyWidok.wyswietl_widok([self.pacjent, self.wizyty])

if __name__ == "__main__":
    fabryka_modelu = FabrykaModelu()
    fabryka_widokow = FabrykaWidokow()

    # Przekazanie fabryk podczas inicjalizacji klasy Sterowanie
    sterowanie = Sterowanie(fabryka_modelu, fabryka_widokow)
    sterowanie.uruchom()