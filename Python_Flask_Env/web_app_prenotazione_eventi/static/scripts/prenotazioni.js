
//1. Attendere il caricamento del DOM
document.addEventListener('DOMContentLoaded', init);


//2. Inizializzazione
function init() {
    fetchPrenotazioni();
}


//3. Recupero delle prenotazioni
function fetchPrenotazioni() {
    fetch('/api/prenotazioni')
    .then(response => {
        if (!response.ok) {
            throw new Error('Errore nel recupero delle prenotazioni');
        }
        return response.json();
    })
    .then(displayPrenotazioni)
    .catch(handleError);
}


//4. Visualizzazione delle prenotazioni
//2. Gestione-Prenotazioni! 
function displayPrenotazioni(prenotazioni) {
    const container = document.getElementById('prenotazioni-container');
    if (prenotazioni.length === 0) {
        container.innerHTML = '<p>Non hai ancora effettuato prenotazioni.</p>';
    } else {
        const rows = prenotazioni.map(createPrenotazioneRow).join('');
        container.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Evento</th>
                        <th>Locale</th>
                        <th>Data e Ora</th>
                        <th>Quantità</th>
                        <th>Stato</th>
                        <th>Azioni</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    }
}


//5 5. Creazione delle righe della tabella

function createPrenotazioneRow(p) {
    return `
        <tr>
            <td>${p.evento}</td>
            <td>${p.locale}</td>
            <td>${p.data_ora}</td>
            <td>
                <input type="number" min="1" value="${p.quantita}" id="quantita-${p.id}" ${p.annullato ? 'disabled' : ''}>
            </td>
            <td>${p.annullato ? '<span class="text-danger">Annullato</span>' : '<span class="text-success">Confermato</span>'}</td>
            <td>
                ${p.annullato ? '' : `
                    <button onclick="modificaPrenotazione(${p.id})" class="btn btn-sm btn-primary">Modifica</button>
                    <button onclick="cancellaPrenotazione(${p.id})" class="btn btn-sm btn-danger">Cancella</button>
                `}
            </td>
        </tr>
    `;
}


//6.Gestione degli errori! 

function handleError(error) {
    console.error('Error:', error);
    document.getElementById('prenotazioni-container').innerHTML = '<p>Si è verificato un errore nel caricamento delle prenotazioni.</p>';
}

//7. Modifica delle prenotazioni!  
                                    
function modificaPrenotazione(prenotazioneId) {
    const nuovaQuantita = document.getElementById(`quantita-${prenotazioneId}`).value;
    updatePrenotazione(prenotazioneId, nuovaQuantita)
        .then(handleUpdateResponse)
        .catch(handleUpdateError);
}

function updatePrenotazione(prenotazioneId, nuovaQuantita) {
    return fetch('/api/prenotazioni', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'update',
            prenotazione_id: prenotazioneId,
            quantita: nuovaQuantita
        }),
    }).then(response => {
        if (!response.ok) {
            throw new Error('Errore durante l\'aggiornamento della prenotazione');
        }
        return response.json();
    });
}


//7.A Gestione Aggiornamento risposta! 
function handleUpdateResponse(data) {
    if (data.message) {
        alert(data.message);
        fetchPrenotazioni(); 
    } else if (data.error) {
        alert(data.error);
    }
}

function handleUpdateError(error) {
    console.error('Error:', error);
    alert('Si è verificato un errore durante la modifica della prenotazione.');
}


//8. Cancellazione delle prenotazioni
function cancellaPrenotazione(prenotazioneId) {
    if (confirm('Sei sicuro di voler cancellare questa prenotazione?')) {
        deletePrenotazione(prenotazioneId)
            .then(handleDeleteResponse)
            .catch(handleDeleteError);
    }
}


function deletePrenotazione(prenotazioneId) {
    return fetch('/api/prenotazioni', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'delete',
            prenotazione_id: prenotazioneId
        }),
    }).then(response => {
        if (!response.ok) {
            throw new Error('Errore durante la cancellazione della prenotazione');
        }
        return response.json();
    });
}

function handleDeleteResponse(data) {
    if (data.message) {
        alert(data.message);
        fetchPrenotazioni();
    } else if (data.error) {
        alert(data.error);
    }
}

function handleDeleteError(error) {
    console.error('Error:', error);
    alert('Si è verificato un errore durante la cancellazione della prenotazione.');
}

