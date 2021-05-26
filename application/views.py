from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from .models import db, User, Room, Note, UserRelation, Message, Participant

# tutaj sa tworzone Routes - czyli podstrony na ktore serwer ma kierowac zapytanie
views = Blueprint('views', __name__)


# zabezpieczenie przed wyswietlaniem strony domowej jesli uzytkownik nie jest zalogowany
# za pomoca login_required
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # za kazdym razem bedzie renderowana strona home.html
    # ktora korzysta z base.html
    # jedynie zmienia bloki w base.html na swoje
    # jest to duze ulatwienie i oszczednosc czasu

    return render_template("home.html", user=current_user)


@views.route('/rooms', methods=['GET', 'POST'])
@login_required
def rooms():
    """
    :return: list of all rooms
    """
    all_rooms = Room.query.all()
    participants = Participant.query.all()
    users = User.query.all()

    return render_template("chat/rooms.html", user=current_user, all_rooms=all_rooms, participants=participants, users=users)


@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    """
    :return: list of all notes
    """
    all_notes = Note.query.all()

    return render_template("notes/notes.html", user=current_user, all_notes=all_notes)


@views.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    """
    :return: list of all messages
    """
    all_messages = Message.query.all()

    return render_template("chat/history.html", user=current_user, messages=all_messages)


@views.route('/chatroom/<room_id>', methods=['GET', 'POST'])
@login_required
def chatroom(room_id):
    all_messages = Message.query.all()

    return render_template("chat/chatroom.html", user=current_user, room_id=room_id)


@views.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    """
    :return: list of all user relations
    """
    all_relations = UserRelation.query.all()
    return render_template("friends/friends.html", user=current_user, all_relations=all_relations)


@views.route('/black-list', methods=['GET', 'POST'])
@login_required
def blocked():
    """
    :return: list of all user relations
    """
    all_relations = UserRelation.query.all()
    return render_template("friends/blocked.html", user=current_user, all_relations=all_relations)


@views.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """
    :return: list of all users
    """

    user_list = User.query.all()

    relations = UserRelation.query.all()
    return render_template("users/users.html", user=current_user, users=user_list, relations=relations)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template("profile/profile.html", user=current_user)


@views.route('/_get_participants/<room_id>', methods=['GET', 'POST'])
def get_participants_name(room_id):
    participants = Participant.query.filter_by(room_id=room_id).all()
    users = []

    for participant in participants:
        user = User.query.filter_by(user_id=participant.user_id).first()
        # users.append(user.user_id)
        users.append(user.username)

    return jsonify(users)


@views.route('/_get_users', methods=['GET', 'POST'])
def get_users():
    all_users = User.query.all()
    user_list = []

    for user in all_users:
        data = {'username': user.username, 'user_id': user.user_id}
        user_list.append(data)

    return jsonify(user_list)

