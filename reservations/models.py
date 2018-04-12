# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager
import datetime
import pytz
import dateutil.parser

# def rate_limit(func):
#     def wrapped(obj, state):
#         cutoff = obj.status_last_changed_at + \
#             datetime.timedelta(
#                 seconds=Reservation.rate_limit_for_state_change_seconds)
#         if (datetime.datetime.now() < cutoff):
#             return False
#         if func(obj, state) == True:
#             obj.status_last_changed_at = datetime.datetime.now()
#             obj.save(update_fields=['status_last_changed_at'])
#     return wrapped

class ReservationManager(BaseUserManager):
    def create_reservation(self, firstname, lastname, phoneno, datetime, guestcount, hotelname):
        reservation = self.model(
            firstname=firstname,
            lastname=lastname,
            phoneno=phoneno,
            datetime=datetime,
            guestcount=guestcount,
            hotelname=hotelname
        )
        # request_dict = request.GET.dict()
        # for i in request_dict.keys():
        #     if i in settings.FIELDS_TO_IGNORE:
        #         continue
        #     new_reservation[i] = request_dict[i]

        # if any(n not in new_reservation.keys() for n in ['firstname', 'lastname', 'datetime', 'hotelname', 'guestcount', 'phoneno']):
        #     return JsonResponse({'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."})

        # is_valid, err = Reservation.validate(new_reservation)
        # if not is_valid:
        #     return JsonResponse({'status': '-1', 'exception': err})
        if self.filter(hotelname=hotelname, datetime=datetime).count() > 0:
            return None
            # return JsonResponse({'status': '-1', 'exception': "This hotel is booked at {}.".format(new_reservation['datetime'])})
        reservation.save()
        return reservation
        # Reservation.objects.create(**new_reservation)
        # return ReservationJsonResponse(Reservation.objects.get(**new_reservation))


class Reservation(models.Model):
    objects = ReservationManager()

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

    rate_limit_for_state_change_seconds = 60

    def get_full_name(self):
        return self.firstname + ' ' + self.lastname

    def get_short_name(self):
        return self.firstname + ' ' + self.lastname

    def __str__(self):
        return self.firstname + ' ' + self.lastname

#     @staticmethod
#     def validate(args):
#         ''' Returns: (bool is_valid, str err) '''
#         try:
#             if 'datetime' in args:
#                 date = dateutil.parser.parse(str(args['datetime']))
#                 if date < datetime.datetime.now():
#                     return False, "You can't reserve a time in the past!"
#         except Exception as e:
#             return False, "You must enter a valid date/time."
#
#         if 'guestcount' in args:
#             try:
#                 gc = int(args['guestcount'])
#             except Exception as e:
#                 return False, "You must enter an integer for the number of guests."
#
#         if 'phoneno' in args:
#             try:
#                 if len(str(args['phoneno'])) != 11:
#                     raise Exception()
#                 ph = int(args['phoneno'])
#             except Exception as e:
#                 return False, "You must enter a valid phone number."
#
#         return True, None
#
#     @rate_limit
#     def change_state(self, state):
#         # VALIDATE STATE AS INT
#         # ADD TEST FOR VALID STATE
#         if state > len(self.STATUSES): return False
#         str_state = self.STATUSES[state]
#         if self.status == str_state: return False
#         self.status = str_state
#         self.save(update_fields=['status'])
#         return True
