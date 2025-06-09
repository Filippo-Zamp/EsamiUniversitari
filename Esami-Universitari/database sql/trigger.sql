CREATE OR REPLACE FUNCTION prenotazione_data_fun() returns trigger as $prenotazione_data$
	BEGIN
		IF NEW.Data >= (Select data_ora
					  From appello
					  Where id=NEW.id_appello)
			THEN RETURN NULL;
		END IF;
		RETURN NEW;
	END;
$prenotazione_data$ LANGUAGE plpgsql;

CREATE TRIGGER prenotazione_data
BEFORE INSERT OR UPDATE ON prenotazione
FOR EACH ROW
EXECUTE FUNCTION prenotazione_data_fun();


CREATE OR REPLACE FUNCTION appello_data_fun() returns trigger as $appello_data$
	BEGIN
		IF NEW.data_ora > (Select MAX(prenotazione.data)
					  		From prenotazione
					  		Where id_appello=NEW.id)
			THEN RETURN NULL;
		END IF;
		RETURN NEW;
	END;
$appello_data$ LANGUAGE plpgsql;

CREATE TRIGGER appello_data
BEFORE INSERT OR UPDATE ON appello
FOR EACH ROW
EXECUTE FUNCTION appello_data_fun();

CREATE OR REPLACE FUNCTION voto_appello_fun() returns trigger as $voto_appello$
	BEGIN
		IF NEW.is_confermato AND NEW.voto<(Select voto_minimo
					  				From prova JOIN appello ON appello.id_prova=prova.id
					  				Where appello.id=NEW.id_appello)
			THEN RETURN NULL;
		END IF;
		RETURN NEW;
	END;
$voto_appello$ LANGUAGE plpgsql;

CREATE TRIGGER appello_data
BEFORE INSERT OR UPDATE ON voto_appello
FOR EACH ROW
EXECUTE FUNCTION voto_appello_fun();

CREATE OR REPLACE FUNCTION prova_voto_minimo_fun() returns trigger as $prova_voto_minimo$
	BEGIN
		IF NEW.voto_minimo >(Select MAX(voto)
					  			From voto_appello JOIN appello ON voto_appello.id_appello=appello.id
					  			Where appello.id_prova=NEW.id AND voto_appello.is_confermato)
			THEN RETURN NULL;
		END IF;
		RETURN NEW;
	END;
$prova_voto_minimo$ LANGUAGE plpgsql;

CREATE TRIGGER prova_voto_minimo
BEFORE INSERT OR UPDATE ON prova
FOR EACH ROW
EXECUTE FUNCTION prova_voto_minimo_fun();