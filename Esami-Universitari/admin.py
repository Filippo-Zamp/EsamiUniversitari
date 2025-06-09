from flask import Blueprint, render_template, request, redirect, url_for, get_flashed_messages
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import select, update

from auth import set_ruolo, set_dati_utente
from models import Utente, engine_admin


admin_bp = Blueprint("admin_bp", __name__)


# funzione che renderizza la pagina principale dell'admin una volta effettuato il login
@admin_bp.route('/amministrazione')
@login_required
def amministrazione():
    get_flashed_messages()
    ruolo = None
    dati_utente_corrente = None
    if current_user is not None:
        # ricava dal database il codice del ruolo (da 0 a 2), che diventa l'indice dell'array dei ruoli
        ruolo = set_ruolo()
        dati_utente_corrente = set_dati_utente()

    return render_template("amministrazione.html", title="Amministrazione", dati_utente=dati_utente_corrente,
                           ruolo=ruolo)


# funzione che permette all'admin di cambiare il ruolo di un utente (es. trasformare uno studente in docente)
def modifica_valori(id_passato):
    nome_radio_button = id_passato + "_radio"
    v = request.form[nome_radio_button]
    with engine_admin.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
        if v == "docente":
            d = update(Utente).where(Utente.id == id_passato, Utente.ruolo != 1).values({"ruolo": 1})
            conn.execute(d)
            conn.commit()
            return redirect(url_for('admin_bp.lista_utente'))
        elif v == "studente":
            s = update(Utente).where(Utente.id == id_passato, Utente.ruolo != 2).values({"ruolo": 2})
            conn.execute(s)
            conn.commit()
            return redirect(url_for('admin_bp.lista_utente'))
    return redirect(url_for('admin_bp.lista_utente'))


# funzione che restituisce una lista rispettivamente per docenti e studenti all'admin
@admin_bp.route('/lista_utente', methods=['GET', 'POST'])
@login_required
def lista_utente():
    get_flashed_messages()
    ruolo = set_ruolo()
    with engine_admin.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
        s = select(Utente.id, Utente.email, Utente.nome, Utente.cognome, Utente.telefono, Utente.ruolo).where\
            (Utente.ruolo == '2').order_by(Utente.ruolo)
        d = select(Utente.id, Utente.email, Utente.nome, Utente.cognome, Utente.telefono, Utente.ruolo).filter\
            (Utente.ruolo == '1').order_by(Utente.ruolo)
        lista_studenti = conn.execute(s)
        lista_docenti = conn.execute(d)

    if 'modificavalori' in request.form and request.form['modificavalori'] == "Modifica permessi":
        id_passato = request.form['id_passato']
        modifica_valori(id_passato)

    if 'modificavalori2' in request.form and request.form['modificavalori2'] == "Modifica permessi":
        id_passato2 = request.form['id_passato2']
        modifica_valori(id_passato2)

    return render_template("lista_utenti.html", ruolo=ruolo, lista_studenti=lista_studenti, lista_docenti=lista_docenti)
