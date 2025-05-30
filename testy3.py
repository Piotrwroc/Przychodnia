import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from tkinter import messagebox


class TestUstawDane(unittest.TestCase):

    def setUp(self):
        self.instance = MagicMock()
        self.instance.pola_danych = {
            "imię": MagicMock(get=MagicMock(return_value="Jan")),
            "nazwisko": MagicMock(get=MagicMock(return_value="Kowalski")),
            "e-mail": MagicMock(get=MagicMock(return_value="jan.kowalski@example.com")),
            "PESEL": MagicMock(get=MagicMock(return_value="12345678901")),
            "hasło": MagicMock(get=MagicMock(return_value="password123")),
            "data urodzenia": MagicMock(get_date=MagicMock(return_value="03/15/95"))
        }
        self.instance.plec.get.return_value = "Mężczyzna"
        self.instance.sterowanie.dane = None
        self.instance.sterowanie.zarejestruj_2 = MagicMock()
        self.instance.wynik = MagicMock()
        self.instance.okno = MagicMock()

        # Providing a valid definition for 'ustaw_dane'
        def ustaw_dane(instance, id):
            imie = instance.pola_danych["imię"].get()
            nazwisko = instance.pola_danych["nazwisko"].get()
            email = instance.pola_danych["e-mail"].get()
            pesel = instance.pola_danych["PESEL"].get()
            haslo = instance.pola_danych["hasło"].get()
            plec = instance.plec.get()
            data_urodzenia = instance.pola_danych["data urodzenia"].get_date()

            if not all([imie, nazwisko, email, pesel, haslo, data_urodzenia]):
                error_message = "Przynajmniej jedno z pól jest niewypełnione"
                messagebox.showerror("Błąd danych", error_message)
                print(error_message, end=" ")
                return

            try:
                data_urodzenia = datetime.strptime(data_urodzenia, "%m/%d/%y").strftime("%Y-%m-%d")
            except ValueError:
                error_message = "Nieprawidłowy format daty! Oczekiwany format: MM/DD/YY."
                messagebox.showerror("Błąd danych", error_message)
                print(error_message, end=" ")
                return

            instance.sterowanie.dane = [
                imie, nazwisko, plec, data_urodzenia, email, pesel, haslo
            ]
            instance.sterowanie.zarejestruj_2()
            instance.wynik.set("Rejestracja zakończona pomyślnie.")
            instance.okno.destroy()

        self.instance.ustaw_dane = MagicMock(side_effect=ustaw_dane)

    @patch("tkinter.messagebox.showerror")
    def test_puste_pola(self, mock_showerror):
        self.instance.pola_danych["imię"].get.return_value = ""
        self.instance.ustaw_dane(self.instance, 1)
        mock_showerror.assert_called_once_with("Błąd danych", "Przynajmniej jedno z pól jest niewypełnione")
        self.assertFalse(self.instance.sterowanie.zarejestruj_2.called)

    @patch("tkinter.messagebox.showerror")
    def test_nieprawidlowy_format_daty(self, mock_showerror):
        self.instance.pola_danych["data urodzenia"].get_date.return_value = "invalid_date"
        self.instance.ustaw_dane(self.instance, 1)
        mock_showerror.assert_called_once_with("Błąd danych", "Nieprawidłowy format daty! Oczekiwany format: MM/DD/YY.")
        self.assertFalse(self.instance.sterowanie.zarejestruj_2.called)

    def test_poprawne_dane(self):
        self.instance.ustaw_dane(self.instance, 1)
        expected_data = [
            "Jan", "Kowalski", "Mężczyzna", "1995-03-15",
            "jan.kowalski@example.com", "12345678901", "password123"
        ]
        self.assertEqual(self.instance.sterowanie.dane, expected_data)
        self.instance.sterowanie.zarejestruj_2.assert_called_once()
        self.assertEqual(self.instance.wynik.set.call_count, 1)
        self.instance.okno.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
