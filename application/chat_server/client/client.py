import json
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock


class Client:

    HOST = 'localhost'
    PORT = 5500
    ADDR = (HOST, PORT)
    BUFSIZ = 512


    def __init__(self, name):
        """
        Zainicjalizuj obiekt i wyślij jego nazwę do serwera.
        :param name: str
        """
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)
        self.messages = []
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()
        self.send_message(name)
        self.lock = Lock()


    def receive_messages(self):
        """
        Odbieraj wiadomości z serwera.
        :return: None
        """
        while True:
            try:
                msg = self.client_socket.recv(self.BUFSIZ).decode()

                # upewnij sie ze mozna bezpiecznie uzyskac dostep do pamieci
                self.lock.acquire()
                self.messages.append(msg)
                self.lock.release()

            except Exception as e:
                print("[EXCEPTION] in receive_messages", e)
                break


    def send_message(self, msg):
        """
        Wysyłaj wiadomości do serwera.
        :param msg: str
        :return: None
        """

        try:
            self.client_socket.send(bytes(msg, "utf8"))
            if msg == "{quit}":
                self.client_socket.close()

        except Exception as e:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.ADDR)
            print(e)


    def get_messages(self):
        """
        Zwraca listę wysłanych przez użytkownika wiadomości.
        :return: list[str]
        """

        messages_copy = self.messages[:]

        # upewnij sie ze pamiec jest wolna
        self.lock.acquire()
        self.messages = []
        self.lock.release()

        return messages_copy


    # rozlacz sie wysylajac sobie samemu wiadomosc o tresci {quit}
    def disconnect(self):
        self.send_message("{quit}")
