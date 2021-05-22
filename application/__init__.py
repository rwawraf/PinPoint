from os import path, environ
from dotenv import load_dotenv
from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from werkzeug.security import generate_password_hash
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from .models import *

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../.env'))


# inicjalizacja flaska
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevConfig')
    # app.config.from_object('config.ProdConfig')

    db.init_app(app)

    # konfiguracja routes
    # dajemy znac programowi ze te moduly istnieja
    from .views import views
    from .auth import auth
    from .chat import chat
    from .notes import notes
    from .models import User
    from .users import users
    from .friends import friends

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(chat, url_prefix='/')
    app.register_blueprint(notes, url_prefix='/')
    app.register_blueprint(users, url_prefix='/')
    app.register_blueprint(friends, url_prefix='/')

    # zaimportuj modele z bazy danych
    # jesli jeszcze nie ma stworzonej bazy danych, to ja utworz
    # ale tylko w przypadku przyjecia konfiguracji Dev
    if app.config['FLASK_ENV'] == 'development':
        create_dev_database(app)

    # tworzenie rol administratora
    # dodanie tej roli do datastore
    # userdatastore zostalo zainicjalizowane w models.py
    def create_admin_role():
        existing_admin_role = Role.query.filter_by(name='admin').first()
        if existing_admin_role:
            flash('Rola administratora juz istnieje.', category='error')
        else:
            role = user_datastore.create_role(name='admin')

            db.session.add(role)
            db.session.commit()

            return role

    # tworzenie roli uzytkownika, dodanie do datastore
    def create_user_role():
        existing_user_role = Role.query.filter_by(name='user').first()
        if existing_user_role:
            flash('Rola uzytkownika juz istnieje.', category='error')
        else:
            role = user_datastore.create_role(name='user')

            db.session.add(role)
            db.session.commit()

            return role

    # wywolanie tworzenia admina
    # ten dekorator mowi o wykonaniu tej funkcji przed pierwszym zaladowaniem
    # tworzy sie uzytkownik, dodaje do bazy oraz przypisuje mu sie stworzona juz role administratora
    @app.before_first_request
    def create_admin():
        existing_admin = User.query.filter_by(email='admin@admin.com').first()
        if existing_admin:
            flash('Administrator juz istnieje.', category='error')
        else:
            new_admin = user_datastore.create_user(email='admin@admin.com',
                                                   username='admin',
                                                   password=generate_password_hash('admin', method='sha256'))

            db.session.add(new_admin)
            db.session.commit()

            role = create_admin_role()
            print(role)
            user_datastore.add_role_to_user(new_admin, role)
            create_user_role()

            db.session.commit()

    # inicjalizacja modulu admin
    # inicjalizacja modulu security, dodanie user_datastore do app
    admin = Admin(app, name='Admin')
    security = Security(app, user_datastore)

    # okreslenie kiedy panel administratorski ma byc dostepny
    # is_accessible - jest dostepny wtedy kiedy dzieje sie to co w returnie
    # czyli wtedy kiedy uzytkownik posiada role administratora oraz jest zalogowany
    # _handle_view - co ma sie dziac kiedy panel nie jest dostepny
    class UserModelView(ModelView):

        def is_accessible(self):
            return current_user.has_role('admin') and current_user.is_authenticated

        def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                return redirect(url_for('/'))

    # dodanie poszczegolnych zakladek do panelu administratorskiego
    # te zakladki pozwalaja na zarzadzanie struktura, zawartoscia tabel etc.
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(UserModelView(Room, db.session))
    admin.add_view(UserModelView(Role, db.session))
    admin.add_view(UserModelView(RolesUsers, db.session))

    # przekazanie danych bezposrednio do security
    # zmiana poszczegolnych flag i przekazanie jako slownik
    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            get_url=url_for,
            h=admin_helpers
        )

    # deklaracja obiektu typu LoginManager
    # zmieniamy mu potem zmienne zeby przekierowywal uzytkownikow na odpowiednie strony
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return app


def create_dev_database(app):
    if not path.exists('application/' + app.config['DEV_DB_NAME']):
        db.create_all(app=app)
        print('Baza danych została utworzona.')
