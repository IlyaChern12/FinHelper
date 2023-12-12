from flask import Flask, render_template, url_for, session, redirect, request, flash, g, send_from_directory, jsonify, request, render_template
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm, NoteIn
from NotesDatabase import NotesDatabase

###############################################################################################################################################

## конфигурация бд ##################################################################
DATABASE = '/tmp/flsite.db' 
DEBUG = True                                                                        # значение для дебага !!! изменить на false при публикации
SECRET_KEY = 'sdkldlkajdjajo&**$@)JWjfskfs;lslsdl;;lsdk'
USERNAME = 'admin'
PASSWORD = '123'
#####################################################################################


app = Flask(__name__)                                                               # инициализация веб-приложения
app.config.from_object(__name__)                                                    # загрузка конфигурации бд

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'fl_site.db')))         # изменение пути к бд

login_manager = LoginManager(app)                                                   # иницализация менеджера авторизации
login_manager.login_view = 'login'                                                              
login_manager.login_message = "Авторизуйтесь для доступа к странице"                # сообщение об успешной авторизации
login_manager.login_message_category = "success"                                    # категория селектора для передачи flash-сообщения в css


## вспомогательные функции для работы с бд ##########################################
@login_manager.user_loader                                                          
def load_user(user_id):
    db = get_db()                                                                   # получение данных из бд
    dbase = FDataBase(db)                                                           # переключение на класс FDataBase
    return UserLogin().fromDB(user_id, dbase)                                       # возврат user после поиска по его id в бд

### установление соединения с бд
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])                                  # подключение к бд пользователей
    conn.row_factory = sqlite3.Row                                                  # записи из бд в виде словаря
    return conn

### создание бд
def create_db():
    db = connect_db()                                                               # установление соединения
    with app.open_resource('sq_db.sql', mode='r') as f:                             # открытие файла со sql скриптами для выполнения
        db.cursor().executescript(f.read())                                         # выполнение скриптов
    db.commit()                                                                     # добавление изменений в бд
    db.close()                                                                      # закрытие бд

### запрос в бд
def get_db():
    if not hasattr(g, 'link_db'):                                                   # проверка наличия атрибута соединения у объекта g
        g.link_db = connect_db()                                                    # добавление бд пользователей к контексту
    return g.link_db

### закрытие бд
@app.teardown_appcontext                                                            # декоратор для сброса контекста (g - объект и проч.) после выполнения
def close_db(error):                                                                # проверка наличия атрибута соединения у объекта g
    if hasattr(g, 'link_db'):                                                       # закрытие бд 
        g.link_db.close()

##################################################################################### 



#   Обработчики ссылок и действий   #################################################

### Авторизация
@app.route("/login", methods=["POST", "GET"])                                       # декоратор для указания на обработчик действия по ссылке /login с get и post методами обмена данных
def login():
    if current_user.is_authenticated:                                               # проверка авторизации пользователя
        return redirect(url_for('main'))                                            # авторизованные пользователи перенаправляются на главную страницу

    db = get_db()                                                                   # подключение к бд
    dbase = FDataBase(db)   

    form = LoginForm()                                                              # подключение формы авторизации из forms
    if form.validate_on_submit():                                                   # нажатие на кнопку "войти"
        user = dbase.getUserByUsername(form.username.data)                          # получение данных user из бд
        if user and check_password_hash(user['passwd'], form.passwd.data):          # если user получен и хеш его пароля совпадает с хэшем введенных символов
            userlogin = UserLogin().create(user)                                    # записываем юзера в залогиненные
            rm = form.remainme.data                                                 # "запомнить меня"
            login_user(userlogin, remember = rm)                                    # авторизуем юзера с запоминанием
            resp = redirect(url_for('main'))                                        # записываем перенаправление в resp
            resp.set_cookie('username', form.username.data, max_age = 24 * 60 * 60) # сохраняем юзернейм в куки на 1 день для главной страницы
            return resp                                                             # перенаправляем на главную
    
        flash("Неверные данные", category="error")                                  # вывод флеша о неверных данных с css-стилем "error"

    return render_template("login.html", form=form)                                 # отображение соответствующей страницы с формой авторизации 

### Регистрация
@app.route('/register', methods = ['POST', 'GET'])
def register():
    db = get_db()
    dbase = FDataBase(db)

    form = RegisterForm()                                                           # подключение формы регистрации из forms
    if form.validate_on_submit():
            hash = generate_password_hash(form.passwd.data)                         # хэширование введенного пароля
            res = dbase.addUser(form.username.data, form.uname.data,                # добавление юзера в бд
                                form.surname.data, hash)
            if res:                                                                 # если успешно добавлен
                flash("Вы успешно зарегистрированы", "success")                         
                user = dbase.getUserByUsername(request.form['username'])            # получаем данные юзера и авторизуем его
                userlogin = UserLogin().create(user)                                #
                login_user(userlogin)                                               #
                resp = redirect(url_for('main'))
                resp.set_cookie('username', form.username.data, max_age = 24 * 60 * 60)
                return resp
            else:
                flash("Пользователь с таким логином уже есть", category="error")    
                # !!! одинаковые логины невозможны т.к. поиск в бд записей по логину

    return render_template("register.html", form=form)

### Главная страница
@app.route('/', methods = ['POST', 'GET'])                 
@login_required                                                                     # декоратор для доступа только авторизованных пользователей
def main():
    db = get_db()                                                                   # подключение бд записей
    dbase = NotesDatabase(db)

    form = NoteIn()                                                                 # подключение формы добавления записи

    u_name = request.cookies.get('username')                                        # юзернейм вошедшего извлекаем из куков
    
    if not(u_name):                                                                 # если куки истекли или их нет сбрасываем на выход
        return redirect(url_for('logout'))

    cur = db.cursor()                                                               
    cur.execute(f"SELECT id, product, category, buydate, cost FROM notes WHERE username LIKE '{u_name}'")
    # выбор подходящих записей
    notes = cur.fetchall()                                                          # вывод всех подходящих записей


    return render_template('main.html', notes = notes, form = form)                 # вывод страницы с записями и формой

### Добавление записей
@app.route('/add_in', methods=['POST'])
def add_in():
    db = get_db()
    dbase = NotesDatabase(db)

    form = NoteIn()
    if form.validate_on_submit():                                                   
            res = dbase.addNote(form.product.data, form.category.data,              # внесение записи в бд с указанием юзернейма
                                form.buydate.data, form.cost.data, 
                                session['username'])
            if res:                                                                 
                flash("Запись добавлена", category="success")
                return redirect(url_for('main'))
            else:
                flash("Что-то пошло не так", category="error")
    else:
        flash("Введите цену числом", category="error")
        
    return redirect(url_for('main'))
            
### Удаление записей
@app.route('/delete_notes', methods=['POST'])
def delete_notes():
    db = get_db()
    dbase = NotesDatabase(db)
    ids = request.json['ids']                                                       # получение списка удаляемых записей
    if ids:
        if ',' in ids:                                                              # список
            ids = ids.split(',')
            resp = dbase.del_notes(ids)                                             # удаление элементов по списку
        else:
            resp = dbase.del_notes([ids])                                           # удаление одной переменной
		
        if resp:
            resp = jsonify("<div class='good_add'>Записи успешно удалены</div>")    # сообщение об успехе выполнения
            resp.status_code = 200
            return resp
        else:
            resp = jsonify("<div class='bad_add'>Что-то пошло не так</div>")
            resp.status_code = 500
            return resp
    else:
        resp = jsonify("<div class='bad_add'>Неверный формат ввода</div>")
        resp.status_code = 400
        return resp

### Выход
@app.route('/logout')
def logout():
    resp = redirect(url_for('main'))
    resp.delete_cookie('username')                                                  # удаление куков
    logout_user()                                                                   # выход юзера
    flash('Вы вышли из аккаунта', category="success")
    return redirect(url_for('login'))                                               # пересылка на аутентификацию

if __name__ == "__main__":                                                          
    app.run(debug = True)                                                           # запуск приложения !!! изменить значение дебага на false