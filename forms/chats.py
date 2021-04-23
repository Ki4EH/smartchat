from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ChatsForm(FlaskForm):
    name = StringField('Тема чата', validators=[DataRequired()])
    persons = StringField('Участники', validators=[DataRequired()])
    about = TextAreaField("Описание")
    submit = SubmitField('Создать')