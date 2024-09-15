from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from models import db, init_db, Evento, Replica, Locale, Utente, Prenotazione
from settings import DATABASE_PATH
from sqlalchemy import func
from forms import RegistrationForm  # Importa il modulo del form
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SECRET_KEY'] = 'mysecretkey'

init_db(app)

# Rotta per la registrazione
@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    print("Funzione di registrazione chiamata")  # Log di debug
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Form convalidato")  # Log di debug
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_utente = Utente(
            nome=form.nome.data,
            cognome=form.cognome.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_utente)
        db.session.commit()
        flash('Account creato con successo! Ora puoi effettuare il login.', 'success')
        return redirect(url_for('login'))
    return render_template('registrazione.html', form=form)

@app.route('/')
def index():
    eventi = Evento.query.all()
    eventi_data = []
    for evento in eventi:
        repliche_data = []
        for replica in evento.rel_repliche:
            posti_prenotati = db.session.query(func.sum(Prenotazione.quantita)).filter_by(replica_id=replica.id).scalar() or 0
            posti_disponibili = evento.rel_locale.posti - posti_prenotati
            repliche_data.append({
                'id': replica.id,
                'data_ora': replica.data_ora,
                'annullato': replica.annullato,
                'posti_disponibili': posti_disponibili
            })
        eventi_data.append({
            'id': evento.id,
            'nome_evento': evento.nome_evento,
            'locale': evento.rel_locale.nome_locale,
            'repliche': repliche_data,
            'image_url': evento.image_url 
        })
    return render_template('index.html', eventi=eventi_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Utente.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = f"{user.nome} {user.cognome}"
            flash(f'Benvenuto, {session["user_name"]}! Login effettuato con successo.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login fallito. Controlla email e password.', 'danger')
    return render_template('login.html')


@app.route('/prenotazioni')
def prenotazioni():
    if 'user_id' not in session:
        flash('Per favore, effettua il login per accedere a questa pagina.', 'warning')
        return redirect(url_for('login', next=request.url))
    return render_template('prenotazioni.html')


@app.route('/api/repliche/<int:evento_id>')
def get_repliche(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    repliche = []
    for replica in evento.rel_repliche:
        posti_prenotati = db.session.query(func.sum(Prenotazione.quantita)).filter_by(replica_id=replica.id).scalar() or 0
        posti_disponibili = evento.rel_locale.posti - posti_prenotati
        repliche.append({
            'id': replica.id,
            'data_ora': replica.data_ora.strftime('%d-%m-%Y %H:%M'),
            'annullato': replica.annullato,
            'posti_disponibili': posti_disponibili
        })
    return jsonify({
        'nome_evento': evento.nome_evento,
        'locale': evento.rel_locale.nome_locale,
        'luogo': evento.rel_locale.luogo,
        'repliche': repliche
    })

@app.route('/repliche/<int:evento_id>')
def repliche(evento_id):
    if 'user_id' not in session:
        flash('Per favore, effettua il login per accedere a questa pagina.', 'warning')
        return redirect(url_for('login', next=request.url))
    return render_template('repliche.html', evento_id=evento_id)

@app.route('/prenota', methods=['POST'])
def prenota():
    if 'user_id' not in session:
        flash('Per favore, effettua il login per accedere a questa pagina.', 'warning')
        return redirect(url_for('login', next=request.url))
    data = request.json
    replica_id = data.get('replica_id')
    quantita = int(data.get('quantita', 1))
    
    replica = Replica.query.get_or_404(replica_id)
    if replica.annullato:
        return jsonify({'error': 'Questa replica è stata annullata.'}), 400
    
    prenotazione = Prenotazione(utente_id=session['user_id'], replica_id=replica_id, quantita=quantita)
    db.session.add(prenotazione)
    db.session.commit()
    
    return jsonify({'message': 'Prenotazione effettuata con successo!'}), 201


@app.route('/api/prenotazioni', methods=['GET', 'POST'])
def api_prenotazioni(): # La funzione api_prenotazioni è il gestore delle richieste per questo endpoint.
    # 1.Controllo dell'autenticazione:
    if 'user_id' not in session: # verifica se l'utente e autenticato,cioe in session, altrimenti da errore 401
        return jsonify({'error': 'Per favore, effettua il login per accedere a questa pagina.'}), 401
    #2.Gestione delle richieste GET e POST:
    if request.method == 'GET':
        return get_prenotazioni() # se la richiesta e GET riporta le prenotazioni fatte dall-utente. 
    elif request.method == 'POST': #Se è POST, chiama handle_prenotazioni_post passando i dati JSON della richiesta per gestire la creazione, l'aggiornamento o la cancellazione di una prenotazione.
        return handle_prenotazioni_post(request.json)
    
# get_prenotazioni() - Questa funzione recupera tutte le prenotazioni dell'utente corrente dal database e le restituisce come un oggetto JSON.
def get_prenotazioni(): 
    #1.Recupero delle prenotazioni
    #Recupera tutte le prenotazioni dal database filtrando per utente_id uguale all'ID dell'utente nella sessione.
    prenotazioni = Prenotazione.query.filter_by(utente_id=session['user_id']).all()
    #dettagli della riga di codice qui sopra:
    #
    
    # 2.Formattazione delle prenotazioni:
    #Formatta le prenotazioni in un elenco di dizionari contenenti informazioni utili come l'evento, il locale, la data e ora, la quantità, lo stato di annullamento e l'ID della replica.
    # vedi la spiegazione dettagliata nell-archivio spiegazione codice esame! 
    prenotazioni_data = [{
        'id': p.id,
        'evento': p.rel_replica.rel_evento.nome_evento,
        'locale': p.rel_replica.rel_evento.rel_locale.nome_locale,
        'data_ora': p.rel_replica.data_ora.strftime('%d-%m-%Y %H:%M'),
        'quantita': p.quantita,
        'annullato': p.rel_replica.annullato,
        'replica_id': p.replica_id
    } for p in prenotazioni]
    #3.Restituisce i dati delle prenotazioni come un oggetto JSON
    return jsonify(prenotazioni_data)
# quando so che devo definire una funzione? per esempio: get_prenotazioni nn sembra uno standard, ma una cosa dettata da me! 
# prenotazioni esiste o la sto svillupando adesso?
# indaga meglio: la ,p, di p.rel_replica da dove e uscita fuori?

#handle_prenotazioni_post(data) - Questa funzione gestisce le azioni POST per creare, aggiornare o cancellare una prenotazione.

def handle_prenotazioni_post(data):
    #1. Identificazione dell'azione
    ##Recupera l'azione richiesta dai dati JSON inviati con la richiesta POST.
    action = data.get('action') 
    
    #2. Gestione dell'azione:
    #In base all'azione, chiama la funzione appropriata (create_prenotazione, update_prenotazione, delete_prenotazione). Se l'azione non è valida, restituisce un errore 400 (Richiesta errata).
    if action == 'create':
        return create_prenotazione(data)
    elif action == 'update':
        return update_prenotazione(data)
    elif action == 'delete':
        return delete_prenotazione(data)
    else:
        return jsonify({'error': 'Azione non valida'}), 400

def create_prenotazione(data):
    # 1.Recupero e verifica dei dati:
    #Recupera l'ID della replica e la quantità dai dati. Verifica se l'utente ha già una prenotazione per la stessa replica, restituendo un errore se esiste.
    replica_id = data.get('replica_id')
    quantita = data.get('quantita', 1)
    
    existing_prenotazione = Prenotazione.query.filter_by(utente_id=session['user_id'], replica_id=replica_id).first()
    if existing_prenotazione:
        return jsonify({'error': 'Hai già una prenotazione per questa replica.'}), 400
    
    #2.Verifica della replica:
    #Controlla se la replica esiste e se è stata annullata, restituendo un errore se annullata
    replica = Replica.query.get_or_404(replica_id)
    if replica.annullato:
        return jsonify({'error': 'Questa replica è stata annullata.'}), 400
    
    #3.Creazione della prenotazione:
    #Crea una nuova prenotazione, la aggiunge alla sessione del database e la salva, restituendo un messaggio di successo.
    prenotazione = Prenotazione(utente_id=session['user_id'], replica_id=replica_id, quantita=quantita)
    db.session.add(prenotazione)
    db.session.commit()
    
    return jsonify({'message': 'Prenotazione effettuata con successo!'}), 201

def update_prenotazione(data):
    #1. Recupera e verifica la prenotazione
    #Recupera l'ID della prenotazione e la nuova quantità dai dati. Verifica se la prenotazione esiste e se l'utente ha i permessi per modificarla.
    prenotazione_id = data.get('prenotazione_id')
    nuova_quantita = data.get('quantita')
    prenotazione = Prenotazione.query.get_or_404(prenotazione_id)
    if prenotazione.utente_id != session['user_id']:
        return jsonify({'error': 'Non sei autorizzato a modificare questa prenotazione.'}), 403
    
    #2. Verifica della replica
    # Controlla se la replica associata è stata annullata, restituendo un errore se annullata.
    if prenotazione.rel_replica.annullato:
        return jsonify({'error': 'Questa replica è stata annullata.'}), 400
    
    #3.Aggiornamento della prenotazione:
    #Aggiorna la quantità della prenotazione e salva le modifiche nel database, restituendo un messaggio di successo.
    prenotazione.quantita = nuova_quantita
    db.session.commit()
    return jsonify({'message': 'Prenotazione aggiornata con successo!'})

    #anche la seguente funzione, ha lo stessa logica delle altre....
def delete_prenotazione(data):
    prenotazione_id = data.get('prenotazione_id')
    prenotazione = Prenotazione.query.get_or_404(prenotazione_id)
    
    if prenotazione.utente_id!= session['user_id']:
        return jsonify({'error': 'Non sei autorizzato a cancellare questa prenotazione.'}), 403
    
    db.session.delete(prenotazione)
    db.session.commit()
    
    return jsonify({'message': 'Prenotazione cancellata con successo!'})

@app.route('/logout')
def logout():
    if 'user_id' not in session:
        flash('Per favore, effettua il login per accedere a questa pagina.', 'warning')
        return redirect(url_for('login', next=request.url))
    session.clear()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
