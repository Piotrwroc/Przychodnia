# from Prezenter import AkcjeUzytkownika
# from Model import Lekarz

import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from tkcalendar import Calendar
from abc import ABC, abstractmethod



class Widok(ABC):  # klasa abstrakcyjna widoków
    def __init__(self, sterowanie):
        self.okno = None
        # vvv Wszystkie metody wywołane stąd przypisane do tego obiektu należy zaimplementować w sterowaniu (prezenter)
        self.sterowanie = sterowanie

    @abstractmethod
    def wyswietl_widok(self):
        pass

    @abstractmethod
    def ustaw_dane(self, opcja):
        pass

    def zamknij_okno(self):
        if messagebox.askokcancel("Zamknąć aplikację?", "Czy na pewno chcesz zamknąć aplikację?"):
            self.okno.destroy()
            exit(0)
        else:
            pass

    def wyswietl_blad(self, wiadomosc):
        messagebox.showwarning("Błąd", wiadomosc)


class WidokLogowania(Widok):
    def __init__(self, sterowanie):
        super().__init__(sterowanie)

        self.pole_haslo = None
        self.pole_email = None
        self.dane = None
        self.wynik = None

    def wyswietl_widok(self):
        # inicjalizacja okna logowania
        self.okno = tk.Tk()
        self.okno.title("Logowanie do systemu")
        self.okno.geometry("400x300")
        self.wynik = tk.IntVar()

        # inicjalizacja elementów interfejsu użytkownika
        ramka = ttk.Frame(self.okno, padding="20")
        ramka.pack(expand=True, fill="both")

        ttk.Label(ramka, text="System przychodni", font=('Helvetica', 16)).pack(pady=10)

        self.pole_email = tk.StringVar()
        self.pole_haslo = tk.StringVar()

        ttk.Label(ramka, text="e-mail:").pack(pady=5)
        ttk.Entry(ramka, textvariable=self.pole_email).pack(pady=5)

        ttk.Label(ramka, text="haslo:").pack(pady=5)
        ttk.Entry(ramka, textvariable=self.pole_haslo).pack(pady=5)

        przyciski = ttk.Frame(ramka)
        przyciski.pack(pady=10)

        ttk.Button(przyciski, text="zaloguj jako pacjent",
                   command=lambda: self.ustaw_dane("pacjent")
                   ).pack(side=tk.LEFT, padx=5)

        ttk.Button(przyciski, text="zaloguj jako lekarz",
                   command=lambda: self.ustaw_dane("lekarz")
                   ).pack(side=tk.LEFT, padx=5)

        rejestracja = ttk.Frame(ramka)
        rejestracja.pack(pady=5)

        ttk.Label(rejestracja, text="nowy pacjent:").pack(side=tk.LEFT, padx=5)

        # Użycie poprawnej metody do rejestracji użytkownika
        ttk.Button(rejestracja, text="zarejestruj",
                   command=self.sterowanie.zarejestruj
                   ).pack(side=tk.LEFT, padx=5)

        self.okno.wait_variable(self.wynik)  # program czeka w momencie, gdy włączone jest okno

    def ustaw_dane(self, rola_uzytkownika):
        if self.pole_email.get().strip() == "" or self.pole_haslo.get().strip() == "":
            self.wyswietl_blad("Przynajmniej jedno z pól jest niewypełnione!")
        else:
            if rola_uzytkownika == "pacjent" or rola_uzytkownika == "lekarz":
                self.dane = (self.pole_email.get(), self.pole_haslo.get(), rola_uzytkownika)
                print(rola_uzytkownika)
            elif rola_uzytkownika == 0:
                self.dane = None

            self.wynik.set(1)  # gdy wartość zmiennej wynik się zmienia, program przestaje czekać
            self.okno.destroy()


class WidokRejestracji:
    def __init__(self, sterowanie):
        self.sterowanie = sterowanie
        self.pola_danych = None
        self.plec = None
        self.dane = None
        self.wynik = tk.IntVar()

    def wyswietl_widok(self):
        self.okno = tk.Tk()
        self.okno.title("Rejestracja pacjenta")
        self.okno.geometry("500x600")

        ramka = ttk.Frame(self.okno, padding="20")
        ramka.pack(expand=True, fill="both")

        ttk.Label(ramka, text="Rejestracja pacjenta", font=('Helvetica', 16)).pack(pady=10)

        self.pola_danych = {}
        for pole in ["imię", "nazwisko", "PESEL", "e-mail", "hasło", "data urodzenia"]:
            ramka_pol = ttk.Frame(ramka)
            ramka_pol.pack(pady=5, fill='x')

            ttk.Label(ramka_pol, text=pole + ":").pack(side=tk.LEFT, padx=5)

            if pole == "hasło":
                self.pola_danych[pole] = ttk.Entry(ramka_pol, show="*")
            elif pole == "data urodzenia":
                self.pola_danych[pole] = Calendar(ramka_pol, selectmode="day", year=2000, month=1, day=1)
            else:
                self.pola_danych[pole] = ttk.Entry(ramka_pol)

            self.pola_danych[pole].pack(side=tk.LEFT, padx=5)

        self.plec = tk.StringVar(value="Mężczyzna")

        ramka_plec = ttk.Frame(ramka)
        ramka_plec.pack(pady=10, fill='x')

        ttk.Label(ramka_plec, text="Płeć:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(ramka_plec, text="Mężczyzna", variable=self.plec, value="Mężczyzna").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(ramka_plec, text="Kobieta", variable=self.plec, value="Kobieta").pack(side=tk.LEFT, padx=5)

        ttk.Button(ramka, text="zarejestruj",
                   command=lambda: self.ustaw_dane(1)
                   ).pack(pady=20)

        ttk.Button(ramka, text="powrót",
                   command=lambda: self.ustaw_dane(0)
                   ).pack(pady=5)

        self.okno.wait_variable(self.wynik)

    from datetime import datetime
    from tkinter import messagebox

    def ustaw_dane(self, opcja):
        # Sprawdzenie, czy są puste pola formularza
        puste_pola = [nazwa for nazwa, widget in self.pola_danych.items()
                      if (isinstance(widget, Calendar) and not widget.get_date()) or
                      (not isinstance(widget, Calendar) and not widget.get().strip())]

        if not self.plec.get():
            puste_pola.append("Płeć")

        if puste_pola:
            print("Przynajmniej jedno z pól jest niewypełnione:", puste_pola)
            messagebox.showerror("Błąd danych", f"Przynajmniej jedno z pól jest niewypełnione: {', '.join(puste_pola)}")
            return  # Nie wykonuj dalszych działań, jeśli są puste pola

        else:
            # Zbieranie danych tylko w przypadku wypełnionych wszystkich pól
            if opcja == 1:
                try:
                    # Pobranie danych z formularza
                    imie = self.pola_danych["imię"].get()
                    nazwisko = self.pola_danych["nazwisko"].get()
                    plec = self.plec.get()
                    email = self.pola_danych["e-mail"].get()
                    pesel = self.pola_danych["PESEL"].get()
                    haslo = self.pola_danych["hasło"].get()

                    # Próba konwersji daty urodzenia do formatu `YYYY-MM-DD`
                    data_urodzenia_string = self.pola_danych["data urodzenia"].get_date()

                    try:
                        # Sparsuj datę w formacie MM/DD/YY
                        data_urodzenia = datetime.strptime(data_urodzenia_string, "%m/%d/%y").date()
                    except ValueError:
                        raise ValueError("Nieprawidłowy format daty! Oczekiwany format: MM/DD/YY.")

                    # Konwersja daty do formatu zgodnego z MySQL
                    data_urodzenia_mysql = data_urodzenia.strftime("%Y-%m-%d")

                    # Przygotowanie danych w odpowiedniej kolejności
                    self.sterowanie.dane = [
                        imie, nazwisko, plec, data_urodzenia_mysql, email, pesel, haslo
                    ]
                    print(f"Debug - dane przekazywane do rejestracji: {self.sterowanie.dane}")
                    print(f"Typy danych: {[type(d) for d in self.sterowanie.dane]}")

                    print(f"Dane wygenerowane w widoku: {self.sterowanie.dane}")

                    # Wywołanie metody zarejestruj_2
                    try:
                        self.sterowanie.zarejestruj_2()
                    except AttributeError:
                        print("Błąd: Obiekt `sterowanie` nie zawiera metody `zarejestruj_2`.")
                        messagebox.showerror(
                            "Błąd aplikacji",
                            "Wystąpił problem z rejestracją: brak metody `zarejestruj_2` w obiekcie `sterowanie`."
                        )
                        return  # Zatrzymaj działanie w przypadku braku metody

                except ValueError as ve:
                    print(f"Błąd: {ve}")
                    messagebox.showerror("Błąd danych", str(ve))
                    return  # Przerwij w przypadku błędu formatu daty

                except Exception as ex:
                    print(f"Unexpected error: {str(ex)}")
                    messagebox.showerror("Błąd aplikacji", f"Nieoczekiwany błąd: {str(ex)}")
                    return  # Obsługa innych, nieoczekiwanych błędów

                # Ustawienie wyniku dopiero po poprawnym wykonaniu danych
                else:
                    self.dane = None
                    self.wynik.set(1)
                    self.okno.destroy()


class WidokLekarza(Widok):
    @abstractmethod
    def wyswietl_widok(self, dane_we=None):
        pass

    @abstractmethod
    def ustaw_dane(self, opcja):
        pass


class WidokPacjenta(Widok):
    @abstractmethod
    def wyswietl_widok(self, dane_we=None):
        pass

    @abstractmethod
    def ustaw_dane(self, opcja):
        pass


# tutaj zaczyna się pierdolnik
class WidokPanelPacjenta:
    def __init__(self, sterowanie):
        """
        :param zawartosc: Zawartość graficzna, gdzie będą renderowane dane.
        :param dane_pobieranie: Obiekt implementujący IPobieranieDanych.
        """
        self.sterowanie = sterowanie
        # self.dane_pobieranie = sterowanie.dane_pobieranie  # Zależność danych

    def szukaj_lekarzy(self, kryterium):
        for widget in self.zawartosc.winfo_children():
            if isinstance(widget, ttk.Treeview):
                widget.destroy()

        # Pobieranie lekarzy przez implementację IPobieranieDanych
        znalezieni_lekarze = self.sterowanie.znajdz_lekarzy(kryterium)

        if znalezieni_lekarze:
            kolumny = ("Imię", "Nazwisko", "Specjalność")
            tabela = ttk.Treeview(self.zawartosc, columns=kolumny, show='headings')

            for kolumna in kolumny:
                tabela.heading(kolumna, text=kolumna)

            for lekarz in znalezieni_lekarze:
                tabela.insert('', 'end', values=(lekarz.imie, lekarz.nazwisko, lekarz.specjalnosc))

            tabela.pack(pady=10, fill='both', expand=True)

            # Wybieranie lekarza
            def wybierz_lekarza(event):
                wybrany_lekarz = event.widget.selection()
                if not wybrany_lekarz:
                    return

                wartosci = event.widget.item(wybrany_lekarz[0])["values"]
                imie_lekarza = f"{wartosci[0]} {wartosci[1]}"

                self.umow_na_wizyte(imie_lekarza, wartosci[2])

            tabela.bind("<Double-1>", wybierz_lekarza)
        else:
            ttk.Label(self.zawartosc, text="Nie znaleziono żadnego lekarza.", font=("Helvetica", 12),
                      foreground="red").pack(pady=10)


    # na razie jeszcze git, nie trzeba dużo tłumaczyć
    def wyswietl_widok(self, dane_we=None):
        self.pacjent = dane_we[0]
        self.wizyty = dane_we[1]

        # inicjalizacja okna panelu pacjenta
        self.okno = tk.Tk()
        self.okno.title("Panel pacjenta")
        self.okno.geometry("800x600")
        self.wynik = tk.IntVar()

        pasek_boczny = ttk.Frame(self.okno, padding="10", relief="raised")
        pasek_boczny.pack(side="left", fill="y")

        self.zawartosc = ttk.Frame(self.okno, padding="20")
        self.zawartosc.pack(side="right", expand=True, fill="both")

        # inicjalizacja przycisków
        ttk.Button(pasek_boczny, text="Moje wizyty",
                   command=self.pokaz_wizyty).pack(pady=5, fill="x")
        ttk.Button(pasek_boczny, text="Umów wizytę",
                   command=self.pokaz_umowienie_wizyty).pack(pady=5, fill="x")
        ttk.Button(pasek_boczny, text="Mój profil",
                   command=self.pokaz_profil).pack(pady=5, fill="x")
        ttk.Button(pasek_boczny, text="Wyloguj",
                   command=self.wyloguj).pack(pady=5, fill="x")

        # domyślnie wyświetla wizyty
        self.pokaz_wizyty()
        print("Widok panelu pacjenta gotowy.")
        self.okno.wait_variable(self.wynik)
    def wyloguj(self):
        if messagebox.askokcancel("Wylogować?", "Czy na pewno chcesz się wylogować?"):
            self.wynik.set(1)
            self.okno.destroy()
            self.sterowanie.zaloguj()

    def pokaz_profil(self):
        # wyczyść zawartość ramki
        for widget in self.zawartosc.winfo_children():
            widget.destroy()

        ttk.Label(self.zawartosc, text="Mój profil", font=("Helvetica", 16)).pack(pady=10)

        # sprawdzanie, czy obiekt self.pacjent został zainicjalizowany
        if not self.pacjent:
            ttk.Label(self.zawartosc, text="Brak danych pacjenta do wyświetlenia.", font=("Helvetica", 12),
                      foreground="red").pack(pady=10)
            return

        # wyświetlenie danych pacjenta
        ttk.Label(self.zawartosc, text=f"Imię: {getattr(self.pacjent, 'imie', 'N/D')}").pack(pady=5)
        ttk.Label(self.zawartosc, text=f"Nazwisko: {getattr(self.pacjent, 'nazwisko', 'N/D')}").pack(pady=5)
        ttk.Label(self.zawartosc, text=f"PESEL: {getattr(self.pacjent, 'pesel', 'N/D')}").pack(pady=5)
        ttk.Label(self.zawartosc, text=f"e-mail: {getattr(self.pacjent, 'email', 'N/D')}").pack(pady=5)
        ttk.Label(self.zawartosc, text=f"Data urodzenia: {getattr(self.pacjent, 'data_urodzenia', 'N/D')}").pack(pady=5)
        ttk.Label(self.zawartosc, text=f"waga: {getattr(self.pacjent, 'waga', 'N/D')}").pack(pady=5)
        ttk.Label(self.zawartosc, text=f"wzrost: {getattr(self.pacjent, 'wzrost', 'N/D')}").pack(pady=5)

    from datetime import datetime

    def pokaz_wizyty(self):
        # Wyczyszczenie zawartości ramki
        for widget in self.zawartosc.winfo_children():
            widget.destroy()

        ttk.Label(self.zawartosc, text="Moje wizyty", font=("Helvetica", 16)).pack(pady=10)

        # Pobranie aktualnego czasu
        teraz = datetime.now()

        # Konwersja wizyta[3] na datetime, jeśli jest w formacie int (np. UNIX timestamp)
        wizyty_nadchodzace = []
        wizyty_ubiegle = []

        for wizyta in self.wizyty:
            try:
                # Sprawdzanie i konwersja wizyta[3] (jeśli wymagane)
                if isinstance(wizyta[3], int):
                    start = datetime.fromtimestamp(wizyta[3])
                else:
                    start = wizyta[3]

                # Sortowanie wizyt na nadchodzące i ubiegłe
                if start > teraz:
                    wizyty_nadchodzace.append(wizyta)
                else:
                    wizyty_ubiegle.append(wizyta)
            except Exception as e:
                print(f"Problem z wizytą: {wizyta}. Błąd: {e}")

        kolumny = ("ID", "Lekarz", "Data", "Godzina", "Zabieg", "Dzien")

        # Tabele nadchodzących wizyt
        ttk.Label(self.zawartosc, text="Nadchodzące wizyty", font=("Helvetica", 14)).pack(pady=5)
        tabela_nadchodzace = ttk.Treeview(self.zawartosc, columns=kolumny, show="headings")

        for kolumna in kolumny:
            tabela_nadchodzace.heading(kolumna, text=kolumna)
            tabela_nadchodzace.column(kolumna, width=100)

        for (id_wizyty, imie, nazwisko, start_timestamp, koniec, zabieg) in wizyty_nadchodzace:
            # Formatowanie daty i godziny
            data = start_timestamp.strftime('%Y-%m-%d')
            godzina = f"{start_timestamp.strftime('%H:%M')} - {koniec.strftime('%H:%M')}"
            tabela_nadchodzace.insert('', "end", values=(id_wizyty, f"{imie} {nazwisko}", data, godzina, zabieg))

        tabela_nadchodzace.pack(pady=10, fill='both', expand=True)

        # Tabele ubiegłych wizyt
        ttk.Label(self.zawartosc, text="Ubiegłe wizyty", font=("Helvetica", 14)).pack(pady=5)
        tabela_ubiegle = ttk.Treeview(self.zawartosc, columns=kolumny, show="headings", selectmode="none")

        for kolumna in kolumny:
            tabela_ubiegle.heading(kolumna, text=kolumna)
            tabela_ubiegle.column(kolumna, width=100)

        for (id_wizyty, imie, nazwisko, start_timestamp, koniec, zabieg, godzina) in wizyty_ubiegle:
            # Konwersja start_timestamp na obiekt datetime, jeśli to wartość UNIX timestamp
            if isinstance(start_timestamp, int):
                start_timestamp = datetime.fromtimestamp(start_timestamp)
            if isinstance(koniec, int):
                koniec = datetime.fromtimestamp(koniec)

            # Formatowanie daty i godziny
            data = start_timestamp.strftime('%Y-%m-%d')
            godzina = f"{start_timestamp.strftime('%H:%M')} - {koniec.strftime('%H:%M')}"
            tabela_ubiegle.insert('', "end", values=(id_wizyty, f"{imie} {nazwisko}", data, godzina, zabieg))

        tabela_ubiegle.pack(pady=10, fill='both', expand=True)

        przycisk = ttk.Frame(self.zawartosc)
        przycisk.pack(pady=10)

        ttk.Button(przycisk, text="Anuluj wizytę",
                   command=lambda: self.anuluj_wizyte(tabela_nadchodzace)).pack(side='left', padx=5)
        ttk.Button(przycisk, text="Zmień termin wizyty",
                   command=lambda: self.zmien_termin(tabela_nadchodzace)).pack(side='left', padx=5)

        self.okno.wait_variable(self.wynik)

    # anulowanie wizyty, nadal dosyć proste
    def anuluj_wizyte(self, tabela):
        wybrana = tabela.selection()
        if not wybrana:
            messagebox.showwarning("Nie wybrano wizyty", "Proszę wybrać wizytę do anulowania")
            return

        id_wizyty = tabela.item(wybrana[0], "values")[0]

        if messagebox.askyesno("Wymagane potwierdzenie", "Czy na pewno chcesz anulować wybraną wizytę?"):
            self.sterowanie.usun_wizyte(id_wizyty)
            self.pokaz_wizyty()

    # entering danger zone
    # zmiana terminu wizyty
    def zmien_termin(self, tabela):
        wybrana = tabela.selection()
        if not wybrana:
            messagebox.showwarning("Nie wybrano wizyty", "Proszę wybrać wizytę, której termin należy zmienić")
            return

        id_wizyty = tabela.item(wybrana[0], "values")[0]
        # wyszukanie ID zabiegu potrzebnego do ustalenia dostępnych godzin
        # wyszukanie lekarza potrzebnego do sprawdzenia harmonogramu + pozostałych wizyt
        lekarz, id_zabiegu = self.sterowanie.pobierz_lekarza_zabieg(id_wizyty)

        # utworzenie okna wyboru dnia
        wybor_dnia = tk.Toplevel(self.okno)
        wybor_dnia.title("Wybierz dzień wizyty")
        wybor_dnia.geometry("400x300")

        ramka = ttk.Frame(wybor_dnia, padding=20)
        ramka.pack(expand=True, fill="both")

        kalendarz = Calendar(ramka, selectmode='day', date_pattern='yyyy-mm-dd')
        kalendarz.pack(pady=5)

        # funkcja do potwierdzenia dostępności dnia wizyty
        def potwierdz_dzien():
            wybrany_dzien = kalendarz.get_date()

            # sprawdza dostępne godziny na podstawie zabiegu i harmonogramu lekarza
            dostepne_godziny = self.sterowanie.pobierz_godziny(wybrany_dzien, lekarz.id, id_zabiegu)

            # jeśli puste to trzeba wybrać inny termin
            if not dostepne_godziny:
                messagebox.showwarning("Niedostępny dzień", "Wybrany dzień jest niedostępny!")
                return

            self.wybierz_godzine(wybrany_dzien, id_zabiegu, lekarz.id, dostepne_godziny, "nowy_termin",
                                 id_wizyty=id_wizyty)

        ttk.Button(ramka, text="Potwierdź dzień", command=potwierdz_dzien()).pack(pady=10)

    # umawianie na wizyte
    def pokaz_umowienie_wizyty(self):
        for widget in self.zawartosc.winfo_children():
            widget.destroy()

        ttk.Label(self.zawartosc, text="Umów wizytę", font=("Helvetica", 16)).pack(pady=10)

        ramka_szukania = ttk.Frame(self.zawartosc)
        ramka_szukania.pack(pady=10, fill='x')

        ttk.Label(ramka_szukania, text="Wyszukaj lekarza po imieniu, nazwisku lub specjalności").pack(side='left',
                                                                                                      padx=5)
        szukanie_var = tk.StringVar()
        ttk.Entry(ramka_szukania, textvariable=szukanie_var).pack(side='left', padx=5)
        ttk.Button(ramka_szukania, text="Szukaj",
                   command=lambda: self.szukaj_lekarzy(szukanie_var.get())).pack(side='left', padx=5)

    # wyszukiwanie lekarzy na podstawie wpisanego kryterium
    def szukaj_lekarzy(self, kryterium):
        for widget in self.zawartosc.winfo_children():
            if isinstance(widget, ttk.Treeview):
                widget.destroy()

        # Wykorzystanie przekazanej metody znajdz_lekarzy
        znalezieni_lekarze = self.znajdz_lekarzy(kryterium)

        if znalezieni_lekarze:
            kolumny = ("Imię", "Nazwisko", "Specjalność")
            tabela = ttk.Treeview(self.zawartosc, columns=kolumny, show='headings')

            for kolumna in kolumny:
                tabela.heading(kolumna, text=kolumna)

            for lekarz in znalezieni_lekarze:
                tabela.insert('', 'end', values=(lekarz["imie"], lekarz["nazwisko"], lekarz["specjalnosc"]))

            tabela.pack(pady=10, fill='both', expand=True)

            # Wybieranie lekarza
            def wybierz_lekarza(event):
                wybrany_lekarz = event.widget.selection()
                if not wybrany_lekarz:
                    return

                wartosci = event.widget.item(wybrany_lekarz[0])["values"]
                imie_lekarza = f"{wartosci[0]} {wartosci[1]}"

                self.umow_na_wizyte(imie_lekarza, wartosci[2])

            tabela.bind("<Double-1>", wybierz_lekarza)
        else:
            ttk.Label(self.zawartosc, text="Nie znaleziono żadnego lekarza.", font=("Helvetica", 12),
                      foreground="red").pack(pady=10)


def umow_na_wizyte(self, imie_lekarza, specjalnosc):
    # teraz trzeba pobrać lekarza na podstawie imienia i nazwiska - aby uzyskać dostęp do ID XD
    lekarz = self.sterowanie.pobierz_lekarza_imie(imie_lekarza)
    # pobieranie zabiegów lekarza z zadanej specjalności
    zabiegi = self.sterowanie.pobierz_wykonywane_zabiegi(lekarz.id, specjalnosc)
    zabiegi_dict = {zabieg[1]: zabieg[0] for zabieg in zabiegi}

    # okno wyboru zabiegu i dnia wizyty
    wybor_zabiegu_dnia = tk.Toplevel(self.okno)
    wybor_zabiegu_dnia.title("Wybierz zabieg i dzień wizyty")
    wybor_zabiegu_dnia.geometry("400x400")

    ramka = ttk.Frame(wybor_zabiegu_dnia, padding=20)
    ramka.pack(expand=True, fill='both')

    # lista zabiegów
    nazwy_zabiegow = list(zabiegi_dict.keys())
    zabiegi_combobox = ttk.Combobox(ramka, values=nazwy_zabiegow)
    zabiegi_combobox.pack(pady=10)

    if nazwy_zabiegow:
        zabiegi_combobox.current(0)

    kalendarz = Calendar(ramka, selectmode='day', date_pattern='yyyy-mm-dd')
    kalendarz.pack(pady=10)

    # funkcja do potwierdzenia dostępności dnia wizyty
    def potwierdz_dzien():
        wybrany_dzien = kalendarz.get_date()
        id_zabiegu = zabiegi_dict[zabiegi_combobox.get()]

        dostepne_godziny = self.sterowanie.pobierz_godziny(wybrany_dzien, lekarz.id, id_zabiegu)

        if not dostepne_godziny:
            messagebox.showwarning("Niedostępny dzień", "Wybrany dzień jest niedostępny!")
            return

        self.wybierz_godzine(
            wybrany_dzien, id_zabiegu, lekarz.id, dostepne_godziny, "nowa_wizyta"
        )

    ttk.Button(ramka, text="Potwierdź zabieg i dzień", command=potwierdz_dzien).pack(pady=5)


    def ustaw_dane(self, opcja):
        # Tu dodaj implementację, która ustawia dane (np. dane pacjenta, wizyty itp.)
        print("Ustawianie danych pacjenta.")


class WidokPanelLekarza(WidokLekarza):  # Dziedziczenie po WidokLekarza
    def __init__(self, sterowanie):
        super().__init__(sterowanie)  # Inicjalizacja klasy bazowej
        self.zawartosc = None

        self.lekarz = None
        self.specjalnosci = []
        self.zabiegi = []

    def wyswietl_widok(self, dane_we=None):
        """
        Implementacja metody wyswietl_widok z klasy abstrakcyjnej.
        Wyświetla panel lekarza z danymi lekarza i jego specjalnościami.
        """
        self.pokaz_profil_lekarza(dane_we)

    def ustaw_dane(self, opcja):
        """
        Implementacja metody ustaw_dane z klasy abstrakcyjnej.
        Przypisuje dane do aktualnego widoku (np. specjalności lub zabiegi).
        """
        if opcja == "specjalnosci":
            self.specjalnosci = self.sterowanie.pobierz_specjalnosci_lekarza()
        elif opcja == "zabiegi":
            self.zabiegi = self.sterowanie.pobierz_zabiegi_lekarza()

    def pokaz_profil_lekarza(self, dane_we=None):
        """
        Wyświetla profil lekarza z jego informacjami i pozwala na dodawanie specjalności lub zabiegów.
        Obsługuje scenariusz, gdy dane_we nie zawierają pełnych danych.
        """
        self.lekarz = dane_we[0] if dane_we and len(dane_we) > 0 else None
        self.specjalnosci = dane_we[1] if dane_we and len(dane_we) > 1 else []
        self.zabiegi = dane_we[2] if dane_we and len(dane_we) > 2 else []

        # Inicjalizacja okna panelu lekarza
        self.okno = tk.Tk()
        self.okno.title("Panel lekarza")
        self.okno.geometry("800x600")

        self.zawartosc = ttk.Frame(self.okno)
        self.zawartosc.pack(fill="both", expand=True)

        ttk.Label(self.zawartosc, text="Mój profil", font=("Helvetica", 16)).pack(pady=10)

        if self.lekarz:
            # Zakładamy, że self.lekarz posiada atrybuty odpowiednich typów (np. stringi)
            ttk.Label(self.zawartosc, text=f"Imię: {self.lekarz.imie}").pack(pady=5)
            ttk.Label(self.zawartosc, text=f"Nazwisko: {self.lekarz.nazwisko}").pack(pady=5)
            ttk.Label(self.zawartosc, text=f"data_urodzenia: {self.lekarz.data_urodzenia}").pack(pady=5)
            ttk.Label(self.zawartosc, text=f"Specjalizacja: {', '.join(self.specjalnosci)}").pack(pady=5)

        ttk.Label(self.zawartosc, text="Zabiegi:", font=("Helvetica", 14)).pack(pady=5)
        for zabieg in self.zabiegi:
            ttk.Label(self.zawartosc, text=f"- {zabieg}", font=("Helvetica", 12)).pack(pady=2)

        ttk.Button(self.zawartosc, text="Dodaj specjalność", command=self.dodaj_specjalnosc).pack(pady=10)
        ttk.Button(self.zawartosc, text="Dodaj zabieg", command=self.dodaj_zabieg).pack(pady=10)

        ttk.Button(self.zawartosc, text="Wyloguj",
                   command=self.wyloguj).pack(pady=5, fill="x")
        self.okno.mainloop()

        #
        # # domyślnie wyświetla wizyty
        # self.pokaz_wizyty()
        # print("Widok panelu pacjenta gotowy.")
        # self.okno.wait_variable(self.wynik)

    def wyloguj(self):
        if messagebox.askokcancel("Wylogować?", "Czy na pewno chcesz się wylogować?"):
            # self.wynik.set(1)
            self.okno.destroy()
            self.sterowanie.zaloguj()

    def dodaj_specjalnosc(self):
        okno_dodawania = tk.Toplevel()
        okno_dodawania.title("Dodaj specjalność")
        okno_dodawania.geometry("300x200")

        ttk.Label(okno_dodawania, text="Podaj nową specjalność:", font=("Helvetica", 12)).pack(pady=10)
        specjalnosc_var = tk.StringVar()
        ttk.Entry(okno_dodawania, textvariable=specjalnosc_var).pack(pady=5)

        def potwierdz_dodanie():
            nowa_specjalnosc = specjalnosc_var.get()
            if nowa_specjalnosc:
                id = self.lekarz.id  # Pobranie ID lekarza
                if self.sterowanie.dodaj_specjalnosc_do_lekarza(id, nowa_specjalnosc):
                    self.specjalnosci.append(nowa_specjalnosc)
                    messagebox.showinfo("Sukces", "Specjalność została dodana")
                    self.pokaz_profil_lekarza()
                else:
                    messagebox.showerror("Błąd", "Nie udało się dodać specjalności")

        ttk.Button(okno_dodawania, text="Dodaj", command=potwierdz_dodanie).pack(pady=10)

    def dodaj_zabieg(self):
        okno_dodawania = tk.Toplevel()
        okno_dodawania.title("Dodaj zabieg")
        okno_dodawania.geometry("300x200")

        ttk.Label(okno_dodawania, text="Podaj nowy zabieg:", font=("Helvetica", 12)).pack(pady=10)
        zabieg_var = tk.StringVar()
        ttk.Entry(okno_dodawania, textvariable=zabieg_var).pack(pady=5)

        def potwierdz_dodanie():
            nowy_zabieg = zabieg_var.get()
            if nowy_zabieg:
                if self.sterowanie.dodaj_zabieg_do_lekarza(nowy_zabieg):
                    self.zabiegi.append(nowy_zabieg)
                    messagebox.showinfo("Sukces", "Zabieg został dodany")
                    self.pokaz_profil_lekarza()
                else:
                    messagebox.showerror("Błąd", "Nie udało się dodać zabiegu")

        ttk.Button(okno_dodawania, text="Dodaj", command=potwierdz_dodanie).pack(pady=10)


class FabrykaWidokow:
    def utworz_widok(self, sterowanie, rodzaj):
        if rodzaj == "logowanie":
            return WidokLogowania(sterowanie)
        elif rodzaj == "rejestracja":
            return WidokRejestracji(sterowanie)
        elif rodzaj == "panel_pacjenta":
            # Dodano przekazanie brakującego argumentu 'dane_pobieranie'
            return WidokPanelPacjenta(sterowanie)
        elif rodzaj == "panel_lekarza":
            return WidokPanelLekarza(sterowanie)
