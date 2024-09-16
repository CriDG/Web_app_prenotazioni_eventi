// P1 Fetch//
//1. Attendere il caricamento del DOM
document.addEventListener('DOMContentLoaded', init);
//Descrizione: Questo codice registra un listener per l'evento DOMContentLoaded sul documento. L'evento DOMContentLoaded viene emesso quando il documento HTML è stato completamente caricato e analizzato, ma prima che tutte le risorse esterne (come immagini, fogli di stile, ecc.) siano state caricate.
//Funzione: Quando questo evento si verifica, viene chiamata la funzione init.

//2. Inizializzazione
function init() {
    fetchPrenotazioni();
}
//Descrizione: La funzione init viene eseguita quando l'evento DOMContentLoaded si verifica.
//Funzione: All'interno di questa funzione, viene chiamata fetchPrenotazioni, che avvia il processo di recupero delle prenotazioni.

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
//Descrizione: Questa funzione utilizza la funzione fetch per effettuare una richiesta GET all'endpoint /api/prenotazioni.
//Funzione:fetch restituisce una Promise che risolve la risposta della richiesta.
//response.json() converte la risposta della richiesta in un oggetto JSON.
//Se la conversione ha successo, il risultato viene passato alla funzione displayPrenotazioni.
//Se si verifica un errore durante la richiesta o la conversione, viene chiamata la funzione handleError.

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
//Descrizione: Questa funzione prende un array di prenotazioni (prenotazioni) come argomento e visualizza queste prenotazioni in una tabella all'interno di un contenitore HTML con l'id prenotazioni-container.
//Condizione: Se l'array prenotazioni è vuoto:
                //Viene visualizzato un messaggio che informa l'utente che non ci sono prenotazioni.
//Condizione: Se ci sono prenotazioni:
            //Viene generata una tabella HTML con le seguenti intestazioni: Evento, Locale, Data e Ora, Quantità, Stato, Azioni.
//Ogni prenotazione viene trasformata in una riga della tabella utilizzando la funzione createPrenotazioneRow.
//Le righe della tabella vengono concatenate (.join('')) e inserite nel corpo della tabella (<tbody>).

//5 5. Creazione delle righe della tabella
//3. creare-prenotazioni 
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
//Descrizione: Questa funzione prende una singola prenotazione come argomento e restituisce una stringa HTML che rappresenta una riga della tabella per quella prenotazione.
//Funzione: La riga contiene i dati della prenotazione e dei pulsanti per modificarla e cancellarla.
            //Se la prenotazione è annullata, il campo quantità è disabilitato e non ci sono pulsanti di modifica e cancellazione.
            //Altrimenti, ci sono pulsanti per modificare e cancellare la prenotazione.


//6.Gestione degli errori! 

//4.Gestione Errori! 
function handleError(error) {
    console.error('Error:', error);
    document.getElementById('prenotazioni-container').innerHTML = '<p>Si è verificato un errore nel caricamento delle prenotazioni.</p>';
}

//7. Modifica delle prenotazioni!  
                                        //NB:VAI PIU IN PROFFONDO QUESTA PARTE!!! 
//a. gestione delle evento di modifica! 
//Descrizione: Questa funzione viene chiamata quando si clicca sul pulsante "Modifica".
//Funzione: Recupera la nuova quantità dal campo di input e chiama updatePrenotazione per aggiornare la prenotazione.

//5.ModificaP
function modificaPrenotazione(prenotazioneId) {
    const nuovaQuantita = document.getElementById(`quantita-${prenotazioneId}`).value;
    updatePrenotazione(prenotazioneId, nuovaQuantita)
        .then(handleUpdateResponse)
        .catch(handleUpdateError);
}

//b. aggiornamento della prenotazione 
//Descrizione: Questa funzione invia una richiesta POST per aggiornare la prenotazione.
//Funzione:
        //Invia un oggetto JSON contenente l'azione (update), l'ID della prenotazione e la nuova quantità.
        //Converte la risposta in un oggetto JSON.

//6.Aggiorna P 
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


//c.Gestione della risposta di aggiornamento
//Descrizione: Queste funzioni gestiscono la risposta alla richiesta di aggiornamento.
//Funzione:
           //handleUpdateResponse visualizza un messaggio di successo o di errore.
            //handleUpdateError visualizza un messaggio di errore e stampa l'errore nella console.
//7.A Gestione Aggiornamento risposta! 
function handleUpdateResponse(data) {
    if (data.message) {
        alert(data.message);
        fetchPrenotazioni(); // Usa fetchPrenotazioni per aggiornare le prenotazioni
    } else if (data.error) {
        alert(data.error);
    }
}

//chat mi legga la parte sotto di handleupdaterror con quella sopra
//7.

function handleUpdateError(error) {
    console.error('Error:', error);
    alert('Si è verificato un errore durante la modifica della prenotazione.');
}


//8. Cancellazione delle prenotazioni
//a. Gestione dell'evento di cancellazione
    //Descrizione: Questa funzione viene chiamata quando si clicca sul pulsante "Cancella".
    //Funzione: Chiede conferma all'utente e, se confermato, chiama deletePrenotazione per cancellare la prenotazione.
function cancellaPrenotazione(prenotazioneId) {
    if (confirm('Sei sicuro di voler cancellare questa prenotazione?')) {
        deletePrenotazione(prenotazioneId)
            .then(handleDeleteResponse)
            .catch(handleDeleteError);
    }
}

//b. Cancellazione della prenotazione
//Descrizione: Questa funzione invia una richiesta POST per cancellare la prenotazione.
//Funzione:
        //Invia un oggetto JSON contenente l'azione (delete) e l'ID della prenotazione.
        //Converte la risposta in un oggetto JSON.

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



//C.gestione della risposta di cancellazione
//Descrizione: Queste funzioni gestiscono la risposta alla richiesta di cancellazione.
 //Funzione:
            //handleDeleteResponse visualizza un messaggio di successo o di errore.
            //handleDeleteError visualizza un messaggio di errore e stampa l'errore nella console.
function handleDeleteResponse(data) {
    if (data.message) {
        alert(data.message);
        fetchPrenotazioni(); // Usa fetchPrenotazioni per aggiornare le prenotazioni
    } else if (data.error) {
        alert(data.error);
    }
}

function handleDeleteError(error) {
    console.error('Error:', error);
    alert('Si è verificato un errore durante la cancellazione della prenotazione.');
}

