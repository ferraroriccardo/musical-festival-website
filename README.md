# <span style="color:#2e86c1">Musical Festival Website</span>
<span style="color:#566573">Website for managing a music festival, allowing administration of both organizers and attendees.</span>

> 🇮🇹 Per la versione italiana, vedi [README_it.md](README_it.md)

## <span style="color:#27ae60">URL after deployment</span>

## <span style="color:#af601a">Staff Registration Password</span>
To sign up as a staff member, use the following password:

`FESTIVAL`

## <span style="color:#b03a2e">Error Messages</span>
### <span style="color:#b03a2e">Login</span>
- `EMAIL_NOT_FOUND_ERROR`: The provided email does not exist.
- `WRONG_PASSWORD_ERROR`: The password entered is incorrect.
- `MISSING_EMAIL_OR_PASSWORD_ERROR`: Email or password is missing.
- `INVALID_EMAIL_ERROR`: The email format is invalid.

### <span style="color:#b03a2e">Signup</span>
- `UNMATCHING_PASSWORDS_ERROR`: The passwords entered do not match.
- `STAFF_PASSWORD_ERROR`: The staff password is incorrect.
- `EMAIL_ALREADY_REGISTERED_ERROR`: The email is already registered.
- `MISSING_REQUIRED_PARAMETERS`: Required parameters are missing from the request.

### <span style="color:#b03a2e">Event</span>
- `NO_TICKETS_AVAILABLE`: No tickets are available for the selected type.
- `SHOW_SLOT_ALREADY_OCCUPIED`: The selected event slot is already occupied by another published event.
- `ARTIST_ALREADY_PERFORMING`: The selected artist is already performing in another event at this time.
- `EVENT_CREATED_WITH_SUCCESS`: The event was created successfully.
- `DATABASE_ERROR`: An error occurred while processing your request. Please try again later.

## <span style="color:#884ea0">Static Tests</span>

### <span style="color:#884ea0">Sold Out Tickets</span>
In the settings section, under "Sell Out Tickets", you can mark all remaining tickets as sold out to preview how the ticket cards page changes (greyed-out card with a "SOLD OUT" message).

### <span style="color:#884ea0">Set Staff Password</span>
In the settings section, under "Set staff password", you can set a new password which must be submitted when signing up as a new staff account.

## <span style="color:#2471a3">Test User Credentials</span>

| Email                    | Password      | User Type |
|--------------------------|--------------|-----------|
| marco.rossi@gmail.com    | marcopassw   | basic     |
| davide.verdi@gmail.com   | davidepassw  | basic     |
| marghe.montru@gmail.com  | marghepassw  | basic     |
| riccardo.ferraro@gmail.com | riccardopassw | staff   |
| samu.poli@gmail.com      | samupassw    | staff     |