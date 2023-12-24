from flask_login import UserMixin

### Объект авторизованного пользователя
class UserLogin(UserMixin):
    ### получение данных юзера
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self
 
    ### запись юзера как авторизованного
    def create(self, user):
        self.__user = user
        return self
 
    ### получение id юзера
    def get_id(self):
        return str(self.__user['id'])