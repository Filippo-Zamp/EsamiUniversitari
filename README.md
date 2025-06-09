# 📚 Gestione di Esami Universitari

Web Application sviluppata per il corso di **Basi di Dati** presso l’Università Ca’ Foscari Venezia, A.A. 2022/2023.  
Permette la gestione completa degli esami universitari per studenti, docenti e amministratori.

## 👥 Team

- **Obeng Takyi Samuel** – 881431  
- **Singh Baljinder** – 880134  
- **Zampiron Filippo** – 887208  
- **Professore**: Stefano Calzavara

---

## 🚀 Tecnologie utilizzate

- **Python**, **Flask** (v2.3.2)
- **Flask-SQLAlchemy** (v3.0.5)
- **PostgreSQL**
- **Bootstrap**, **WTForms**, **Flask-Login**
- **Pandas**, **Plotly**, **FullCalendar**, **FPDF2**

---

## 🔧 Avvio del Progetto

1. Clonare il progetto:
   ```bash
   git clone https://github.com/SinghBaljinder/Esami-Universitari
    ```
2. Installare i pacchetti:
   ```bash
   pip install -r requirements.txt
    ```
3. Avviare il progetto in PyCharm o tramite:
   ```bash
   flask run
    ```
## 🧩 Funzionalità principali

- Registrazione e login (studenti/docenti)
- Gestione esami, prove, appelli (docenti)
- Prenotazioni, voti e carriera (studenti)
- Ruoli personalizzati: admin, docente, studente
- Calendario prenotazioni (FullCalendar)
- Statistiche per esami (Plotly)
- Scarica carriera in PDF

## 🛠️ Database

- Progettazione concettuale e logica
- Implementazione con PostgreSQL
- Uso di: Trigger, Check, Indici, Ruoli e permessi

## 📊 Statistiche disponibili

- Distribuzione studenti per età, genere, voto
- Visualizzazione interattiva con Plotly
- Esportazione report carriera in PDF

## 📁 Struttura del progetto
```
Esami-Universitari/
├── app/                 # Codice applicativo Flask
│   ├── templates/       # HTML e interfaccia
│   ├── static/          # CSS, JS, immagini
│   ├── models.py        # Modelli SQLAlchemy
│   └── routes.py        # Routing Flask
├── docs/                # Documentazione
├── requirements.txt     # Librerie Python
└── README.md            # Questo file
```

## 🧠 Contributo

- Ogni membro del team ha contribuito a:
- Analisi e progettazione del DB
- Sviluppo delle funzionalità front-end e back-end
- Stesura della documentazione e testing

- 
