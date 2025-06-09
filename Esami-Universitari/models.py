from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# DB URI
# db_uri dei vari ruoli (studente, docente, admin) da usare alla fine quando impostiamo i ruoli nell'app
DB_URI_STUDENTE = "postgresql+psycopg2://studente:studente@localhost/esame_lab"
DB_URI_DOCENTE = "postgresql+psycopg2://docente:docente@localhost/esame_lab"
DB_URI_ADMIN = "postgresql+psycopg2://admin:admin@localhost/esame_lab"

DB_URI_B = "postgresql+psycopg2://postgres:187714aa@localhost/esame_lab"

# db uri attuale
DB_URI = DB_URI_B

# creazione engine
engine = create_engine(DB_URI)
engine_studente = create_engine(DB_URI_STUDENTE)
engine_docente = create_engine(DB_URI_DOCENTE)
engine_admin = create_engine(DB_URI_ADMIN)

Base = declarative_base()
metadata = Base.metadata

# creazione della factory
Session = sessionmaker(bind=engine)
session = Session()

login_manager = LoginManager()


class Utente(UserMixin, Base, db.Model):
    __tablename__ = 'utente'

    id = Column(Integer, primary_key=True, server_default=text("nextval('utente_id_seq'::regclass)"))
    email = Column(String(50), nullable=False)
    nome = Column(String(50), nullable=False)
    cognome = Column(String(50), nullable=False)
    data_nascita = Column(Date, nullable=False)
    sesso = Column(String(50), nullable=False)
    ruolo = Column(Integer, nullable=False)
    password = Column(String(200), nullable=False)
    telefono = Column(String(11), nullable=False)
    altri_contatti = Column(String(999))

    # __repr__ restituisce un array associativo contentente i valori qui sotto elencati, vedi link per chiarimenti
    # https://stackoverflow.com/questions/57647799/what-is-the-purpose-of-thing-sub-function-returning-repr-with-f-str
    def __repr__(self):
        return self._repr(
            email=self.email,
            nome=self.nome,
            cognome=self.cognome,
            data_nascita=self.data_nascita,
            sesso=self.sesso,
            ruolo=self.ruolo,
            telefono=self.telefono,
            password=self.password,
            altri_contatti=self.altricontatti
        )

    def __init__(self, email, nome, cognome, data_nascita, sesso, ruolo, telefono, password, altri_contatti):
        self.email = email
        self.nome = nome
        self.cognome = cognome
        self.data_nascita = data_nascita
        self.sesso = sesso
        self.ruolo = ruolo
        self.telefono = telefono
        self.password = generate_password_hash(password, method='scrypt', salt_length=8)
        self.altri_contatti = altri_contatti

        # converte la password da normale ad "hashata"
    def set_password(self, pwd):
        self.password = generate_password_hash(pwd, method='scrypt', salt_length=8)

    # controlla l'hash della password
    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def is_active(self):
        """Vero se l'utente � attivo"""
        return True

    def get_id(self):
        return self.id

    def get_role(self):
        return self.ruolo

    def is_authenticated(self):
        """Ritorna true se l'utente � autenticato"""
        return True

    def is_anonymous(self):
        """Ritorna falso, perch� gli utenti anonimi non sono supportati"""
        return False


class Esame(Base, db.Model):
    __tablename__ = 'esame'

    id = Column(Integer, primary_key=True, server_default=text("nextval('esame_id_seq'::regclass)"))
    nome = Column(String(50), nullable=False)
    anno_accademico = Column(String(50), nullable=False)
    cfu = Column(Integer, nullable=False)
    is_opzionale = Column(Boolean, nullable=False)
    id_utente = Column(ForeignKey('utente.id'), nullable=False)


class Prova(Base):
    __tablename__ = 'prova'

    id = Column(Integer, primary_key=True, server_default=text("nextval('prova_id_seq'::regclass)"))
    nome = Column(String(50), nullable=False)
    tipo = Column(String(50), nullable=False)
    descrizione = Column(String(999), nullable=True)
    id_esame = Column(ForeignKey(Esame.id), nullable=False)
    peso = Column(Integer, nullable=False)
    id_utente = Column(ForeignKey(Utente.id), nullable=False)
    voto_minimo = Column(Integer, nullable=False)
    esame = relationship(Esame)


class DipendenzaProva(Base, db.Model):
    __tablename__ = 'dipendenza_prova'

    id = Column(Integer, primary_key=True, server_default=text("nextval('dipendenza_prova_id_seq'::regclass)"))
    id_prova_1 = Column(ForeignKey(Prova.id), nullable=False)
    id_prova_2 = Column(ForeignKey(Prova.id), nullable=False)


class Appello(Base, db.Model):
    __tablename__ = 'appello'

    id = Column(Integer, primary_key=True, server_default=text("nextval('appello_id_seq'::regclass)"))
    id_prova = Column(ForeignKey(Prova.id), nullable=False)
    data_ora = Column(TIMESTAMP, nullable=False)
    data_scad = Column(Date, nullable=False)
    aula = Column(String(50), nullable=False)
    prova = relationship(Prova)


class VotoAppello(Base):
    __tablename__ = 'voto_appello'

    id = Column(Integer, primary_key=True, server_default=text("nextval('voto_appello_id_seq'::regclass)"))
    id_appello = Column(ForeignKey(Appello.id), nullable=False)
    id_utente = Column(ForeignKey(Utente.id), nullable=False)
    voto = Column(Integer, nullable=False)
    is_confermato = Column(Boolean, nullable=False)
    appello = relationship(Appello)


class VotoEsame(Base):
    __tablename__ = 'voto_esame'

    id = Column(Integer, primary_key=True, server_default=text("nextval('voto_esame_id_seq'::regclass)"))
    id_esame = Column(ForeignKey(Esame.id), nullable=False)
    id_utente = Column(ForeignKey(Utente.id), nullable=False)
    voto = Column(Integer, nullable=False)
    is_confermato = Column(Boolean, nullable=False)
    esame = relationship(Esame)


class Prenotazione(Base):
    __tablename__ = 'prenotazione'

    id = Column(Integer, primary_key=True, server_default=text("nextval('prenotazione_id_seq'::regclass)"))
    id_appello = Column(ForeignKey(Appello.id), nullable=False)
    id_utente = Column(ForeignKey(Utente.id), nullable=False)
    data = Column(Date, nullable=False)
    appello = relationship(Appello)