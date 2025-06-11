# <span style="color:#2e86c1">Sito Musical Festival</span>
<span style="color:#566573">Sito per la gestione di un festival musicale, con amministrazione sia per organizzatori che per partecipanti.</span>

> 🇬🇧 For the English version, see [README.md](README.md)

## <span style="color:#27ae60">URL dopo il deploy</span>

## <span style="color:#af601a">Password Registrazione Staff</span>
Per registrarsi come membro dello staff, usa la seguente password:

`FESTIVAL`

## <span style="color:#b03a2e">Messaggi di Errore</span>
### <span style="color:#b03a2e">Login</span>
- `EMAIL_NOT_FOUND_ERROR`: L'email inserita non esiste.
- `WRONG_PASSWORD_ERROR`: La password inserita non è corretta.
- `MISSING_EMAIL_OR_PASSWORD_ERROR`: Email o password mancanti.
- `INVALID_EMAIL_ERROR`: Il formato dell'email non è valido.

### <span style="color:#b03a2e">Registrazione</span>
- `UNMATCHING_PASSWORDS_ERROR`: Le password inserite non coincidono.
- `STAFF_PASSWORD_ERROR`: La password staff non è corretta.
- `EMAIL_ALREADY_REGISTERED_ERROR`: L'email è già registrata.
- `MISSING_REQUIRED_PARAMETERS`: Parametri richiesti mancanti nella richiesta.
- `MISSING_NAME_ERROR`: Il campo nome è obbligatorio.

### <span style="color:#b03a2e">Biglietti</span>
- `NO_TICKETS_AVAILABLE`: Non ci sono biglietti disponibili per la tipologia selezionata.
- `HAS_TICKET`: L'utente ha già acquistato un biglietto.

### <span style="color:#b03a2e">Evento</span>
- `SHOW_SLOT_ALREADY_OCCUPIED`: La fascia oraria selezionata è già occupata da un altro evento pubblicato.
- `ARTIST_ALREADY_PERFORMING`: Ogni artista non può esibirsi due volte nel festival.
- `EVENT_CREATED_WITH_SUCCESS`: Evento creato con successo.
- `DATABASE_ERROR`: Si è verificato un errore durante l'elaborazione della richiesta. Riprova più tardi.
- `FILE_TYPE_NOT_ALLOWED_ERROR`: Il tipo di file caricato non è supportato.

## <span style="color:#884ea0">Test Statici</span>

### <span style="color:#884ea0">Biglietti Sold Out</span>
Nella sezione impostazioni, sotto "Sell Out Tickets", puoi esaurire tutti i biglietti rimanenti per vedere come cambia la pagina delle card dei biglietti (card grigia con messaggio "SOLD OUT").

### <span style="color:#884ea0">Imposta Password Staff</span>
Nella sezione impostazioni, sotto "Set staff password", puoi impostare una nuova password che dovrà essere inserita per registrarsi come nuovo account staff.

## <span style="color:#2471a3">Credenziali Utenti di Prova</span>

| Email                      | Password      | Tipo Utente |
|----------------------------|--------------|-------------|
| marco.rossi@gmail.com      | marcopassw   | base        |
| davide.verdi@gmail.com     | davidepassw  | base        |
| marghe.montru@gmail.com    | marghepassw  | base        |
| riccardo.ferraro@gmail.com | riccardopassw| staff       |
| samu.poli@gmail.com        | samupassw    | staff       |