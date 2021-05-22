from socket import AF_INET, socket, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread
import time
from person import Person

###   ###
# 29:19 #
###   ###

# STALE GLOBALNE
HOST = 'localhost'
PORT = 5500
ADDR = (HOST, PORT)
MAX_CONNECTIONS = 10
BUFSIZ = 512

# ZMIENNE GLOBALNE
persons = []
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR) # przygotuj serwer

def broadcast(msg, name):
    """
    Wysyłaj nowe wiadomości do wszystkich klientów.
    :param msg: bytes["utf8"]
    :param name: str
    :return:
    """
    for person in persons:
        client = person.client
        try:
            client.send(bytes(name, "utf8") + msg)
        except Exception as e:
            print("[EXCEPTION] in broadcast", e)


# tworzy obiekty klientow
# przechowuje adres ip i nazwe
# dzieki temu bedziemy wiedziec kto z kim czatuje i kto wysyla wiadomosci
def client_communication(person):
    """
    Wątek przechwytujący wszystkie wiadomości od klienta.
    :param Person: person
    :return: None
    """
    client = person.client

    # get persons name
    name = client.recv(BUFSIZ).decode("utf8")
    person.set_name(name)

    msg = bytes(f"{name} dołączył do pokoju!", "utf8")
    broadcast(msg, "") # rozglaszaj wiadomość powitalna

    while True:
        msg = client.recv(BUFSIZ)

        if msg == bytes("{quit}", "utf8"):
            client.close()
            persons.remove(person)

            broadcast(bytes(f"{name} opuścił chat...", "utf8"), "")
            print(f"[DISCONNECTED] {name} rozłączył się.")
            break
        else:
            broadcast(msg, name + ": ")
            print(f"{name}: ", msg.decode("utf8"))


def wait_for_connection():
    """
    Czekaj na połączenie od nowych klientów, utwórz nowy wątek po połączeniu.
    :param SERVER: SOCKET
    :return:
    """
    while True:
        try:
            client, addr = SERVER.accept()
            person = Person(addr, client)
            persons.append(person)

            print(f"[CONNECTION] {addr} połączył się z serwerem. Czas: {time.time()}")
            Thread(target=client_communication, args=(person,)).start()
        except Exception as e:
            print("[EXCEPTION] in wait_for_connection", e)
            break

    print("[ERROR] Błąd serwera.")


if __name__ == "__main__":
    SERVER.listen(MAX_CONNECTIONS)
    print("[STARTED] Czekam na połączenie...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()