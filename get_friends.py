from data import db_session
from data.users_table import User


def get_names(str_list_of_ids):
    list_of_names = []
    db_sess = db_session.create_session()
    for i in str_list_of_ids.split(', '):
        user = db_sess.query(User).filter(User.id == int(i)).first()
        list_of_names.append(''.join([user.user_name, '(', user.phone_number, ')']))
    return list_of_names


def get_ids(str_of_names):
    list_of_ids = []
    db_sess = db_session.create_session()
    for i in str_of_names.split('\n'):
        phone_num = i.split('(')[-1][:-1]
        user = db_sess.query(User).filter(User.phone_number == phone_num).first()
        list_of_ids.append(str(user.id))
    return list_of_ids