from data import db_session
from data.users_table import User


def get_names(str_list_of_ids):
    list_of_names = []
    db_sess = db_session.create_session()
    for i in str_list_of_ids.split(', '):
        user = db_sess.query(User).filter(User.id == int(i)).first()
        list_of_names.append(''.join([user.user_name, '(', user.phone_number, ')']))
    return list_of_names