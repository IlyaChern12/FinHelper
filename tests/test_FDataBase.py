import unittest
from FDataBase import FDataBase
from unittest import mock

# fake бд данных пользователей
class FakeFDB:
    def __init__(self):
        self.users = []

    def cursor(self):
        return self

    def execute(self, sql, params=None):
        if "SELECT COUNT" in sql:
            uname = sql.split("LIKE '")[1].split("'")[0]
            self._count = sum(1 for u in self.users if u[2] == uname)
            self._mode = "count"
        elif "SELECT * FROM users WHERE id" in sql:
            u_id = int(sql.split("WHERE id = ")[1].split()[0])
            for u in self.users:
                if u[0] == u_id:
                    self._fetched = u
                    break
            else:
                self._fetched = None
            self._mode = "get"
        elif "INSERT INTO users" in sql:
            self.users.append(params)

    def fetchone(self):
        if getattr(self, "_mode", None) == "count":
            return {"count": getattr(self, "_count", 0)}
        elif getattr(self, "_mode", None) == "get":
            return getattr(self, "_fetched", None)
        return None

    # stub - чтобы база не упала
    def commit(self):
        pass

# тестирование операций с записями о пользователях
class TestFDataBase(unittest.TestCase):
    # добавление
    def test_addUser(self):
        # arrange
        db = FakeFDB()
        fdb = FDataBase(db)
        cases = [
            {"username": "user1", "name": "Иван", "surname": "Иванов", "pswd": "hash1", "exp": True},
            {"username": "user1", "name": "Иван", "surname": "Иванов", "pswd": "hash1", "exp": False},
            {"username": "user2", "name": "Анна", "surname": "Петрова", "pswd": "hash2", "exp": True} ]

        for case in cases:
            with self.subTest(username=case["username"]):

                # act
                got = fdb.addUser(case["username"], case["name"], case["surname"], case["pswd"])

                # assert
                self.assertEqual(got, case["exp"])
                if got:
                    self.assertIn((case["name"], case["surname"], case["username"], case["pswd"], mock.ANY), db.users)

    # запрос не существующего юзера
    def test_getUser_not_found(self):
        # arrange
        db = FakeFDB()
        fdb = FDataBase(db)

        # act
        got = fdb.getUser(999)

         # assert
        self.assertFalse(got)

if __name__ == "__main__":
    unittest.main()