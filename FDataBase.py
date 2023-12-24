import sqlite3
import math
import time
import re
from flask import url_for

####################################################################

# Объект базы данных пользователей
class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    ### Добавление юзера
    def addUser(self, username, name, surname, hpsw):
            try:
                # проверка, что юзер с таким логином отсутствует
                self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE username LIKE '{username}'")
                res = self.__cur.fetchone()
                if res['count'] > 0:
                    print("Пользователь с таким логином уже существует")
                    return False

                tm = math.floor(time.time()) # время авторизации
                self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?, ?)", (name, surname, username, hpsw, tm))
                self.__db.commit()
                # добавление юзера в бд

            except sqlite3.Error as e:
                print("Ошибка добавления пользователя в БД "+str(e))
                return False
    
            return True
    
    ### Получение данных юзера по id в бд
    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            # извлечение записи
            if not res:
                print("Пользователь не найден")
                return False 
 
            return res
        
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))
 
        return False
    
    ### Получение данных юзера по юзернейму
    def getUserByUsername(self, username):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE username LIKE '{username}' LIMIT 1")
            res = self.__cur.fetchone()
            # извлечение записи
            if not res:
                print("Пользователь не найден")
                return False 
 
            return res
        
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))
 
        return False
    