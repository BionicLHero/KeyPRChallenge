# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager
import datetime
import pytz
import dateutil.parser


# REALLY wanting to put this into a larger class. If I was working with more
# classes than just Reservation, I'd make a larger validator net.
def validate_reservation(kwargs):
    ''' Returns: (bool is_valid, dict errors) '''
    is_valid = True
    errors = {}
    errors['datetime'] = []
    try:
        date = dateutil.parser.parse(str(kwargs['datetime']).replace('T',' '))
        if date < datetime.datetime.now():
            is_valid = False
            errors['datetime'].append("You can't reserve a time in the past!")
    except Exception as e:
        is_valid = False
        errors['datetime'].append("You must enter a valid date/time.")

    errors['phoneno'] = []
    try:
        ph = int(kwargs['phoneno'])
        if len(str(kwargs['phoneno'])) not in [10, 11]:
            is_valid = False
            errors['phoneno'].append("You must enter a valid phone number.")
    except Exception as e:
        is_valid = False
        errors['phoneno'].append("You must enter a valid phone number.")

    return is_valid, errors


class Reservation(models.Model):
    objects = models.Manager()

    STATUS_UPCOMING = "Upcoming reservation"
    STATUS_GUEST_IS_HERE = "Guest is here"
    STATUS_GUEST_HAS_LEFT = "Guest has left"
    STATUSES = [STATUS_UPCOMING, STATUS_GUEST_IS_HERE, STATUS_GUEST_HAS_LEFT]

    REQUIRED_FIELDS = ['firstname','lastname','phoneno','datetime','guestcount']

    firstname = models.CharField(max_length=15)
    lastname = models.CharField(max_length=15)
    phoneno = models.IntegerField()
    datetime = models.DateTimeField()
    guestcount = models.SmallIntegerField()
    hotelname = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default=STATUS_UPCOMING)
    status_last_changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('datetime', 'hotelname')

    rate_limit_for_status_change_seconds = 60

    def get_full_name(self):
        return self.firstname + ' ' + self.lastname

    def get_short_name(self):
        return self.firstname + ' ' + self.lastname

    def __str__(self):
        return self.firstname + ' ' + self.lastname

    def change_status(self):
        status = self.STATUSES.index(self.status)
        status += 1
        if status == len(self.STATUSES): status = 0
        self.status = self.STATUSES[status]
        self.save(update_fields=['status'])
