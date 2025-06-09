from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, get_flashed_messages
from wtforms import SelectField, DateField, DateTimeLocalField, StringField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange
from flask_wtf import FlaskForm

from auth import set_ruolo, set_dati_utente
from models import db, Prova, Utente, Appello, Prenotazione, VotoAppello
from flask_login import current_user, login_required

appello_bp = Blueprint("appello_bp", __name__)


class ProvaForm(FlaskForm):
    # Prendere nome prova da inserire quì
    aula = SelectField('Aula', validators=[InputRequired()],
                       choices=['Aula 1 (Edificio Zeta)', 'Aula 2 (Edificio Zeta)', 'Aula A (Edificio Zeta)',
                                'Aula B (Edificio Zeta)', 'Aula C (Edificio Zeta)', 'Aula D (Edificio Zeta)',
                                'Aula Epsilon 1', 'Aula Epsilon 2'])
    data_ora = DateTimeLocalField('Data Ora dell appello', validators=[InputRequired()])
    data_scad = DateField('Data Scadenza', validators=[InputRequired()])


class TestForm(FlaskForm):
    # Prendere nome prova da inserire quì
    voto = IntegerField(validators=[InputRequired(), NumberRange(min=0, max=30)])


# Funzione che ci permette di creare un nuovo appello
@appello_bp.route('/creazione_appello/<prova>', methods=['GET', 'POST'])
@login_required
def creazione_appello(prova):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = set_ruolo()
    form = ProvaForm()
    # prendo il contenuto del form di registrazione
    # generato in html dalla classe qui sopra
    if request.method == 'POST':
        aula = form.aula.data
        data_ora = form.data_ora.raw_data[0]
        data_scad = form.data_scad.data
        nuovo_appello = Appello(aula=aula,
                                data_ora=data_ora,
                                data_scad=data_scad,
                                id_prova=prova
                                )

        db.session.add(nuovo_appello)
        db.session.commit()

        return redirect(url_for('appello_bp.lista_appello'))

    return render_template('creazione_appello.html', prova=prova, form=form, title='Creazione appello', ruolo=ruolo,
                           dati_utente=dati_utente_corrente)


# funzione che permette di visualizzare una lista degli appelli
@appello_bp.route('/lista_appello', methods=['POST', 'GET'])
@login_required
def lista_appello():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = set_ruolo()
    if request.method == 'POST':
        appello_update = request.form.get('update')
        appello_subscribe = request.form.get('subscrib')
        appello_cancel = request.form.get('cancel')
        if appello_update is not None:
            return redirect(url_for('.update_appello', appello=appello_update))
        elif appello_subscribe is not None:
            today = date.today()
            nuovo_subscrib = Prenotazione(id_appello=appello_subscribe,
                                          id_utente=Utente.get_id(current_user),
                                          data=today
                                          )
            db.session.add(nuovo_subscrib)
            db.session.commit()
            return redirect(url_for(".lista_appello"))
        elif appello_cancel is not None:
            cancel(appello_cancel)
            return redirect(url_for(".lista_appello"))
        else:
            form = {}
            appello_bookings = request.form.get('subscription')
            subscription = db.session.query(Prenotazione.id_utente).filter_by(id_appello=appello_bookings).all()
            appello = db.session.query(Appello.id).filter_by(id=appello_bookings).first()
            listsub = []
            for i in range(len(subscription)):
                utente = db.session.query(Utente).filter(Utente.id.in_(subscription[i])).first()
                query = db.session.query(VotoAppello).filter_by(id_appello=appello_bookings, id_utente=utente.id).\
                    first()
                if query is None:
                    listsub.append(utente)
                    form[utente.id] = TestForm(formdata=None)
            subscription_count = len(subscription)
            return render_template("iscrizioni_lista_appello.html", list=listsub, form=form, count=subscription_count,
                                   appello=appello.id, ruolo=ruolo, dati_utente=dati_utente_corrente)
    else:
        ruolo = set_ruolo()
        if ruolo == '1':
            query_p = db.session.query(Appello).join(Prova).filter(Prova.id_utente == Utente.get_id(current_user))\
                .count()
        else:
            query_p = db.session.query(Prenotazione.id_appello).filter_by(id_utente=Utente.get_id(current_user)).all()
        list = []
        for i in range(len(query_p)):
            list.append(query_p[i][0])
        query_a = db.session.query(Appello).filter(Appello.id.not_in(list)).all()
        return render_template("lista_appello.html", list=query_a, ruolo=ruolo, title="Lista Appelli",
                               dati_utente=dati_utente_corrente)


# funzione di modifica appello
@appello_bp.route('/update_appello/<appello>', methods=['POST', 'GET'])
@login_required
def update_appello(appello):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    query = db.session.query(Appello).filter_by(id=appello).first()
    ruolo = set_ruolo()

    class ProvaForm1(FlaskForm):
        aula = SelectField('Aula', default=query.aula, validators=[InputRequired()],
                           choices=['Aula 1 (Edificio Zeta)', 'Aula 2 (Edificio Zeta)', 'Aula A (Edificio Zeta)',
                                    'Aula B (Edificio Zeta)', 'Aula C (Edificio Zeta)', 'Aula D (Edificio Zeta)',
                                    'Aula Epsilon 1', 'Aula Epsilon 2'])
        data_ora = DateTimeLocalField('Data Ora dell appello', default=query.data_ora, validators=[InputRequired()])
        data_scad = DateField('Data Scadenza', default=query.data_scad, validators=[InputRequired()])

    form = ProvaForm1()
    if request.method == 'POST':
        aula = request.form.get('aula')
        data_ora = request.form.get('data_ora')
        data_scad = request.form.get('data_scad')

        db.session.query(Appello).filter(Appello.id == query.id). \
            update({'aula': aula, 'data_scad': data_scad,
                    'data_ora': data_ora})
        db.session.commit()
        return redirect(url_for(".lista_appello"))
    else:
        return render_template("update_appello.html", query=query, form=form, ruolo=ruolo, title="Update Appello",
                               dati_utente=dati_utente_corrente)


# funzione per cancellare un appello
def cancel(appello):
    db.session.query(Appello).filter_by(id=appello).delete()
    db.session.commit()
