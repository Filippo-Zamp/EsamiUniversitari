from flask import Blueprint, render_template, request, redirect, url_for, get_flashed_messages
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import InputRequired, Length

from auth import set_dati_utente, set_ruolo
from appello import TestForm
from models import db, Utente, DipendenzaProva, Prenotazione, VotoAppello, Appello, VotoEsame
from flask_login import current_user, login_required

voto_bp = Blueprint("voto_bp", __name__)

# costanti utili
RUOLI = ["admin", "docente", "studente"]


@voto_bp.route('/inserisci_voto/<appello>', methods=['POST', 'GET'])
@login_required
def inserisci_voto(appello):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    appello_inserisci = request.form.get('inserisci')
    ruolo = set_ruolo()
    if appello_inserisci is not None:
        voto = request.form.get('voto')
        nuovo_subscrib = VotoAppello(id_appello=appello,
                                     id_utente=appello_inserisci,
                                     voto=voto,
                                     is_confermato=0
                                     )
        db.session.add(nuovo_subscrib)
        db.session.commit()
        subscription = db.session.query(Prenotazione.id_utente).filter_by(id_appello=appello).all()
        appello1 = db.session.query(Appello.id).filter_by(id=appello).first()
        listsub = []
        form = {}
        for i in range(len(subscription)):
            utente = db.session.query(Utente).filter(Utente.id.in_(subscription[i])).first()
            query = db.session.query(VotoAppello).filter_by(id_appello=appello, id_utente=utente.id).first()
            if query is None:
                listsub.append(utente)
                form[utente.id] = TestForm(formdata=None)
        subscription_count = len(subscription)
        return render_template("iscrizioni_lista_appello.html", list=listsub, form=form, count=subscription_count,
                               appello=appello1.id, ruolo=ruolo, dati_utente=dati_utente_corrente)


@voto_bp.route('/voti_appelli', methods=['POST', 'GET'])
@login_required
def voti_appelli():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = None
    if current_user is not None:
        ruolo = RUOLI[Utente.get_role(current_user)]
    if request.method == 'POST':
        conferma = request.form.get('conferma')
        if conferma is not None:
            db.session.query(VotoAppello).filter(VotoAppello.id == conferma). \
                update({'is_confermato': 1})
            db.session.commit()

            voto_appello = db.session.query(VotoAppello).filter(VotoAppello.id == conferma).first()
            dipendenze = []
            dipendenze_prove([voto_appello.appello.id_prova], dipendenze)
            query = db.session.query(VotoAppello).join(Appello, Appello.id == VotoAppello.id_appello).filter \
                (Appello.id_prova.in_(dipendenze), VotoAppello.id_utente == Utente.get_id(current_user),
                 VotoAppello.is_confermato).all()
            somma = 0
            voto_finale = 0
            for i in range(len(query)):
                voto_finale += (query[i].voto * query[i].appello.prova.peso)
                somma += query[i].appello.prova.peso
            if somma == 100:
                voto_finale = voto_finale / somma
                nuovo_voto_esame = VotoEsame(id_esame=voto_appello.appello.prova.id_esame,
                                             id_utente=Utente.get_id(current_user),
                                             voto=voto_finale,
                                             is_confermato=0
                                             )
                db.session.add(nuovo_voto_esame)
                db.session.commit()
            return redirect(url_for('.voti_appelli'))
    else:
        if current_user is not None:
            ruolo = RUOLI[Utente.get_role(current_user)]
        query = db.session.query(VotoAppello).filter(VotoAppello.id_utente == Utente.get_id(current_user),
                                                     VotoAppello.is_confermato == 'False').all()
        return render_template("voti_appelli.html", list=query, ruolo=ruolo, title="Voti Appelli",
                               dati_utente=dati_utente_corrente)


@voto_bp.route('/bacheca_esiti', methods=['POST', 'GET'])
@login_required
def bacheca_esiti():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = None
    if current_user is not None:
        ruolo = RUOLI[Utente.get_role(current_user)]
    if request.method == 'POST':
        conferma = request.form.get('conferma')

        if conferma is not None:
            db.session.query(VotoEsame).filter(VotoEsame.id == conferma).update({'is_confermato': 1})
            db.session.commit()

            return redirect(url_for('.bacheca_esiti'))
    else:
        if current_user is not None:
            ruolo = RUOLI[Utente.get_role(current_user)]
        query = db.session.query(VotoEsame).filter(VotoEsame.id_utente == Utente.get_id(current_user),
                                                   VotoEsame.is_confermato == 'False').all()
        return render_template("bacheca_esiti.html", list=query, ruolo=ruolo, title="Bacheca Esiti",
                               dati_utente=dati_utente_corrente)


def dipendenze_prove(prove, result):
    result.extend(prove)
    id_prove = db.session.query(DipendenzaProva.id_prova_2).filter(DipendenzaProva.id_prova_1.in_(prove)).all()
    if len(id_prove) != 0:
        dipendenze_prove(id_prove[0], result)
