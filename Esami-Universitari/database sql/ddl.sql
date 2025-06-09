DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

CREATE TABLE utente
(
 id				serial,
 email				varchar(50) NOT NULL,
 nome				varchar(50) NOT NULL,
 cognome			varchar(50) NOT NULL,
 data_nascita			date NOT NULL,
 sesso				varchar(50) NOT NULL,
 ruolo				int NOT NULL,
 password			varchar(200) NOT NULL,
 telefono			varchar(11) NOT NULL,
 altri_contatti			varchar(999) NULL,
 CONSTRAINT utente_pk PRIMARY KEY ( id)
);


CREATE TABLE Esame
(
 id				 serial,
 nome				 varchar(50) NOT NULL,
 anno_accademico 		 varchar(50) NOT NULL,
 cfu				 int NOT NULL,
 is_opzionale 			 bool NOT NULL,
 id_utente			 integer NOT NULL,
 UNIQUE(nome, anno_accademico),
 CONSTRAINT esame_pk PRIMARY KEY (id),
 CONSTRAINT id_utente_fk FOREIGN KEY ( id_utente) REFERENCES utente( id) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE Prova
(
 id				serial,
 nome				varchar(50) NOT NULL,
 tipo				varchar(50) NOT NULL,
 descrizione			varchar(999) NULL,
 id_esame			integer NOT NULL,
 peso				int NOT NULL,
 id_utente 			integer NOT NULL,
 voto_minimo			int NOT NULL,
 CONSTRAINT prova_pk  PRIMARY KEY (id),
 CONSTRAINT id_esame_fk FOREIGN KEY ( id_esame) REFERENCES Esame ( id ) ON UPDATE CASCADE ON DELETE CASCADE,
 CONSTRAINT id_utente_fk FOREIGN KEY ( id_utente) REFERENCES utente( id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE dipendenza_prova
(
 id				serial,
 id_prova_1 			integer NOT NULL,
 id_prova_2 			integer NOT NULL,
 CONSTRAINT dipendenza_prova_pk PRIMARY KEY ( id ),
 CONSTRAINT id_prova_1_fk FOREIGN KEY ( id_prova_1) REFERENCES prova ( id) ON UPDATE CASCADE ON DELETE CASCADE,
 CONSTRAINT id_prova_2_fk FOREIGN KEY ( id_prova_2 ) REFERENCES prova ( id ) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX dipendenza_prova_id_prova_1_idx ON dipendenza_prova
(
 id_prova_1
);

CREATE INDEX dipendenza_prova_id_prova_2_idx ON dipendenza_prova
(
 id_prova_2
);

CREATE TABLE appello
(
 id				serial,
 id_prova  			integer NOT NULL,
 data_ora			timestamp NOT NULL,
 data_scad			date NOT NULL,
 aula				varchar(50) NOT NULL,
 CONSTRAINT appello_pk PRIMARY KEY ( id ),
 CONSTRAINT id_prova_fk FOREIGN KEY ( id_prova) REFERENCES prova( id) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE voto_appello
(
 id				serial,
 id_appello			integer NOT NULL,
 id_utente			integer NOT NULL,
 voto				int NOT NULL,
 is_confermato			bool NOT NULL,
 CONSTRAINT voto_appello_uc UNIQUE (id_appello,id_utente),
 CONSTRAINT voto_appello_pk PRIMARY KEY ( id),
 CONSTRAINT id_appello_fk FOREIGN KEY ( id_appello) REFERENCES appello( id) ON UPDATE CASCADE ON DELETE CASCADE,
 CONSTRAINT id_utente_fk FOREIGN KEY ( id_utente) REFERENCES utente( id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX voto_appello_id_appello_idx ON voto_appello
(
 id_appello
);

CREATE INDEX voto_appello_id_utente_idx ON voto_appello
(
 id_utente
);


CREATE TABLE voto_esame
(
 id				serial,
 id_esame			integer NOT NULL,
 id_utente 			integer NOT NULL,
 voto				int NOT NULL,
 is_confermato 			bool NOT NULL,
 CONSTRAINT voto_esame_uc UNIQUE (id_esame,id_utente),
 CONSTRAINT voto_esame_pk PRIMARY KEY ( id),
 CONSTRAINT id_esame_fk FOREIGN KEY ( id_esame ) REFERENCES esame( id)ON UPDATE CASCADE ON DELETE CASCADE,
 CONSTRAINT id_utente_fk FOREIGN KEY ( id_utente) REFERENCES utente( id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX voto_esame_id_esame_idx ON voto_esame
(
 id_esame
);

CREATE INDEX voto_esame_id_utente_idx ON voto_esame
(
 id_utente
);

CREATE TABLE prenotazione
(
 id				serial,
 id_appello			integer NOT NULL,
 id_utente			integer NOT NULL,
 data				date NOT NULL,
 CONSTRAINT prenotazione_uc UNIQUE (id_appello,id_utente),
 CONSTRAINT prenotazione_pk PRIMARY KEY ( id),
 CONSTRAINT id_appello_fk FOREIGN KEY ( id_appello) REFERENCES appello( id) ON UPDATE CASCADE ON DELETE CASCADE,
 CONSTRAINT id_utente_fk FOREIGN KEY ( id_utente) REFERENCES utente( id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX prenotazione_id_appello_idx ON prenotazione
(
 id_appello
);

CREATE INDEX prenotazione_id_utente_idx ON prenotazione
(
 id_utente
);



