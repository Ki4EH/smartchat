import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats_table'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    admin = sqlalchemy.Column(sqlalchemy.Integer)
    users = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chat_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about_chat = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chat_created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
