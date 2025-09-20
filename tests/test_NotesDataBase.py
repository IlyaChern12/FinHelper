import unittest
from NotesDatabase import NotesDatabase

# fake бд записей о покупках
class FakeNotesDB:
    def __init__(self):
        self.notes = []

    def cursor(self):
        return self

    def execute(self, sql, params=None):
        if "INSERT" in sql:
            self.notes.append(params)
        elif "DELETE" in sql:
            self.notes.clear()

    # stub - чтоб база не упала
    def commit(self):
        pass

# тестирование работы с записями
class TestNotesDatabase(unittest.TestCase):
    # создание записей
    def test_addNote(self):
        # arrange
        db = FakeNotesDB()
        ndb = NotesDatabase(db)
        cases = [
            {"product": "Молоко", "category": "Еда", "buydate": "2005-10-15", "cost": 300, "username": "user", "exp": True},
            {"product": "", "category": "Еда", "buydate": "2025-09-09", "cost": 500, "username": "user", "exp": True},
            {"product": "фаафыфа", "category": "", "buydate": "2025-08-21", "cost": 200, "username": "user", "exp": True} ]

        for case in cases:
            with self.subTest(product=case["product"]):

                # act
                got = ndb.addNote(case["product"], case["category"], case["buydate"], case["cost"], case["username"])

                # assert
                self.assertEqual(got, case["exp"])
                if got:
                    self.assertIn((case["product"], case["category"], case["buydate"], case["cost"], case["username"]), db.notes)

    # удаление записей
    def test_del_notes(self):
         # arrange
        db = FakeNotesDB()
        ndb = NotesDatabase(db)
        db.notes.append(("Milk", "Food", "2025-09-20", 100, "user"))
        cases = [
            {"ids": ["1"], "exp": True},
            {"ids": [], "exp": True} ]

        for case in cases:
            with self.subTest(ids=case["ids"]):
     
                #  аct
                got = ndb.del_notes(case["ids"])

                # аssert
                self.assertEqual(got, case["exp"])
                self.assertEqual(len(db.notes), 0)


if __name__ == "__main__":
    unittest.main()