# <span style="color:#2e86c1">Music Festival Website</span>
<span style="color:#566573">Website for managing a music festival, with administration for both organizers and participants.</span>

> 🇮🇹 Per la versione italiana, vedi [README_it.md](README_it.md)

## <span style="color:#27ae60">Deployed URL</span>
[https://ferraroriccardo.pythonanywhere.com/](https://ferraroriccardo.pythonanywhere.com/)

## <span style="color:#af601a">Staff Registration Password</span>
To register as a staff member, use the following password:

`FESTIVAL!1`

## <span style="color:#2471a3">Test User Credentials</span>

| Email                      | Password       | User Type | Ticket                   |
|----------------------------|---------------|-----------|--------------------------|
| marco.rossi@gmail.com      | marcopassw    | basic     | Sun 22nd                 |
| davide.verdi@gmail.com     | davidepassw   | basic     | Sat 21st - Sun 22nd      |
| alice.blu@gmail.com        | alicepassw    | basic     | 3 days                   |
| matteo.bianchi@gmail.com   | matteopassw   | basic     | -                        |
| riccardo.ferraro@gmail.com | riccardopassw | staff     | -                        |
| marghe.montru@gmail.com    | marghepassw   | staff     | -                        |

## <span style="color:#b03a2e">Error Messages</span>
### <span style="color:#b03a2e">Login</span>
- `EMAIL_NOT_FOUND_ERROR`: The entered email does not exist.
- `WRONG_PASSWORD_ERROR`: The entered password is incorrect.
- `MISSING_EMAIL_OR_PASSWORD_ERROR`: Email or password missing.
- `INVALID_EMAIL_ERROR`: The email format is invalid.

### <span style="color:#b03a2e">Registration</span>
- `UNMATCHING_PASSWORDS_ERROR`: The entered passwords do not match.
- `STAFF_PASSWORD_ERROR`: The staff password is incorrect.
- `EMAIL_ALREADY_REGISTERED_ERROR`: The email is already registered.
- `MISSING_REQUIRED_PARAMETERS`: Required parameters are missing in the request.
- `MISSING_NAME_ERROR`: The name field is required.

### <span style="color:#b03a2e">Tickets</span>
- `NO_TICKETS_AVAILABLE`: No tickets available for the selected type.
- `HAS_TICKET`: The user has already purchased a ticket.

### <span style="color:#b03a2e">Event</span>
- `SHOW_SLOT_ALREADY_OCCUPIED`: The selected time slot is already occupied by another published event.
- `ARTIST_ALREADY_PERFORMING`: Each artist can only perform once at the festival.
- `EVENT_CREATED_WITH_SUCCESS`: Event created successfully.
- `DATABASE_ERROR`: An error occurred while processing the request. Please try again later.
- `FILE_TYPE_NOT_ALLOWED_ERROR`: The uploaded file type is not supported.

