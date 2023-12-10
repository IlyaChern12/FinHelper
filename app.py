from flask import Flask, render_template, url_for, session, redirect, request, flash, g, send_from_directory, jsonify, request, render_template
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm, NoteIn
from NotesDatabase import NotesDatabase

###################################################################################################################################################################################################

# конфигурация бд
DATABASE = '/tmp/flsite.db' 
DEBUG = True
SECRET_KEY = 'sdkldlkajdjajo&**$@)JWjfskfs;lslsdl;;lsdk'
USERNAME = 'admin'
PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)                                            # загрузка конфигурации бд

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'fl_site.db'))) # изменение пути к бд

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к странице"
login_manager.login_message_category = "success"

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    dbase = FDataBase(db)
    return UserLogin().fromDB(user_id, dbase)

# установление соединения с бд
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row                  # записи из бд в виде словаря
    return conn

# создание бд
def create_db():
    db = connect_db()   # установление соединения
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read()) # выполнение скриптов
    db.commit()    # добавление изменений в бд
    db.close()     # закрытие бд

# запрос в бд
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()
###################################  



#   Форма авторизации    ##########################################################################################
@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))

    db = get_db()
    dbase = FDataBase(db)

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByUsername(form.username.data)
        if user and check_password_hash(user['passwd'], form.passwd.data):
            userlogin = UserLogin().create(user)
            session['username'] = form.username.data
            rm = form.remainme.data
            login_user(userlogin, remember = rm)
            return redirect(url_for('main'))
    
        flash("Неверные данные", category="error") 

    return render_template("login.html", form=form)

@app.route('/add_in', methods=['POST'])
def add_in():
    db = get_db()
    dbase = NotesDatabase(db)

    form = NoteIn()
    if form.validate_on_submit():
            res = dbase.addNote(form.product.data, form.category.data, form.buydate.data, form.cost.data, session['username'])
            if res:
                flash("Запись добавлена", category="success")
                return redirect(url_for('main'))
            else:
                flash("Что-то пошло не так", category="error")
    else:
        flash("Введите цену числом", category="error")
        
    return redirect(url_for('main'))
            

@app.route('/delete_notes', methods=['POST'])
def delete_notes():
    db = get_db()
    dbase = NotesDatabase(db)
    ids = request.json['ids']
    if ids:
        if ',' in ids:
            ids = ids.split(',')
            resp = dbase.del_notes(ids)
        else:
            resp = dbase.del_notes([ids])
		
        if resp:
            resp = jsonify("<div class='good_add'>Записи успешно удалены</div>")
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


@app.route('/', methods = ['POST', 'GET'])
@login_required
def main():
    db = get_db()
    dbase = NotesDatabase(db)

    form = NoteIn()

    u_name = session['username'] 

    cur = db.cursor()
    cur.execute(f"SELECT id, product, category, buydate, cost FROM notes WHERE username LIKE '{u_name}'")
    notes = cur.fetchall()

    return render_template('main.html', notes = notes, form = form)


@app.route('/register', methods = ['POST', 'GET'])
def register():
    db = get_db()
    dbase = FDataBase(db)

    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(form.passwd.data)
            res = dbase.addUser(form.username.data, form.uname.data, form.surname.data, hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                user = dbase.getUserByUsername(request.form['username'])
                userlogin = UserLogin().create(user)
                session['username'] = form.username.data
                login_user(userlogin)
                return redirect(url_for('main'))
            else:
                flash("Пользователь с таким логином уже есть", category="error")

    return render_template("register.html", form=form)



@app.route('/logout')
def logout():
    session['username'] = ""
    logout_user()
    flash('Вы вышли из аккаунта', category="success") # через запятую можно указать специальный селектор для успеха или неудачи!!!
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug = True)