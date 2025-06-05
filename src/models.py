from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, tipo, id_biglietto):
        self.id = id
        self.email = email
        self.password = password
        self.tipo = tipo
        self.id_biglietto = id_biglietto