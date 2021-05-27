from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import current_user
from .models import db, Room, Message, Participant
import json
from datetime import datetime


chat = Blueprint('chat', __name__)

MSG_LIMIT = 20


@chat.route('/add-room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        roomname = request.form.get('roomname')
        password = request.form.get('password')
        roomtype = request.form.get('roomtype')
        user_limit = request.form.get('userlimit')
        accesstype = request.form.get('accesstype')
        owner_id = current_user.user_id

        if roomname != '':
            room = Room.query.filter_by(roomname=roomname).first()
            if room:
                flash('Pokój o podanej nazwie już istnieje!', category='error')
            else:
                if user_limit == '':
                    user_limit = 2
                new_room = Room(roomname=roomname,
                                password=password,
                                roomtype=roomtype,
                                user_limit=user_limit,
                                accesstype=accesstype,
                                owner_id=owner_id)
                db.session.add(new_room)
                db.session.commit()

                flash('Pokój został utworzony!', category='success')

                return redirect(url_for('views.rooms'))
        else:
            flash('Podaj nazwę pokoju!', category='error')

    return render_template("chat/add_room.html", user=current_user)


@chat.route('/delete-room', methods=['GET', 'POST'])
def delete_room():
    room = json.loads(request.data)

    room_id = room['room_id']

    room = Room.query.get(room_id)
    if room:
        if room.owner_id == current_user.user_id:
            db.session.delete(room)
            db.session.commit()

            flash('Pokój został pomyślnie usunięty.', category='success')
        else:
            flash('Nie możesz usunąć pokoju, którego nie jesteś właścicielem!', category='error')

    return jsonify({})


@chat.route('/chatroom/<room_id>/enter', methods=['GET', 'POST'])
def enter_chatroom(room_id):
    if current_user.is_authenticated:
        user_id = current_user.user_id
        room_id = int(room_id)

        room = Room.query.filter_by(room_id=room_id).first()
        participants = Participant.query.filter_by(room_id=room_id).all()

        print(len(participants))

        check_for_duplicates = Participant.query.filter_by(room_id=room_id, user_id=user_id).all()

        if len(participants) < room.user_limit and not check_for_duplicates:

            new_participant = Participant(user_id=user_id,
                                          room_id=room_id)
            db.session.add(new_participant)
            db.session.commit()

            # flash('Wejście do pokoju zakończone pomyślnie.', category='success')

            new_participantJSON = new_participant.as_dict()
            session["participant"] = new_participantJSON
            session["room_id"] = room_id

            # return redirect(url_for('views.chatroom', room_id=room_id))
            return render_template("chat/chatroom.html", user=current_user, room_id=room_id, **{"session": session})

        elif check_for_duplicates:
            return render_template("chat/chatroom.html", user=current_user, room_id=room_id, **{"session": session})

        else:
            flash('Pokój jest pełny', category='error')
            return redirect(url_for('views.rooms'))


@chat.route('/chatroom/<room_id>/leave', methods=['GET', 'POST'])
def leave_chatroom(room_id):

    user_id = current_user.user_id
    room_id = int(room_id)
    participant = Participant.query.filter_by(user_id=user_id, room_id=room_id).first()
    if participant:
        db.session.delete(participant)
        db.session.commit()

        session["participant"] = None

        # # flash('Wyjście z pokoju zakończone pomyślnie.', category='success')
        return redirect(url_for('views.rooms'))

    return redirect(url_for('views.rooms'))
    # return render_template("chat/chatroom.html", user=current_user, room_id=room_id)


@chat.route('/chatroom/<room_id>/kick/<user_id>', methods=['GET', 'POST'])
def kick_from_chatroom(room_id, user_id):

    user_id = int(user_id)
    room_id = int(room_id)
    participant = Participant.query.filter_by(user_id=user_id, room_id=room_id).first()

    if participant:
        db.session.delete(participant)
        db.session.commit()

        session["participant"] = None

    return jsonify({})


@chat.route('/chatroom/<room_id>/leave_json', methods=['GET', 'POST'])
def leave_chatroom_json(room_id):

    user_id = current_user.user_id
    room_id = int(room_id)
    participant = Participant.query.filter_by(user_id=user_id, room_id=room_id).first()

    if participant:
        db.session.delete(participant)
        db.session.commit()

        session["participant"] = None

    return jsonify({})


@chat.route('/get-messages')
def get_messages():
    return get_all_messages(to_json=True)


@chat.route('/user/get-name')
def get_name():
    data = {"name": ""}

    if current_user.is_authenticated:
        data = {"name": current_user.username}

    return jsonify(data)


@chat.route('/user/get-picture')
def get_picture():
    data = {"picture": ""}

    if current_user.is_authenticated:
        data = {"picture": current_user.image_path}

    return jsonify(data)


@chat.route('/user/get-user-id')
def get_user_id():
    data = {"user_id": ""}

    if current_user.is_authenticated:
        data = {"user_id": current_user.user_id}

    return jsonify(data)


@chat.route('/room/get-id')
def get_room_id():
    data = {"room_id": ""}

    if session["room_id"]:
        data = {"room_id": session["room_id"]}

    return jsonify(data)


@chat.route('/history')
def history():
    return render_template("chat/history.html", user=current_user)


@chat.route('/history/user/<user_id>/messages')
def history_user_message(user_id):
    json_messages = get_all_messages(user_id)

    return render_template("chat/history.html", user=current_user, messages=json_messages)


@chat.route('/history/chatroom/<room_id>/messages')
def history_room_messages(room_id):
    json_messages = get_all_messages(room_id)

    return render_template("chat/history.html", user=current_user, room_id=room_id, messages=json_messages)


@chat.route('/history/chatroom/<room_id>/user/<user_id>/messages')
def history_room_user_messages(user_id, room_id):
    json_messages = get_all_messages(user_id, room_id)

    return render_template("chat/history.html", user=current_user, messages=json_messages)


# DB METHODS
def get_all_messages(user_id=None, room_id=None, limit=100, to_json=False):

    if not user_id and not room_id:
        all_messages = Message.query.limit(limit).all()
    if not user_id and room_id:
        all_messages = Message.query.filter_by(room_id=room_id).limit(limit).all()
    if user_id and not room_id:
        all_messages = Message.query.filter_by(user_id=user_id).limit(limit).all()
    else:
        all_messages = Message.query.filter_by(user_id=user_id, room_id=room_id).limit(limit).all()

    # for message in all_messages:
    #     if not message.content:
    #         all_messages.remove(message)

    # usuwanie pustych wiadomosci
    i = 0
    while i < len(all_messages):
        if not all_messages[i].content:
            del all_messages[i]
            i -= 1
        i += 1

    if to_json:
        all_messages_asdict = []

        for message in all_messages:
            all_messages_asdict.append(message.as_dict())

        all_messagesJSON = json.dumps(all_messages_asdict, indent=4, sort_keys=True, default=str)

        return all_messagesJSON
    else:
        return all_messages


def save_message(message):

    user_id = current_user.user_id
    room_id = int(message["room_id"])
    content = message["message"]

    new_message = Message(content=content,
                          date=datetime.now(),
                          is_saved=True,
                          user_id=user_id,
                          room_id=room_id)

    db.session.add(new_message)
    db.session.commit()


