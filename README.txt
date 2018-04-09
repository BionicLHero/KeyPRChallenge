You can use this API to create, read, update, and delete hotel reservation information,
all from GET requests to your browser.

This project's data storage is in a sqlite3 file, attached with this project.

In the Usage section: All URLs are relative URLs from localhost.
Example (modifying reservation): localhost:8000/3/change?firstname=Jacob

You may have to run `./manage.py migrate` when setting up the project.

Testing:
    `$ ./manage.py test`
    Or, if you have pytest installed (I do),
    `$ py.test -sv`

Usage:

    View all reservations:
        `/`
        The reservations are modifiable through their IDs.

    Create reservation:
        `/create?{{ PARAMETERS }}`
        Where PARAMETERS is a querystring, with these required parameters:
        firstname (string)
        lastname (string)
        phoneno (11-digit number)
        datetime (in format YYYY-MM-DDThh:mm, example: 2019-01-01T08:30)
        guestcount (int)
        hotelname (string)
        
    Modify reservation:
        `/{{ id }}/change?{{ param }}={{ value }}&{{ paramb }}={{ valueb }}...`

    Get reservation information:
        `/{{ id }}`

    Get reservation status:
        `/{{ id }}/status`

    Delete reservation:
        `/{{ id }}/delete`

    Change status:
        `/{{ id }}/state/{{ status }}`
        Where status is an int between 0 and 3.
            0. Upcoming reservation,
            1. Guest is here,
            2. Guest has left,
            3. Guest missed reservation.