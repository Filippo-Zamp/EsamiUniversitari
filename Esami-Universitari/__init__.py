"""
The flask application package.
"""
from os import environ
from flask import Flask, flash
from sqlalchemy.sql.expression import null

import admin
import appello
import esame
import statistiche
import views
import prova
import voto
from models import Utente, engine_studente
from flask_login import LoginManager

from models import db, DB_URI
import auth


# avviamo l'applicazione Flask e l'assegnamo ad app
app = Flask(__name__)

app.register_blueprint(appello.appello_bp)
app.register_blueprint(auth.auth_bp)
app.register_blueprint(admin.admin_bp)
app.register_blueprint(views.views_bp)
app.register_blueprint(esame.esame_bp)
app.register_blueprint(prova.prova_bp)
app.register_blueprint(statistiche.statistiche_bp)
app.register_blueprint(voto.voto_bp)


# secret key: serve a mantenere sicura la connessione da client a server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'

# inizializza l'applicazione sul nostro database
db.init_app(app)

# inizializza la libreria che gestisce i login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# funzione importante che serve affinché flask login tenga
# traccia dell'utente loggato, tramite il suo id di sessione
# segue l'esempio che c'è qui: https://flask-login.readthedocs.io/en/latest/#your-user-class
@login_manager.user_loader
def user_loader(id_utente):
    with engine_studente.connect().execution_options(isolation_level="READ UNCOMMITTED") as conn:
        conn.begin()
        try:
            return Utente.query.filter_by(id=id_utente).first()
        except:
            flash("Errore")
            return null
        finally:
            conn.close()


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
