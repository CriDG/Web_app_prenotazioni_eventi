from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from models import db, init_db, Evento, Replica, Locale, Utente, Prenotazione
from settings import DATABASE_PATH
from sqlalchemy import func
from forms import RegistrationForm  
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SECRET_KEY'] = 'mysecretkey'

init_db(app)


@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    print("Funzione di registrazione chiamata")  
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Form convalidato") 
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
def api_prenotazioni():
    if 'user_id' not in session:
        return jsonify({'error': 'Per favore, effettua il login per accedere a questa pagina.'}), 401
    if request.method == 'GET':
        return get_prenotazioni()  
    elif request.method == 'POST': 
        return handle_prenotazioni_post(request.json)
    

def get_prenotazioni(): 
    prenotazioni = Prenotazione.query.filter_by(utente_id=session['user_id']).all()
    prenotazioni_data = [{
        'id': p.id,
        'evento': p.rel_replica.rel_evento.nome_evento,
        'locale': p.rel_replica.rel_evento.rel_locale.nome_locale,
        'data_ora': p.rel_replica.data_ora.strftime('%d-%m-%Y %H:%M'),
        'quantita': p.quantita,
        'annullato': p.rel_replica.annullato,
        'replica_id': p.replica_id
    } for p in prenotazioni]
    return jsonify(prenotazioni_data)


def handle_prenotazioni_post(data):
    action = data.get('action') 
    if action == 'create':
        return create_prenotazione(data)
    elif action == 'update':
        return update_prenotazione(data)
    elif action == 'delete':
        return delete_prenotazione(data)
    else:
        return jsonify({'error': 'Azione non valida'}), 400

def create_prenotazione(data):
    replica_id = data.get('replica_id')
    quantita = data.get('quantita', 1)
    
    existing_prenotazione = Prenotazione.query.filter_by(utente_id=session['user_id'], replica_id=replica_id).first()
    if existing_prenotazione:
        return jsonify({'error': 'Hai già una prenotazione per questa replica.'}), 400
    replica = Replica.query.get_or_404(replica_id)
    if replica.annullato:
        return jsonify({'error': 'Questa replica è stata annullata.'}), 400
    prenotazione = Prenotazione(utente_id=session['user_id'], replica_id=replica_id, quantita=quantita)
    db.session.add(prenotazione)
    db.session.commit()
    return jsonify({'message': 'Prenotazione effettuata con successo!'}), 201

def update_prenotazione(data):
    prenotazione_id = data.get('prenotazione_id')
    nuova_quantita = data.get('quantita')
    prenotazione = Prenotazione.query.get_or_404(prenotazione_id)
    if prenotazione.utente_id != session['user_id']:
        return jsonify({'error': 'Non sei autorizzato a modificare questa prenotazione.'}), 403
    if prenotazione.rel_replica.annullato:
        return jsonify({'error': 'Questa replica è stata annullata.'}), 400
    
    prenotazione.quantita = nuova_quantita
    db.session.commit()
    return jsonify({'message': 'Prenotazione aggiornata con successo!'})

   
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
