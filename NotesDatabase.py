import sqlite3
import math
from datetime import datetime
import re
from flask import url_for

class NotesDatabase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addNote(self, product, category, buydate, cost, username):
            try:
                self.__cur.execute("INSERT INTO notes VALUES(NULL, ?, ?, ?, ?, ?)", (product, category, buydate, cost, username))
                self.__db.commit()
            except sqlite3.Error as e:
                print("Ошибка добавления записи в БД "+str(e))
                return False
    
            return True
			
    def del_notes(self, ids):
        try:
            self.__cur.execute("DELETE FROM notes WHERE id IN (" + ", ".join(ids) + ")")
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка удаления записи из БД "+str(e))
            return False
        
        return True