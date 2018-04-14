You can use this REST API to create, read, update, and delete hotel reservation
information.

This project's data storage is in a sqlite3 file, attached with this project.

In the Usage section: All URLs are relative URLs from localhost.
Example (changing status): localhost:8000/3/status-change

You may have to run `./manage.py migrate` when setting up the project.

Testing:
    `$ ./manage.py test`
    Or, if you have pytest installed (I do),
    `$ py.test -sv`

Usage:

    View all reservations:
        `GET /`
        The reservations are modifiable through their IDs.

    Create reservation:
        `POST /` (data=PARAMETERS)
        Where PARAMETERS is a dict, with these REQUIRED parameters:
        firstname: (string)
        lastname: (string)
        phoneno: (10-digit or 11-digit number)
        datetime: (in format YYYY-MM-DDThh:mm, example: 2019-01-01T08:30)
        guestcount: (int)
        hotelname: (string)

    Get reservation information:
        `GET /{{ id }}`

    Modify reservation:
        `PATCH /{{ id }}` (data=PARAMETERS)
        Where PARAMETERS is a dict, with these OPTIONAL parameters:
        firstname: (string)
        lastname: (string)
        phoneno: (10-digit or 11-digit number)
        datetime: (in format YYYY-MM-DDThh:mm, example: 2019-01-01T08:30)
        guestcount: (int)
        hotelname: (string)

    Delete reservation:
        `DELETE /{{ id }}`

    Check status:
        `GET /{{ id }}/status-change`

    Change status:
        `POST /{{ id }}/status-change`
        This can only be called once every minute per reservation.
