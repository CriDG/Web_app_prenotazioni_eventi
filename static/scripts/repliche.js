document.addEventListener('DOMContentLoaded', initRepliche);

function initRepliche() {
    const eventoId = document.getElementById('repliche-container').dataset.eventoId;
    loadRepliche(eventoId);
}

function loadRepliche(eventoId) {
    fetch(`/api/repliche/${eventoId}`)
        .then(response => response.json())
        .then(displayRepliche)
        .catch(error => console.error('Error:', error));
}

function displayRepliche(data) {
    const container = document.getElementById('repliche-container');
    container.innerHTML = `
        <h1 class="mb-4">Repliche di "${data.nome_evento}"</h1>
        <h2 class="mb-3">${data.locale}</h2>
        <p><strong>Luogo:</strong> ${data.luogo}</p>
        <div class="row">
            ${data.repliche.map(createReplicaCard).join('')}
        </div>
    `;
}

function createReplicaCard(replica) {
    return `
        <div class="col-md-4 mb-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${replica.data_ora}</h5>
                    <p class="card-text">Posti disponibili: ${replica.posti_disponibili}</p>
                    ${replica.annullato 
                        ? '<p class="text-danger">Questa replica è stata annullata.</p>'
                        : `
                            <form onsubmit="prenota(event, ${replica.id})">
                                <div class="mb-3">
                                    <label for="quantita-${replica.id}" class="form-label">Quantità:</label>
                                    <input type="number" class="form-control" id="quantita-${replica.id}" name="quantita" value="1" min="1" max="${replica.posti_disponibili}">
                                </div>
                                <button type="submit" class="btn btn-dark">Prenota</button>
                            </form>
                        `
                    }
                </div>
            </div>
        </div>
    `;
}

function prenota(event, replicaId) {
    event.preventDefault();
    const quantita = document.getElementById(`quantita-${replicaId}`).value;

    createPrenotazione(replicaId, quantita)
        .then(handlePrenotazioneResponse)
        .catch(handlePrenotazioneError);
}

function createPrenotazione(replicaId, quantita) {
    return fetch('/api/prenotazioni', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'create',
            replica_id: replicaId,
            quantita: parseInt(quantita)
        }),
    }).then(response => response.json());
}

function handlePrenotazioneResponse(data) {
    if (data.message) {
        alert(data.message);
        const eventoId = document.getElementById('repliche-container').dataset.eventoId;
        loadRepliche(eventoId);
    } else if (data.error) {
        alert(data.error);
    }
}

function handlePrenotazioneError(error) {
    console.error('Error:', error);
    alert('Si è verificato un errore durante la prenotazione.');
}

