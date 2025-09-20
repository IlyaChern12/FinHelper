import unittest
from UserLogin import UserLogin

# фейковая бд userов
class FakeUserDB:
    def getUser(self, user_id):
        if user_id == 1:
                return {"id": 1, "username": "user"}
        return None

# тестирование системы авторизации
class TestUserLogin(unittest.TestCase):
    # создание пользователя и получение его id
    def test_create_get_id(self):
        # arrange
        cases = [
            {"user_data": {"id": 20, "username": "Ivan"}, "status": False, "exp_id": "20"},
            {"user_data": None, "status": True, "exp_id": None}
        ]

        for case in cases:
            with self.subTest(user_data=case["user_data"]):
                user = UserLogin()

                # act
                user.create(case["user_data"])

                # assert
                if case["status"]:
                    # некорректный юзер должен вызывать ошибку
                    with self.assertRaises(TypeError):
                        user.get_id()
                else:
                    self.assertEqual(user.get_id(), case["exp_id"])


    #перезапись данных пользователя
    def test_create_changing(self):
        # arrange
        user = UserLogin()
        user.create({"id": 1, "username": "first"})

        #act
        user.create({"id": 2, "username": "second"})

        # assert
        self.assertEqual(user.get_id(), "2")

    # получение данных существующего пользователя
    def test_fromDB(self):
        # arrange
        db = FakeUserDB()
        cases = [
            {"user_id": 1, "status": True, "exp_id": "1"},   
            {"user_id": 99, "status": False, "exp_id": None} ]

        for case in cases:
            with self.subTest(user_id=case["user_id"]):

                # act
                user = UserLogin().fromDB(case["user_id"], db)

                # assert
                if case["status"]:
                    self.assertEqual(user.get_id(), case["exp_id"])
                else:
                    with self.assertRaises(TypeError):
                        user.get_id()


if __name__ == "__main__":
    unittest.main()