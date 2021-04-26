from flask import Flask, render_template, redirect, session, make_response, request, abort, jsonify
from data.messages_table import Messages
from forms.message import AddmessForm
from gettings import get_names, get_ids, get_email_from_frineds, get_messages, get_ids_from_emails, get_chat_names
from data.chats_table import Chats
from data.users_table import User
from forms.chats import ChatsForm, ChatsUsersForm
from forms.user import RegisterForm, LoginForm, UpdateForm, AddingForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'smartchat_project_secret_key'
CURRENT_CHAT = None
CREATING_CHAT_USERS = None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def wellcome():
    if current_user.is_authenticated:
        chats = current_user.chats
        if chats:
            if ', ' in chats:
                chats = chats.split(', ')
            elif chats:
                chats = [chats]
            return render_template("chats.html", title='Твои чаты', chats=get_chat_names(chats))
        return render_template("chats.html", title='Твои чаты')
    else:
        return render_template("wellcome.html", title='Главная страница')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first() and\
                db_sess.query(User).filter(User.phone_number == form.phone_num.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой юзер уже есть")
        user = User(
            user_name=form.name.data,
            email=form.email.data,
            phone_number=form.phone_num.data,
            about_user=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.user_name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильное имя или пароль",form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addchat',  methods=['GET', 'POST'])
@login_required
def add_chat():
    global CURRENT_CHAT
    global CREATING_CHAT_USERS
    form = ChatsForm()
    if form.validate_on_submit():
        if len(CREATING_CHAT_USERS) > 1:
            users = ', '.join(CREATING_CHAT_USERS)
        else:
            users = CREATING_CHAT_USERS[0]
        db_sess = db_session.create_session()
        chat = Chats(
            chat_name=form.name.data,
            about_chat=form.about.data,
            admin=current_user.id,
            users=users
        )
        db_sess.add(chat)
        db_sess.commit()
        for id in CREATING_CHAT_USERS:
            u = db_sess.query(User).filter(User.id == id).first()
            if u.chats:
                u.chats = ', '.join([u.chats, str(chat.id)])
            else:
                u.chats = str(chat.id)
            db_sess.merge(u)
        db_sess.commit()
        CURRENT_CHAT = chat
        CREATING_CHAT_USERS = None
        return redirect(f'/chat/{CURRENT_CHAT.id}')
    return render_template('addchat.html', title='Создание чата', form=form)


@app.route('/choose_users', methods=['GET', 'POST'])
def choose_users():
    global CREATING_CHAT_USERS
    CREATING_CHAT_USERS = None
    form = ChatsUsersForm()
    if form.validate_on_submit():
        if current_user.friends:
            for email in form.email_friends.data.split(', '):
                if email not in get_email_from_frineds(current_user.friends):
                    mes = f"Пользователя с почтой {email} у вас нет в контактах. Отредактируйте или уберите почту."
                    return render_template('choose_users.html', title='Добавление участников', form=form, message=mes)
            CREATING_CHAT_USERS = get_ids_from_emails(form.email_friends.data)
            CREATING_CHAT_USERS.append(str(current_user.id))
            return redirect('/addchat')
        mes = f"Пользователя/ей с почтой/ами {form.email_friends.data} у вас нет в контактах."
        return render_template('choose_users.html', title='Добавление участников', form=form, message=mes)
    return render_template('choose_users.html', title='Добавление участников', form=form)


@app.route('/person_info/<int:id>', methods=['GET', 'POST'])
@login_required
def person_info(id):
    form = UpdateForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user and user == current_user:
            form.name.data = user.user_name
            form.email.data = user.email
            form.phone_num.data = user.phone_number
            form.about.data = user.about_user
            if user.friends:
                form.contacts.data = '\n'.join(get_names(user.friends))
            else:
                form.contacts.data = None
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user and user == current_user:
            user.user_name = form.name.data
            user.email = form.email.data
            user.phone_number = form.phone_num.data
            user.about_user = form.about.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('person_info.html', title='Информация', form=form)


@app.route('/add_user',  methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddingForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data,
                                          User.phone_number == form.phone_num.data).first()
        if user:
            if user == current_user:
                message = 'Мы понимаем, что вы себя любите, но не добавлять же себе свой же контакт!'
                return render_template('adduser.html', title='Добавить контакт', form=form, message=message,
                                       id=current_user.id)
            elif current_user.friends:
                if str(user.id) in current_user.friends.split(', '):
                    message = 'У вас уже есть такой контакт'
                    return render_template('adduser.html', title='Добавить контакт', form=form, message=message,
                                           id=current_user.id)
                current_user.friends = ', '.join([current_user.friends, str(user.id)])
            else:
                current_user.friends = str(user.id)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect(f"/person_info/{current_user.id}")
        message = 'Такого пользователя не существует'
        return render_template('adduser.html', title='Добавить контакт', form=form, message=message, id=current_user.id)
    return render_template('adduser.html', title='Добавить контакт', form=form, id=current_user.id)


@app.route('/chat/<int:id>', methods=['GET', 'POST'])
def chat(id):
    global CURRENT_CHAT
    db_sess = db_session.create_session()
    ch = db_sess.query(Chats).filter(Chats.id == id).first()
    ch_name = ch.chat_name
    messages = get_messages(ch.id)
    CURRENT_CHAT = ch
    return render_template('user_s_chat.html', title='Чат', ch_name=ch_name, messages=messages, cur_id=current_user.id)


@app.route('/writing_message', methods=['GET', 'POST'])
def writing_message():
    global CURRENT_CHAT
    form = AddmessForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        message = Messages(
            text=form.about.data,
            user_id=current_user.id,
            chat_id=CURRENT_CHAT.id)
        db_sess.add(message)
        db_sess.commit()
        return redirect(f"/chat/{CURRENT_CHAT.id}")
    return render_template('writing_message.html', ch_id=CURRENT_CHAT.id, form=form)


@app.route('/message_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def message_delete(id):
    global CURRENT_CHAT
    db_sess = db_session.create_session()
    mes = db_sess.query(Messages).filter(Messages.id == id, Messages.user_id == current_user.id).first()
    if mes:
        db_sess.delete(mes)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/chat/{CURRENT_CHAT.id}')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()

