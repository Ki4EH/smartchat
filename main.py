import datetime
from flask import Flask, render_template, redirect, session, make_response, request, abort, jsonify
from flask_restful import Api
from get_friends import get_names, get_ids
from data.chats_table import Chats
from data.users_table import User
from forms.chats import ChatsForm, ChatsUsersForm
from forms.user import RegisterForm, LoginForm, UpdateForm, AddingForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session  #, news_api, news_resources


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'smartchat_project_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def wellcome():
    if current_user.is_authenticated:
        chats = current_user.chats
        if chats:
            chats.split(', ')
        return render_template("chats.html", title='Твои чаты', chats=chats)
    else:
        return render_template("wellcome.html", title='Главная страница')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first() or\
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
    form = ChatsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        chats = Chats()
        chats.chat_name = form.name.data
        chats.about_chat = form.about.data
        chats.users = ChatsUsersForm().persons.data

        chats.collaborators = form.collaborators.data
        chats.is_finished = form.is_finished.data
        current_user.jobs.append(chats)

        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('addchat.html', title='Создание чата', form=form)


@app.route('/choose_users', methods=['GET', 'POST'])
def choose_users():
    persons = current_user.friends
    if persons:
        persons = get_names(persons)
    form = ChatsUsersForm()
    if form.validate_on_submit():
        bar = request.form.getlist('pers')
        print('nigga')
        print(bar)
        for pers in persons:
            print(pers)
            bar = request.form.getlist(pers)
            print(bar)
    return render_template('choose_users.html', title='Добавление участников', persons=persons, form=form)


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
                print(form.contacts)
                form.contacts.data = '\n'.join(get_names(user.friends))
            else:
                form.contacts.data = None
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user and user == current_user:
            print(form.name.data)
            user.user_name = form.name.data,
            user.email = form.email.data,
            user.phone_number = form.phone_num.data,
            user.about_user = form.about.data
            if form.contacts.data:
                user.friends = get_ids(form.contacts.data)
            else:
                user.friends = None
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
                return render_template('adduser.html', title='Добавить контакт', form=form, message=message)
            elif current_user.friends:
                if str(user.id) in current_user.friends.split(', '):
                    message = 'У вас уже есть такой контакт'
                    return render_template('adduser.html', title='Добавить контакт', form=form, message=message)
                current_user.friends = ', '.join([current_user.friends, str(user.id)])
            else:
                current_user.friends = str(user.id)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect(f"/person_info/{current_user.id}")
        message = 'Такого пользователя не существует'
        return render_template('adduser.html', title='Добавить контакт', form=form, message=message)
    return render_template('adduser.html', title='Добавить контакт', form=form)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()

