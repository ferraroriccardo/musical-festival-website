from flask_login import LoginManager
from models import User
import dao.utenti_dao as utenti_dao

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    db_user = utenti_dao.get_user_by_id(user_id)
    if db_user is None:
        return None
    return User(
        id=db_user["id"],
        nome=db_user["nome"],
        email=db_user["email"],
        password=db_user["password"],
        tipo=db_user["tipo"],
        id_biglietto=db_user["id_biglietto"]
    )

def setup_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"