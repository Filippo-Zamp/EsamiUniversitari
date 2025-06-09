from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm

from auth import set_ruolo, set_dati_utente
from models import db, Prova, Utente, engine_docente, DipendenzaProva
from sqlalchemy.sql.expression import select
from flask_login import current_user, login_required

prova_bp = Blueprint("prova_bp", __name__)


# classe wtforms per creare form in modo veloce
class ProvaForm(FlaskForm):
    # Prendere nome prova da inserire quì
    nome = StringField('Nome della Prova', validators=[InputRequired(), Length(max=50)])
    tipo = SelectField('Tipo', validators=[InputRequired()], choices=['Scritto', 'Orale', 'Progetto'])
    descrizione = StringField('Descrizione', validators=[InputRequired(), Length(max=999)])
    peso = IntegerField('Peso', validators=[InputRequired(), Length(max=2)])
    voto_minimo = IntegerField('Voto Minimo', validators=[InputRequired(), Length(max=2)])
    dipendenze = SelectMultipleField('Dipendenze', choices=[])


# Funzione che permette di creare un nuovo prova
@prova_bp.route('/creazione_prova/<esame>', methods=['GET', 'POST'])
@login_required
def creazione_prova(esame):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = set_ruolo()
    query = db.session.query(Prova).filter_by(id_esame=esame).all()
    form = ProvaForm()
    prova_id = []
    for i in range(len(query)):
        prova_id.append(query[i].id)
    form.dipendenze.choices = prova_id
    # prendo il contenuto del form di registrazione
    # generato in html dalla classe qui sopra
    if request.method == 'POST':
        nome = form.nome.data
        tipo = form.tipo.data
        peso = form.peso.data
        descrizione = form.descrizione.data
        voto_minimo = form.voto_minimo.data
        dipendenze = form.dipendenze.data

        prova_gia_esiste = False
        with engine_docente.connect().execution_options(isolation_level="READ COMMITTED") as conn:
            list_prova = conn.execute(select(Prova.nome))
        for row in list_prova:
            if row[0] == nome and prova_gia_esiste is False:
                prova_gia_esiste = True
        if prova_gia_esiste:
            flash("Esiste già una prova con questo nome! Cambiare nome, grazie.")
        else:
            nuova_prova = Prova(nome=nome,
                                tipo=tipo,
                                descrizione=descrizione,
                                id_esame=esame,
                                peso=peso,
                                id_utente=Utente.get_id(current_user),
                                voto_minimo=voto_minimo
                                )
            db.session.add(nuova_prova)
            db.session.commit()
            for i in range(len(dipendenze)):
                nuova_dipendenza = DipendenzaProva(id_prova_1=nuova_prova.id,
                                                   id_prova_2=dipendenze[i]
                                                   )
                db.session.add(nuova_dipendenza)
                db.session.commit()

            return redirect(url_for('esame_bp.lista_esame'))
    return render_template('creazione_prova.html', esame=esame, form=form, title='Creazione Prova', ruolo=ruolo,
                           dati_utente=dati_utente_corrente)


# Funzione che permette di visualizzare la lista delle prome di un determinato esame
@prova_bp.route('/lista_prova/<esame>', methods=['POST', 'GET'])
@login_required
def lista_prova(esame):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    if request.method == 'POST':
        prova_update = request.form.get('update')
        prova_cancel = request.form.get('cancel')
        create_appello = request.form.get('appello')
        if prova_update is not None:
            return redirect(url_for('.update_prova', prova=prova_update))
        elif create_appello is not None:
            return redirect(url_for('appello_bp.creazione_appello', prova=create_appello))
        elif prova_cancel is not None:
            cancel(prova_cancel)
            return redirect(url_for("esame_bp.lista_esame"),)
    else:
        ruolo = set_ruolo()
        query = db.session.query(Prova).filter_by(id_esame=esame).all()
        queryid = db.session.query(Prova).filter_by(id_esame=esame).first()
        return render_template("lista_prova.html", list=query, queryid=queryid, ruolo=ruolo, title="Lista Prove",
                               dati_utente=dati_utente_corrente)


# funzione di modifica prova
@prova_bp.route('/update_prova/<prova>', methods=['POST', 'GET'])
@login_required
def update_prova(prova):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    query = db.session.query(Prova).filter_by(id=prova).first()
    ruolo = set_ruolo()
    query1 = db.session.query(Prova).filter_by(id_esame=query.id_esame).all()
    form = ProvaForm()
    prova_id = []
    for i in range(len(query1)):
        if query1[i].id != query.id:
            prova_id.append(query1[i].id)
    form.dipendenze.choices = prova_id
    form.nome.data = query.nome
    form.tipo.data = query.tipo
    form.descrizione.data = query.descrizione
    form.peso.data = query.peso
    form.voto_minimo.data = query.voto_minimo

    if request.method == 'POST':
        nome = request.form.get('nome')
        tipo = request.form.get('tipo')
        peso = request.form.get('peso')
        descrizione = request.form.get('descrizione')
        voto_minimo = request.form.get('voto_minimo')
        dipendenze = form.dipendenze.data

        db.session.query(Prova).filter(Prova.id == query.id). \
            update({'nome': nome, 'tipo': tipo,
                    'peso': peso, 'descrizione': descrizione,
                    'voto_minimo': voto_minimo})
        db.session.commit()

        db.session.query(DipendenzaProva).filter_by(id_prova_1=query.id).delete()
        db.session.commit()

        for i in range(len(dipendenze)):
            db.session.query(DipendenzaProva).filter_by(id_prova_2=query.id, id_prova_1=dipendenze[i]).delete()
            db.session.commit()
            nuova_dipendenza = DipendenzaProva(id_prova_1=query.id,
                                               id_prova_2=dipendenze[i]
                                               )
            db.session.add(nuova_dipendenza)
            db.session.commit()
        return redirect(url_for("esame_bp.lista_esame"))
    else:
        return render_template("update_prova.html", query=query, form=form, ruolo=ruolo, title="Update Prova",
                               dati_utente=dati_utente_corrente)


# funzione per cancellare una prova
def cancel(prova):
    db.session.query(Prova).filter_by(id=prova).delete()
    db.session.commit()
