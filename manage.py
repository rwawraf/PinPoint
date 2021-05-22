from flask_script import Manager
import flask_migrate
from run import app
from application import db

"""
plik wykorzystywany przy tworzeniu bazy danych na serwerze.
wpierw trzeba wprowadzic dobra konfiguracje polaczenia z baza danych w config.py.
nastepnie, aby utworzyc baze danych, trzeba wprowadzic kolejno polecenia w terminalu:
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
"""

manager = Manager(app)
migrate = flask_migrate.Migrate(app, db)

manager.add_command('db', flask_migrate.MigrateCommand)


@manager.command
def seed():
    pass


if __name__ == '__main__':
    manager.run()