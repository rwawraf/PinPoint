from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
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
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def seed():
    pass


if __name__ == '__main__':
    manager.run()