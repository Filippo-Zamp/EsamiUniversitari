from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm
from auth import set_ruolo, set_dati_utente
from models import db, Esame, Utente, engine_docente
from sqlalchemy.sql.expression import select
from flask_login import current_user, login_required

esame_bp = Blueprint("esame_bp", __name__)


# classe wtforms per creare form in modo veloce
# Form Per creazione esame
class EsameForm(FlaskForm):
    nome = StringField('Nome del Esame', validators=[InputRequired(), Length(max=50)])
    anno_accademico = StringField('Anno Accademico', validators=[InputRequired(), Length(max=50)])
    cfu = IntegerField('CFU', validators=[InputRequired(), Length(max=2)])
    is_opzionale = SelectField('Opzionale', validators=[InputRequired()], choices=['Si', 'No'])


# Funzione che ci permette di creare un nuovo esame
@esame_bp.route('/creazione_esame', methods=['GET', 'POST'])
@login_required
def creazione_esame():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = set_ruolo()
    form = EsameForm()
    # prendo il contenuto del form di registrazione
    # generato in html dalla classe qui sopra
    if request.method == 'POST':
        nome = form.nome.data
        anno_accademico = form.anno_accademico.data
        cfu = form.cfu.data
        is_opzionale = form.is_opzionale.data
        if is_opzionale == 'Si':
            is_opzionale = True
        else:
            is_opzionale = False
        esame_gia_esiste = False
        with engine_docente.connect().execution_options(isolation_level="READ COMMITTED") as conn:
            list_esame = conn.execute(select(Esame.nome))
        for row in list_esame:
            if row[0] == nome and esame_gia_esiste is False:
                esame_gia_esiste = True
        if esame_gia_esiste:
            flash("Esiste già un esame con questo nome! Cambiare nome, grazie.")
        else:
            nuovo_esame = Esame(nome=nome,
                                anno_accademico=anno_accademico,
                                cfu=cfu,
                                is_opzionale=is_opzionale,
                                id_utente=Utente.get_id(current_user)
                                )

            db.session.add(nuovo_esame)
            db.session.commit()

            return redirect(url_for('esame_bp.lista_esame'))

    return render_template('creazione_esame.html', form=form, title='Creazione Esame', ruolo=ruolo,
                           dati_utente=dati_utente_corrente)


# funzione utile a visualizzare una lista degli esami
@esame_bp.route('/lista_esame', methods=['POST', 'GET'])
@login_required
def lista_esame():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()

    if request.method == 'POST':
        esame_update = request.form.get('update')
        esame_cancel = request.form.get('cancel')
        esame_create_prova = request.form.get('createprova')
        esame_lista_prova = request.form.get('listaprova')
        esame_statistiche = request.form.get('statistiche')

        if esame_update is not None:
            return redirect(url_for('.update', esame=esame_update))
        elif esame_create_prova is not None:
            return redirect(url_for('prova_bp.creazione_prova', esame=esame_create_prova))
        elif esame_cancel is not None:
            cancel(esame_cancel)
            return redirect(url_for(".lista_esame"))
        elif esame_lista_prova is not None:
            return redirect(url_for('prova_bp.lista_prova', esame=esame_lista_prova))
        elif esame_statistiche is not None:
            return redirect(url_for('statistiche_bp.statistiche', esame=esame_statistiche))
    else:
        ruolo = set_ruolo()
        query = db.session.query(Esame).all()
        return render_template("lista_esame.html", list=query, ruolo=ruolo, title="Lista Esami",
                               dati_utente=dati_utente_corrente)


# funzione di modifica esame
@esame_bp.route('/update/<esame>', methods=['POST', 'GET'])
@login_required
def update(esame):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    query = db.session.query(Esame).filter_by(id=esame).first()
    ruolo = set_ruolo()

    class EsameForm1(FlaskForm):
        nome = StringField('Nome del Esame', default=query.nome, validators=[InputRequired(), Length(max=50)])
        anno_accademico = StringField('Anno Accademico', default=query.anno_accademico, validators=[InputRequired(),
                                                                                                    Length(max=50)])
        cfu = IntegerField('CFU', default=query.cfu, validators=[InputRequired(), Length(max=2)])
        is_opzionale = SelectField('Opzionale', default=query.is_opzionale, validators=[InputRequired()],
                                   choices=['Si', 'No'])

    form = EsameForm1()
    if request.method == 'POST':
        nome = request.form.get('nome')
        anno_accademico = request.form.get('anno_accademico')
        cfu = request.form.get('cfu')
        is_opzionale = request.form.get('is_opzionale')
        if is_opzionale == 'Si':
            is_opzionale = True
        else:
            is_opzionale = False

        db.session.query(Esame).filter(Esame.id == query.id). \
            update({'id': query.id, 'nome': nome, 'anno_accademico': anno_accademico,
                    'cfu': cfu, 'is_opzionale': is_opzionale, 'id_utente': query.id_utente})
        db.session.commit()
        return redirect(url_for(".lista_esame"))
    else:
        return render_template("update_esame.html", query=query, form=form, ruolo=ruolo, title="Update Esame",
                               dati_utente=dati_utente_corrente)


# funzione per cancellare un esame
def cancel(esame):
    db.session.query(Esame).filter_by(id=esame).delete()
    db.session.commit()
