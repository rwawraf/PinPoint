# importujemy z __init__.py objekt o nazwie db
# czyli 'uchwyt' do bazy danych
# UserMixin to modul ulatwiajacy napisanie logowania
# tworzymy tutaj modele na wzor naszych tabel w bazie danych

from flask_security import RoleMixin, SQLAlchemyUserDatastore, UserMixin
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# helper table
# potrzebujemy jej, poniewaz jest łącznikiem między relacją wiele-do-wielu
# nie umialem zdefiniowac tego inaczej, jako zwykla tabele ktora jest inaczej inicjalizowana
# w koncu udalo mi sie to zrobic, zwykla definicja z db.Model
class RolesUsers(db.Model):
    __tablename__ = "roles_and_users"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    users = db.relationship('User')
    roles = db.relationship('Role')


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


# klasa uzytkownik musi dziedziczyc po db.Model oraz UserMixin
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    active = db.Column(db.Boolean)
    registration_date = db.Column(db.DateTime(timezone=True), default=func.now())
    is_banned = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String())

    # zarejestrowanie zwiazku z inna tabela
    # aby zarejestrowac zwiazek wiele do wielu trzeba podac nazwe tabeli z "__tablename__"
    rooms = db.relationship('Room')
    roles = db.relationship('Role', secondary="roles_and_users", backref=db.backref('user', lazy='dynamic'))
    notes = db.relationship('Note')
    messages = db.relationship('Message')
    user_settings = db.relationship('UserSettings')
    is_participant_in = db.relationship('Participant')
    is_blocked_participant_in = db.relationship('BlockedParticipant')
    is_allowed_participant_in = db.relationship('AllowedParticipant')

    # musze napisac metode bo logowanie przestalo poprawnie dzialac
    def get_id(self):
        return self.user_id


# pokoje, chatroomy
class Room(db.Model):
    __tablename__ = "room"
    room_id = db.Column(db.Integer, primary_key=True)
    roomname = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150), default=None)
    roomtype = db.Column(db.String(150)) # do poprawy! trzeba zdefiniowac typ (chat, whiteboard)
    user_limit = db.Column(db.Integer)
    accesstype = db.Column(db.String(150)) # do poprawy! trzeba zdefiniowac typ (publiczny, prywatny)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    messages = db.relationship('Message')
    participants = db.relationship('Participant')
    blocked_participants = db.relationship('BlockedParticipant')
    allowed_participants = db.relationship('AllowedParticipant')


# notatki dodawane przez uzytkownika
class Note(db.Model):
    __tablename__ = "note"
    note_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000))
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())

    # zdefiniowanie klucza obcego
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))


# wiadomosc 'normalna' wysylana w chatroomie
class Message(db.Model):
    __tablename__ = "message"
    message_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    is_saved = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# prywatna wiadomosc wysylana bezposrednio miedzy uzytkownikami
class PrivateMessage(db.Model):
    __tablename__ = "private_message"
    private_message_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000))

    user_sender_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user_receiver_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    # gdy tabela ma kilka kluczy obcych z tej samej tabeli, trzeba zwiazki zdefiniowac w ten sposob
    user_sender = db.relationship('User', foreign_keys=[user_sender_id])
    user_receiver = db.relationship('User', foreign_keys=[user_receiver_id])


# ustawienia uzytkownika ktore sobie sam zdefiniuje. pozniej mozna dodac jeszcze wiecej
class UserSettings(db.Model):
    __tablename__ = "user_settings"
    user_settings_id = db.Column(db.Integer, primary_key=True)
    app_theme = db.Column(db.String(5))

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))


# relacje miedzy uzytkownikami - mozna kogos zablokowac albo dodac do znajomych
# https://www.codedodle.com/social-network-friends-database/Status Codes
# Status Codes Meaning
# 0	Pending
# 1	Accepted
# 2	Declined
# 3	Blocked
class UserRelation(db.Model):
    __tablename__ = "user_relation"
    user_relation_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.SmallInteger)

    relating_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    related_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    # pozwala na sprawdzenie kto komu wyslal zapytanie o dodanie do znajomych
    # ktory uzytkownik ostatni wykonal akcje
    action_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    # gdy tabela ma kilka kluczy obcych z tej samej tabeli, trzeba zwiazki zdefiniowac w ten sposob
    relating_user = db.relationship('User', foreign_keys=[relating_user_id])
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    action_user = db.relationship('User', foreign_keys=[action_user_id])


# uzytkownicy obecni w danym pokoju
class Participant(db.Model):
    __tablename__ = "participant"
    participant_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# lista zablokowanych uzytkownikow w danym pokoju
class BlockedParticipant(db.Model):
    __tablename__ = "blocked_participant"
    blocked_participant_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(150))

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))


# lista dopuszczonych uzytkownikow do prywatnego pokoju
class AllowedParticipant(db.Model):
    __tablename__ = "allowed_participant"
    allowed_participant_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))


# zostalo zainicjalizowane tutaj zeby moc zaimportowac sobie to w __init__
user_datastore = SQLAlchemyUserDatastore(db, User, Role)