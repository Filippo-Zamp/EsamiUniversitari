"""
Routes and views for the flask application.
"""
import datetime

from flask import Blueprint, render_template, get_flashed_messages, request, redirect, url_for, Response
from flask_login import login_required, current_user
from fpdf import FPDF

from auth import set_ruolo, set_dati_utente
from models import Utente, db, Prenotazione, Appello, Esame, Prova, VotoEsame
from statistiche import grafico_carriera, image_grafico_carriera


views_bp = Blueprint("views_bp", __name__)


# funzione che renderizza il template del profilo privato
# come output ritorna la pagina di login
@views_bp.route('/profilo')
@login_required
def profilo():
    get_flashed_messages()
    if current_user is not None:
        ruolo = set_ruolo()
        # query per prendere i dati dell'utente dal db
        dati_utente_corrente = set_dati_utente()

        if ruolo == 'studente':
            return render_template("profilo.html", title="Profilo studente", dati_utente=dati_utente_corrente,
                                   ruolo=ruolo)

        elif ruolo == 'docente':
            return render_template("profilo.html", title="Profilo docente", dati_utente=dati_utente_corrente,
                                   ruolo=ruolo)
    else:
        return render_template("login.html", title="Login")


# funzione che renderizza il calendario del sito
@views_bp.route('/calendar')
@login_required
def calendar():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = set_ruolo()
    prenotazioni = db.session.query(Prenotazione).filter_by(id_utente=Utente.get_id(current_user)).all()
    events = []
    if prenotazioni:
        for i in range(len(prenotazioni)):
            appellobj = db.session.query(Appello).filter_by(id=prenotazioni[i].id_appello).first()
            provaobj = db.session.query(Prova).filter_by(id=appellobj.id_prova).first()
            esameobj = db.session.query(Esame).filter_by(id=provaobj.id_esame).first()
            data = appellobj.data_ora
            datastr = appellobj.data_ora.strftime('%m/%d/%Y, alle ore %H:%M:%S')
            data_scad = appellobj.data_scad.strftime('%m/%d/%Y')
            aula = appellobj.aula
            title = provaobj.nome
            tipo = provaobj.tipo
            description = provaobj.descrizione
            peso = str(provaobj.peso)
            voto_minimo = str(provaobj.voto_minimo)
            nomesame = esameobj.nome
            cfuesame = str(esameobj.cfu)
            is_opzionale = esameobj.is_opzionale

            if is_opzionale:
                is_opzionale = "opzionale"
            else:
                is_opzionale = "è obbligatoria"

            events.append({
                'title': title,
                'start': data,
                'end': data,
                'description': "Il giorno: " + datastr + " si svolgerà la prova: " + title +
                               " nell aula: " + aula + ", sarà valida fino: " + data_scad +
                               ". La prova appartiene all esame: " + nomesame + " ed è: " + is_opzionale +
                               ". Ha un valore di: " + cfuesame + " cfu. La prova sarà di tipo: " + tipo +
                               " ed ha come descrizione: " + description + ". Avrà un peso del: " + peso +
                               "%, il voto minimo per superarla è: " + voto_minimo + "."
            },
            )

    return render_template('calendar.html', events=events, ruolo=ruolo, dati_utente=dati_utente_corrente)


@views_bp.route('/carriera', methods=['POST', 'GET'])
@login_required
def carriera():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    ruolo = set_ruolo()
    plot1 = grafico_carriera()
    query = db.session.query(VotoEsame).filter(VotoEsame.id_utente == Utente.get_id(current_user)).all()
    return render_template("carriera.html", list=query, ruolo=ruolo, plot1=plot1, title="Carriera",
                           dati_utente=dati_utente_corrente)


@views_bp.route('/lista_prenotazioni', methods=['POST', 'GET'])
@login_required
def lista_prenotazioni():
    get_flashed_messages()
    dati_utente_corrente = set_dati_utente()
    if request.method == 'POST':
        prenotazione_cancel = request.form.get('cancel')
        if prenotazione_cancel is not None:
            cancel(prenotazione_cancel)
            return redirect(url_for(".lista_prenotazioni"))
    else:
        ruolo = set_ruolo()
        query = db.session.query(Prenotazione).filter_by(id_utente=Utente.get_id(current_user)).all()
        return render_template("lista_prenotazioni.html", list=query, ruolo=ruolo, title="Lista prenotazioni",
                               dati_utente=dati_utente_corrente)


# funzione per cancellare un appello
def cancel(prenotazione):
    db.session.query(Prenotazione).filter_by(id=prenotazione).delete()
    db.session.commit()


@views_bp.route('/home_principale/', methods=['GET', 'POST'])
@login_required
def home_principale():
    ruolo = set_ruolo()
    dati_utente_corrente = set_dati_utente()
    return render_template('home.html', ruolo=ruolo, dati_utente=dati_utente_corrente)


@views_bp.route('/scarica_carriera', methods=['POST', 'GET'])
@login_required
def scarica_carriera():
    querys = db.session.query(Utente).filter_by(id=Utente.get_id(current_user)).first()
    nomes = querys.nome
    cognomes = querys.cognome
    data = str(datetime.date.today())
    nomer = 'Tiziana'
    cognomer = 'Lippiello'
    query = db.session.query(VotoEsame).filter(VotoEsame.id_utente == Utente.get_id(current_user)).all()

    class PDF(FPDF):
        def lines(self):
            self.set_fill_color(32.0, 47, 250)  # color for outer rectangle
            self.rect(5.0, 5.0, 200.0, 287.0, 'DF')
            self.set_fill_color(255, 255, 255)  # color for inner rectangle
            self.rect(8.0, 8.0, 194.0, 282.0, 'FD')

        def imagex(self):
            self.set_xy(78.0, 28.0)
            self.image(r"D:\Desktop\Esami-Universitari\static\Immagini\logo1.png", w=60.0, h=30)

        def testo(self):
            self.set_xy(0.0, 55.0)
            self.set_font('Arial', 'B', 35)
            self.set_text_color(220, 50, 50)
            self.cell(w=210.0, h=40.0, align='C', txt="Università Ca' Foscari", border=0)
            self.set_font('Arial', 'B', 20)
            self.set_text_color(17, 17, 17)
            self.set_xy(0.0, 90.0)
            self.cell(w=210.0, h=40.0, align='C', txt="Attesta", border=0)
            self.set_xy(0.0, 110.0)
            self.cell(w=210.0, h=40.0, align='C', txt="Che", border=0)
            self.set_font('Arial', 'B', 25)
            self.set_xy(0.0, 125.0)
            self.cell(w=210.0, h=40.0, align='C', txt=nomes + " " + cognomes, border=0)
            self.set_font('Arial', 'B', 20)
            self.set_xy(0.0, 150.0)
            self.cell(w=210.0, h=40.0, align='C', txt="Ha conseguito i seguenti esami", border=0)
            self.set_font('Arial', 'B', 15)
            self.set_xy(20.0, 260.0)
            self.cell(w=210.0, h=15.0, align='L', txt="Venezia, il " + data, border=0)
            self.set_xy(150.0, 260.0)
            self.cell(w=210.0, h=15.0, align='L', txt=nomer + " " + cognomer, border=0)

    pdf = PDF()
    pdf.add_page()
    pdf.lines()
    pdf.imagex()
    pdf.testo()
    pdf.add_page()
    pdf.lines()
    with pdf.table() as table:
        row = table.row()
        row.cell('Nome')
        row.cell('Anno Accademico')
        row.cell('Cfu')
        row.cell('Opzionale')
        row.cell('Voto')
        for data_row in query:
            row = table.row()
            row.cell(data_row.esame.nome)
            row.cell(data_row.esame.anno_accademico)
            row.cell(str(data_row.esame.cfu))
            row.cell(str(data_row.esame.is_opzionale))
            row.cell(str(data_row.voto))
    pdf.add_page()
    pdf.lines()
    fig = image_grafico_carriera()
    pdf.image(fig.to_image('jpg'), w=175, h=125)
    pdf.set_author('Università Ca Foscari')
    return Response(bytes(pdf.output()), mimetype='application/pdf')
