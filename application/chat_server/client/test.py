from client import Client
import time
from threading import Thread


c1 = Client("rafal")
c2 = Client("pawel")


def update_messages():
    """
    Aktualizuje lokalną listę wiadomości.
    :return: None
    """

    local_messages = []
    run = True

    while run:
        time.sleep(0.1) # aktualizuj co kazda 1/10 sekundy
        new_messages = c1.get_messages() # odbierz wszystkie nowe wiadomosci od klienta
        local_messages.extend(new_messages) # dodaj do listy lokalnej

        for msg in new_messages: # wyswietlaj nowe wiadomosci
            print(msg)

            if msg == f"{quit}":
                run = False
                break


# Thread(target=update_messages).start()

c1.send_message("to ja klient nr 1, to jest moj test")
time.sleep(5)
c2.send_message("teraz to ja, klient nr 2, to jest moj test")
time.sleep(5)
c1.send_message("co tam u ciebie slychac paroweczko")
time.sleep(5)
c2.send_message("nom wszystko w porzadeczku")
time.sleep(5)

c1.disconnect()
time.sleep(2)
c2.disconnect()