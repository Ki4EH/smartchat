from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ChatsForm(FlaskForm):
    name = StringField('Тема чата', validators=[DataRequired()])
    persons = StringField('Участники', validators=[DataRequired()])
    about = TextAreaField("Описание")
    submit = SubmitField('Создать')


class ChatsUsersForm(FlaskForm):
    submit = SubmitField('Применить')
    email_friends = StringField('Впишите сюда почты контактов, который будут в чате, через запятую с пробелом',
                                validators=[DataRequired()])