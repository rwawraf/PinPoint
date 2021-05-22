from flask_socketio import SocketIO
from application import create_app
from application.chat import save_message
import config


app = create_app()
socketio = SocketIO(app)


@socketio.on('event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    """
    Funkcja odpowiedzialna za zapisywanie wiadomości
    oraz za wysyłanie ich do innych klientów.
    :param json: json
    :param methods: POST GET
    :return: None
    """
    data = dict(json)
    if "user_id" and "room_id" in data:
        save_message(json)

    socketio.emit('message response', json)


@socketio.on('notification')
def show_notification(json):
    # data = dict(json)

    socketio.emit('notification', json)


# MAINLINE
if __name__ == "__main__":  # start the web server
    socketio.run(app, debug=True, host=str(config.Config.SERVER))
