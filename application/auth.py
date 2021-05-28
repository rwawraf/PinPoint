from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from copy import copy
from datetime import timedelta

from .DataCache import DataCache
from .models import db, User, user_datastore, Role

# tutaj sa tworzone Routes - czyli podstrony na ktore serwer ma kierowac zapytanie
auth = Blueprint('auth', __name__)

online_users = DataCache(timedelta(minutes=1))


# przed zapytaniem ustaw zmienna globalna przypisana do uzytkownika
# dodaj go do tej listy globalnej, jakos ze jest zalogowany
@auth.before_request
def mark_online():
    global online_users
    if not online_users.get(current_user.get_id(), "") and current_user.get_id():
        online_users[current_user.get_id()] = copy(current_user)


# przekazanie bezposrednio do szablonu strony jinja zmiennej online_users
# za pomoca dekoratora context_processor
@auth.context_processor
def currently_online_users():
    return dict(online_users=online_users)


@auth.route('/online-users')
def online_users_list():
    return render_template("chat/online.html", user=current_user)


# zdefiniowanie trzech nowych ścieżek/podstron dla logowania
# poprzez methods dajemy znac ktore zapytania sa przez ta podstrone akceptowane
# domyslnie jest get, jesli nie wpisalibysmy post nie wpusciloby
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logowanie przebiegło pomyślnie.', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Niepoprawne hasło lub konto pod danym adresem email nie istnieje. (haslo)', category='error')
        else:
            flash('Niepoprawne hasło lub konto pod danym adresem email nie istnieje. (email)', category='error')

    return render_template("auth/login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # obsluga poszczegolnych metod, musimy rozdzielic get'a od post'a
    # obsluga formularza rejestracyjnego
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # warunki zabezpieczajace pola
        # message-flashing using flask
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Użytkownik o podanym adresie email już istnieje.', category='error')
        elif len(email) < 6:
            flash('Adres email musi być dłuższy niż 5 znaków.', category='error')
        elif len(username) < 4:
            flash('Nazwa użytkownika musi być dłuższa niż 3 znaki.', category='error')
        elif password1 != password2:
            flash('Hasła nie są zgodne.', category='error')
        elif len(password1) < 7:
            flash('Hasło musi być dłuższe niż 6 znaków.', category='error')
        else:
            # new_user = User(email=email,
            #                 username=username,
            #                 password=generate_password_hash(password1, method='sha256'))
            # db.session.add(new_user)
            # db.session.commit()

            # nie uzywam juz normalnego usera, tylko user_datastore
            # dodaje poprawnie tych uzytkownikow, bo zostalo zainicjowane w models.py
            new_user = user_datastore.create_user(email=email,
                                                  username=username,
                                                  password=generate_password_hash(password1, method='sha256'),
                                                  image_path='/static/images/default.jpg'
                                                  )
            db.session.add(new_user)

            user_role = Role.query.filter_by(name='user').first()
            user_datastore.add_role_to_user(new_user, user_role)

            db.session.commit()

            login_user(new_user, remember=True)

            flash('Konto zostało utworzone!', category='success')

            # po dodaniu uzytkownika przekieruj na homepage
            return redirect(url_for('views.home'))

    return render_template("auth/sign_up.html", user=current_user)
