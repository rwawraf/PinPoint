class Person:
    """
    Pojedynczy użytkownik.
    Przechowuje nazwę użytkownika, port oraz adres IP
    """
    def __init__(self, addr, client):
        self.addr = addr
        self.client = client
        self.name = None

    def set_name(self, name):
        """
        Ustawia nazwę użytkownika.
        :param name: string
        :return: None
        """
        self.name = name

    def __repr__(self):
        return f"Person({self.addr}, {self.name})"
