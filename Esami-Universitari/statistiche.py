import json
from datetime import date

import pandas as pd
import plotly
import plotly.graph_objects as grob
from flask import Blueprint, render_template, get_flashed_messages
from flask_login import current_user, login_required
from sqlalchemy import func

from auth import set_ruolo, set_dati_utente
from models import db, Utente, VotoEsame

statistiche_bp = Blueprint("statistiche_bp", __name__)


# funzione per generare un grafico a torta delle quantità dei vari utenti in base al loro genere
def grafico_carriera():
    get_flashed_messages()
    query = db.session.query(VotoEsame).filter(VotoEsame.id_utente == Utente.get_id(current_user),
                                               VotoEsame.is_confermato == 'True').all()
    labels = []
    values = []
    if query is not None:
        for i in range(len(query)):
            labels.append(query[i].esame.nome)
            values.append(query[i].voto)

    fig = grob.Figure(data=[grob.Pie(labels=labels, values=values)])

    plot2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return plot2


def image_grafico_carriera():
    get_flashed_messages()
    query = db.session.query(VotoEsame).filter(VotoEsame.id_utente == Utente.get_id(current_user),
                                               VotoEsame.is_confermato == 'True').all()
    labels = []
    values = []
    if query is not None:
        for i in range(len(query)):
            labels.append(query[i].esame.nome)
            values.append(query[i].voto)

    fig = grob.Figure(data=[grob.Pie(labels=labels, values=values)])

    return fig


# funzione per generare un grafico a torta delle quantità dei vari utenti in base al loro genere
def grafico_torta_maschi_femmine_altro(esame):
    get_flashed_messages()
    maschi = db.session.query(VotoEsame, Utente).join(Utente).filter(Utente.sesso == 'Maschio',
                                                                     Utente.ruolo == 2,
                                                                     VotoEsame.id_esame == esame).count()
    femmine = db.session.query(VotoEsame, Utente).join(Utente).filter(Utente.sesso == 'Femmina',
                                                                      Utente.ruolo == 2,
                                                                      VotoEsame.id_esame == esame).count()
    altro = db.session.query(VotoEsame, Utente).join(Utente).filter(Utente.sesso == 'Altro',
                                                                    Utente.ruolo == 2,
                                                                    VotoEsame.id_esame == esame).count()
    labels = ['Maschio', 'Femmina', 'Altro']
    values = [maschi, femmine, altro]
    fig = grob.Figure(data=[grob.Pie(labels=labels, values=values)])

    plot2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return plot2


# funzione per generare un grafico a barre della distribuzione delle età tra i vari utenti dell'applicazione
def grafico_eta(esame):
    get_flashed_messages()
    # conta il numero di iscritti al corso
    n = db.session.query(VotoEsame.id_utente).filter_by(id_esame=esame).all()
    nuova = []
    today = date.today()
    for i in range(len(n)):
        nuova.append(n[i][0])
    count_eta = db.session.query(Utente.data_nascita, func.count(Utente.data_nascita)).filter(Utente.id.in_(nuova)). \
        group_by(Utente.data_nascita).all()
    eta = []
    quantita = []
    for row in range(len(count_eta)):
        for col in range(len(count_eta[row])):
            if col == 0:
                birthdate = count_eta[row][col]
                eta.append(today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day)))
            if col == 1:
                quantita.append(count_eta[row][col])
    dafr = pd.DataFrame({'x': eta, 'y': quantita})  # creating a sample dataframe

    data = [
        grob.Bar(
            x=dafr['x'],  # assign x as the dataframe column 'x'
            y=dafr['y']
        )
    ]

    plot1 = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return plot1


# funzione per generare un grafico a barre della distribuzione dei voti
def grafico_voti(esame):
    get_flashed_messages()
    # conta il numero di iscritti al corso
    count_voti = db.session.query(VotoEsame.voto, func.count(VotoEsame.voto)).filter(VotoEsame.id_esame == esame). \
        group_by(VotoEsame.voto).all()
    voto = []
    quantita = []
    for row in range(len(count_voti)):
        for col in range(len(count_voti[row])):
            if col == 0:
                voto.append(count_voti[row][col])
            if col == 1:
                quantita.append(count_voti[row][col])
    dafr = pd.DataFrame({'x': voto, 'y': quantita})  # creating a sample dataframe

    data = [
        grob.Bar(
            x=dafr['x'],  # assign x as the dataframe column 'x'
            y=dafr['y']
        )
    ]

    plot3 = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return plot3


@statistiche_bp.route('/statistiche/<esame>', methods=['POST', 'GET'])
@login_required
def statistiche(esame):
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = set_ruolo()
    plot1 = grafico_eta(esame)
    plot2 = grafico_torta_maschi_femmine_altro(esame)
    plot3 = grafico_voti(esame)

    return render_template('statistiche.html', plot1=plot1, plot2=plot2, plot3=plot3, ruolo=ruolo,
                           dati_utente=dati_utente_corrente)
