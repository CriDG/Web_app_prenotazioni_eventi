
import os
from settings import BASE_DIR
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import json

db = SQLAlchemy()

#Le relazioni tra le tabelle vengono definite usando db.relationship e db.ForeignKey. Questo è il modo in cui SQLAlchemy (l'ORM utilizzato) stabilisce le connessioni tra le diverse tabelle.
#
class Locale(db.Model, SerializerMixin):
    __tablename__ = 'locali'
    id = db.Column(db.Integer, primary_key=True)  
    nome_locale = db.Column(db.String(50), nullable=False)  
    luogo = db.Column(db.String(100), nullable=False)  
    posti = db.Column(db.Integer, nullable=False)  
   
    #
    rel_eventi = db.relationship('Evento', back_populates='rel_locale', lazy=True)
    serialize_rules = ('-rel_eventi.rel_locale',)


class Evento(db.Model, SerializerMixin):
    __tablename__ = 'eventi'
    id = db.Column(db.Integer, primary_key=True)  
    locale_id = db.Column(db.Integer, db.ForeignKey('locali.id'), nullable=False) # FK indica che ogni evento e associato a un locae spcifico!
    nome_evento = db.Column(db.String(50), nullable=False)  
    image_url = db.Column(db.String(255), nullable=True)

    rel_locale = db.relationship('Locale', back_populates='rel_eventi', lazy=True)
    rel_repliche = db.relationship('Replica', back_populates='rel_evento', lazy=True)
    serialize_rules = ('-rel_locale.rel_eventi', '-rel_repliche.rel_evento')


class Replica(db.Model, SerializerMixin):
    __tablename__ = 'repliche'
    id = db.Column(db.Integer, primary_key=True) 
    evento_id = db.Column(db.Integer, db.ForeignKey('eventi.id'), nullable=False)  
    data_ora = db.Column(db.DateTime, nullable=False) 
    annullato = db.Column(db.Boolean, default=False)  

    rel_evento = db.relationship('Evento', back_populates='rel_repliche', lazy=True)
    rel_prenotazioni = db.relationship('Prenotazione', back_populates='rel_replica', lazy=True)
    serialize_rules = ('-rel_evento.rel_repliche', '-rel_prenotazioni.rel_replica')


class Utente(db.Model, SerializerMixin):
    __tablename__ = 'utenti'
    id = db.Column(db.Integer, primary_key=True) 
    cognome = db.Column(db.String(50), nullable=False)  
    nome = db.Column(db.String(50), nullable=False)  
    telefono = db.Column(db.String(20))  
    email = db.Column(db.String(100), nullable=False, unique=True)  
    password = db.Column(db.String(30), nullable=False) 
   
    rel_prenotazioni = db.relationship('Prenotazione', back_populates='rel_utente', lazy=True)
    serialize_rules = ('-rel_prenotazioni.rel_utente',)


class Prenotazione(db.Model, SerializerMixin):
    __tablename__ = 'prenotazioni'
    id = db.Column(db.Integer, primary_key=True)  
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)  
    replica_id = db.Column(db.Integer, db.ForeignKey('repliche.id'), nullable=False)  
    quantita = db.Column(db.Integer, nullable=False)  

    rel_utente = db.relationship('Utente', back_populates='rel_prenotazioni', lazy=True)
    rel_replica = db.relationship('Replica', back_populates='rel_prenotazioni', lazy=True)
    serialize_rules = ('-rel_utente.rel_prenotazioni', '-rel_replica.rel_prenotazioni')

def converti_datetime(dt_string):
    day, month, year, time = dt_string.split('-')
    hour, minute, second = time.split(':')
    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))


def init_db(app):
    db.init_app(app)
    with app.app_context():
       
        db.create_all()

        if Utente.query.first() is None:
            json_files = [
                ('utenti.json', Utente),
                ('prenotazioni.json', Prenotazione),
                ('repliche.json', Replica),
                ('eventi.json', Evento),
                ('locali.json', Locale),
            ]

            for filename, model in json_files:
                file_path = os.path.join(BASE_DIR, 'database', 'data_json', filename)
                with open(file_path, 'r') as file:
                    lista_record = json.load(file)
                    
                for record_dict in lista_record:
                    if 'data_ora' in record_dict:
                        record_dict['data_ora'] = converti_datetime(record_dict['data_ora'])
                    new_record = model(**record_dict)
                    db.session.add(new_record)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()