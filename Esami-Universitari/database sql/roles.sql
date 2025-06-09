DROP OWNED BY studente;
DROP ROLE IF EXISTS studente;
DROP OWNED BY docente;
DROP ROLE IF EXISTS docente;
DROP OWNED BY admin;
DROP ROLE IF EXISTS admin;

CREATE ROLE studente WITH LOGIN PASSWORD 'studente';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO studente;
GRANT INSERT ON TABLE prenotazione TO studente;

GRANT UPDATE ON TABLE voto_appello TO studente;
GRANT UPDATE ON TABLE prenotazione TO studente;

GRANT DELETE ON TABLE prenotazione TO studente;



CREATE ROLE docente WITH LOGIN PASSWORD 'docente';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO docente;

GRANT INSERT ON TABLE esame TO docente;
GRANT INSERT ON TABLE prova TO docente;
GRANT INSERT ON TABLE dipendenza_prova TO docente;
GRANT INSERT ON TABLE appello TO docente;
GRANT INSERT ON TABLE voto_appello TO docente;
GRANT INSERT ON TABLE voto_esame TO docente;

GRANT UPDATE ON TABLE esame TO docente;
GRANT UPDATE ON TABLE prova TO docente;
GRANT UPDATE ON TABLE dipendenza_prova TO docente;
GRANT UPDATE ON TABLE appello TO docente;
GRANT UPDATE ON TABLE voto_appello TO docente;
GRANT UPDATE ON TABLE voto_esame TO docente;

GRANT DELETE ON TABLE esame TO docente;
GRANT DELETE ON TABLE prova TO docente;
GRANT DELETE ON TABLE dipendenza_prova TO docente;
GRANT DELETE ON TABLE appello TO docente;
GRANT DELETE ON TABLE voto_appello TO docente;
GRANT DELETE ON TABLE voto_esame TO docente;



CREATE ROLE admin WITH LOGIN PASSWORD 'admin' SUPERUSER;
GRANT ALL ON SCHEMA public TO admin;
