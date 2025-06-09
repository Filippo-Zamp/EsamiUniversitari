from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.sql.expression import *
from models import engine_studente, Utente, db, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, EmailField
from wtforms.validators import InputRequired, Email, Length

auth_bp = Blueprint("auth_bp", __name__)

# costanti utili
RUOLI = ["admin", "docente", "studente"]


# funzione che renderizza la home del sito
@auth_bp.route('/')
def index():
    return render_template('index.html')


# classe di wtforms che contiene il form di login
# scrivendo nell'html usando la sintassi di jinja2
# {{ form.email('class_='form-control') }} si otterra'
# come risultato il campo email da riempire. In pratica
# tu nella pagina html scrivi python, questo poi viene
# tradotto in html
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email(message='Email non valida'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=1, max=50)])


# stessa cosa di quello sopra, ma per la registrazione
class SignupForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email(message='Email non valida'), Length(max=50)])
    nome = StringField('Nome', validators=[InputRequired(), Length(min=2, max=50)])
    cognome = StringField('Cognome', validators=[InputRequired(), Length(min=2, max=50)])
    data = DateField('Data', validators=[InputRequired()])
    genere = SelectField('Genere', validators=[InputRequired()], choices=['Maschio', 'Femmina', 'Altro'])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=1, max=50)])
    telefono = StringField('Telefono', validators=[InputRequired(), Length(max=11)])
    altricontatti = StringField('Altri contatti', validators=[Length(max=999)])


# funzione che renderizza al css per accedere
@auth_bp.route('/accedi')
def accedi():
    dati_utente = set_dati_utente()
    return render_template('template.html', dati_utente=dati_utente)


# funzione che effettua il logout dell'utente loggato e reindirizza
# alla home
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.close()
    return render_template('logout.html')


# funzione per ritornare il ruolo di un utente
def set_ruolo():
    ruolo = None
    if current_user is not None:
        ruolo = RUOLI[Utente.get_role(current_user)]
    return ruolo


# funzione che ritorna i dati dell utente
def set_dati_utente():
    dati_utente_corrente = None
    if current_user is not None:
        dati_utente_corrente = db.session.query(Utente).filter_by(id=Utente.get_id(current_user)).first()
    return dati_utente_corrente


# funzione che renderizza la pagina di login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    get_flashed_messages()
    # crea il form seguendo le istruzioni della classe login scritta sopra
    form = LoginForm()
    # se tutti i campi sono validati
    ema = form.email.data
    pwd = form.password.data
    # controlla che ci sia una sola email corrispondente
    if request.method == 'POST':
        utente = Utente.query.filter_by(email=ema).first()
        # se c'è, allora controlla anche la password (salvata criptata)
        if utente is not None and utente.check_password(pwd):
            # se tutto va bene, effettua il login, aggiungendo l'utente
            # alla sessione e riportandolo alla schermata profilo
            login_user(utente)
            if ema == "admin@gmail.com" and pwd == "admin":
                return redirect(url_for('admin_bp.amministrazione'))
            return redirect(url_for('views_bp.home_principale'))
        flash('Email o Password errati')
        return redirect('/login')

    return render_template('login.html', form=form)


# permette ad un nuovo utente di registrarsi nell'applicazione
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    get_flashed_messages()
    form = SignupForm()
    # prendo il contenuto del form di registrazione
    # generato in html dalla classe qui sopra
    if request.method == 'POST':
        eml = form.email.data
        nome = form.nome.data
        cognome = form.cognome.data
        data = form.data.data
        genere = form.genere.data
        passwd = form.password.data
        tel = form.telefono.data
        altri_cont = form.altricontatti.data

        usr_gia_esiste = False
        with engine_studente.connect().execution_options(isolation_level="READ COMMITTED") as conn:
            lista_utenti = conn.execute(select(Utente.email))
        for row in lista_utenti:
            if row[0] == eml and usr_gia_esiste is False:
                usr_gia_esiste = True
        if usr_gia_esiste:
            flash("Sei gia iscritto? Controlla meglio la tua email")
        else:
            # se ha questa mail, è un admin
            if eml == "admin@gmail.com" and passwd == "admin":
                rl = 0
            else:
                rl = 2

            # creo l'oggetto utente
            nuovo_utente = Utente(email=eml,
                                  nome=nome,
                                  cognome=cognome,
                                  data_nascita=data,
                                  sesso=genere,
                                  ruolo=rl,
                                  telefono=tel,
                                  password=passwd,
                                  altri_contatti=altri_cont)

            db.session.add(nuovo_utente)
            db.session.commit()

            flash('Registrazione completata')
            return redirect('/login')

    return render_template('signup.html', form=form)
