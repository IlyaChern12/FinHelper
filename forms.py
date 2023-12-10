from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, DateField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Логин: ', validators = [DataRequired(), Length(min = 3)], render_kw={"placeholder": "Введите логин"}) # длина логина от 3 до 33
    passwd = PasswordField('Пароль: ', validators = [DataRequired(), Length(min = 6)], render_kw={"placeholder": "Введите пароль"})
    remainme = BooleanField('Запомнить меня', default = False)
    submit = SubmitField('Войти') 

class RegisterForm(FlaskForm):
    uname = StringField('Имя: ', validators = [DataRequired()], render_kw={"placeholder": "Введите имя"}) # длина логина от 3 до 33
    surname = StringField('Фамилия: ', validators = [DataRequired()], render_kw={"placeholder": "Введите фамилию"})
    username = StringField('Логин: ', validators = [DataRequired(), Length(min = 3)], render_kw={"placeholder": "Введите логин (не менее 3 символов)"})
    passwd = StringField('Пароль: ', validators = [DataRequired(), Length(min = 6)], render_kw={"placeholder": "Введите пароль (не менее 6 символов)"})
    passwd2 = StringField('Повторите пароль: ', validators = [DataRequired(), Length(min = 6), EqualTo('passwd', message='Пароли не совпадают')], render_kw={"placeholder": "Повторите пароль"})
    submit = SubmitField('Зарегистрироваться') 

class NoteIn(FlaskForm):
    product = StringField(validators = [DataRequired(), Length(min = 1, max = 21)], render_kw={"placeholder": "Название"})
    category = StringField(validators = [DataRequired(), Length(min = 1, max = 21)], render_kw={"placeholder": "Категория"})
    buydate = DateField(default=date.today, render_kw={"placeholder": "Дата"})
    cost = FloatField(validators = [DataRequired()], render_kw={"placeholder": "Стоимость (до 10 млн)"})
    submit = SubmitField('  Добавить покупку  ') 