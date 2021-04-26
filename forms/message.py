from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class AddmessForm(FlaskForm):
    about = TextAreaField("Написать сообщение")
    submit = SubmitField('Отправить')