import unittest


class MyTestCase(unittest.TestCase):
    def test_logowanie_poprawne_dane_pacjenta(self):
        mock_controller = self.przygotuj_mock_controller()
        mock_controller.obecnyWidok = self.przygotuj_widok_poprawny()
        mock_controller.zaloguj()
        self.assertIsNotNone(mock_controller.obslugaUzytkownika)
        self.assertEqual(mock_controller.obslugaUzytkownika.pacjent, {"id": 1, "imie": "Jan", "nazwisko": "Kowalski"})

    def test_logowanie_bledne_dane(self):
        mock_controller = self.przygotuj_mock_controller()
        mock_controller.obecnyWidok = self.MockWidokBledny()
        mock_controller.zaloguj()
        self.assertIsNone(mock_controller.obslugaUzytkownika)
        self.assertEqual(mock_controller.bladKomunikat, "Niepoprawne dane logowania!")

    def test_logowanie_bledny_typ_uzytkownika(self):
        mock_controller = self.przygotuj_mock_controller()
        mock_controller.obecnyWidok = self.MockWidokZlyTyp()
        mock_controller.zaloguj()
        self.assertIsNone(mock_controller.obslugaUzytkownika)
        self.assertEqual(mock_controller.bladKomunikat, "Niepoprawny typ użytkownika!")

    class MockWidokBledny:
        dane = ["zly_login", "zle_haslo", "pacjent"]

        def wyswietl_widok(self): pass

        def wyswietl_blad(self, komunikat): print(komunikat)

    class MockWidokZlyTyp:
        dane = ["login", "haslo", "nieistniejacy_typ"]

        def wyswietl_widok(self): pass

        def wyswietl_blad(self, komunikat): print(komunikat)

    def przygotuj_mock_controller(self):
        class MockFabrykaWidokow:
            def utworz_widok(self, controller, widok):
                if widok == "bledny":
                    class MockWidokBledny:
                        dane = ["zly_login", "zle_haslo", "pacjent"]

                        def wyswietl_widok(self): pass

                        def wyswietl_blad(self, komunikat): print(komunikat)

                    return MockWidokBledny()
                else:
                    class MockWidok:
                        dane = ["login", "haslo", "pacjent"]

                        def wyswietl_widok(self): pass

                        def wyswietl_blad(self, komunikat): print(komunikat)

                    return MockWidok()

        class MockFabrykaModelu:
            def utworz_model(self):
                class MockPobieranieDanych:
                    def weryfikacja_uzytkownika(self, login, haslo, typ):
                        if login == "login" and haslo == "haslo" and typ == "pacjent":
                            return 1
                        return -1

                    def pobierz_pacjenta(self, id_uzytkownika):
                        return {"id": id_uzytkownika, "imie": "Jan", "nazwisko": "Kowalski"}

                return [MockPobieranieDanych(), object()]

        class MockObslugaPacjenta:
            def __init__(self, controller, pacjent):
                self.controller = controller
                self.pacjent = pacjent

            def panel_pacjenta(self): pass

        class MockController:
            def __init__(self):
                self.fabrykaWidokow = MockFabrykaWidokow()
                self.fabrykaModelu = MockFabrykaModelu()
                self.obecnyWidok = None
                self.pobieranieDanych = None
                self.aktualizacjaDanych = None
                self.obslugaUzytkownika = None
                self.bladKomunikat = None

            def zaloguj(self):
                self.obslugaUzytkownika = None
                if not hasattr(self.obecnyWidok, 'dane') or len(self.obecnyWidok.dane) != 3:
                    self.bladKomunikat = "Niepoprawne dane wejściowe!"
                    if self.obecnyWidok is not None:
                        self.obecnyWidok.wyswietl_blad(self.bladKomunikat)
                    return

                login, haslo, typ = self.obecnyWidok.dane
                [self.pobieranieDanych, self.aktualizacjaDanych] = self.fabrykaModelu.utworz_model()

                if typ != "pacjent":  # Typ użytkownika inny niż "pacjent"
                    self.bladKomunikat = "Niepoprawny typ użytkownika!"
                    self.obecnyWidok.wyswietl_blad(self.bladKomunikat)
                    return

                id_uzytkownika = self.pobieranieDanych.weryfikacja_uzytkownika(login, haslo, typ)

                if id_uzytkownika == -1:  # Błędne dane logowania
                    self.bladKomunikat = "Niepoprawne dane logowania!"
                    self.obecnyWidok.wyswietl_blad(self.bladKomunikat)
                else:
                    try:
                        pacjent = self.pobieranieDanych.pobierz_pacjenta(id_uzytkownika)
                        self.obslugaUzytkownika = MockObslugaPacjenta(self, pacjent)
                        self.obslugaUzytkownika.panel_pacjenta()
                    except Exception as e:
                        self.bladKomunikat = f"Błąd podczas logowania: {str(e)}"
                        self.obecnyWidok.wyswietl_blad(self.bladKomunikat)

        return MockController()

    def przygotuj_widok_poprawny(self):
        class MockWidokPoprawny:
            dane = ["login", "haslo", "pacjent"]

            def wyswietl_widok(self): pass

            def wyswietl_blad(self, komunikat): print(komunikat)

        return MockWidokPoprawny()


if __name__ == '__main__':
    unittest.main()
