import unittest


class TestAktualizujWizyte(unittest.TestCase):
    def setUp(self):
        class MockDatabase:
            def __init__(self):
                self.executed_queries = []
                self.committed = False

            def execute_query(self, query, params):
                if None in params:
                    raise ValueError("Brakuje danych.")
                if not all(isinstance(param, str) for param in params[:3]) or not isinstance(params[3], int):
                    raise ValueError("Błędne dane wejściowe.")
                self.executed_queries.append((query, params))

            def get_connection(self):
                class MockConnection:
                    def commit(self_conn):
                        self.committed = True

                return MockConnection()

        class TestClass:
            def __init__(self, database):
                self.database = database

            def aktualizuj_wizyte(self, id_wizyty, dzien, godz_rozp, godz_zak):
                query = """
                    UPDATE WIZYTA
                    SET godzina_rozpoczecia = %s, godzina_zakonczenia = %s, dzien = %s
                    WHERE id = %s
                """
                try:
                    self.database.execute_query(query, (godz_rozp, godz_zak, dzien, id_wizyty))
                    self.database.get_connection().commit()
                except Exception as e:
                    print(f"Error occurred: {e}")
                    raise e

        self.MockDatabase = MockDatabase
        self.TestClass = TestClass

    def test_aktualizuj_wizyte_poprawne_dane(self):
        db = self.MockDatabase()
        test_obj = self.TestClass(db)
        test_obj.aktualizuj_wizyte(1, '2023-10-01', '09:00', '10:00')
        self.assertTrue(db.committed)
        self.assertEqual(len(db.executed_queries), 1)

    def test_aktualizuj_wizyte_bledne_dane(self):
        db = self.MockDatabase()
        test_obj = self.TestClass(db)
        with self.assertRaises(ValueError) as context:
            test_obj.aktualizuj_wizyte(1, 20231001, '09:00', '10:00')
        self.assertEqual(str(context.exception), "Błędne dane wejściowe.")

    def test_aktualizuj_wizyte_brak_danych(self):
        db = self.MockDatabase()
        test_obj = self.TestClass(db)
        with self.assertRaises(ValueError) as context:
            test_obj.aktualizuj_wizyte(None, '2023-10-01', None, '10:00')
        self.assertEqual(str(context.exception), "Brakuje danych.")


if __name__ == '__main__':
    unittest.main()
