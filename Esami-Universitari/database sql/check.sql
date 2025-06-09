ALTER TABLE appello
ADD CHECK (data_scad>data_ora);

ALTER TABLE appello
ADD CHECK (data_ora>CURRENT_DATE);

ALTER TABLE prova
ADD CHECK (peso>=0 AND peso <=100);

ALTER TABLE prova
ADD CHECK (voto_minimo>=0 AND voto_minimo <=18);

ALTER TABLE voto_appello
ADD CHECK (voto>=0 AND voto <=30);

ALTER TABLE voto_esame
ADD CHECK (voto>=18 AND voto <=30);

ALTER TABLE utente
ADD CHECK ((CURRENT_DATE-data_nascita)>=18);