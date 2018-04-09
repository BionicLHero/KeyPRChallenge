# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
import datetime
import pytz
import dateutil.parser

def rate_limit(func):
    def wrapped(obj):
        cutoff = obj.status_last_changed_at + \
            datetime.timedelta(
                seconds=Reservation.rate_limit_for_state_change_seconds)
        if (datetime.datetime.now() < cutoff):
            return False
        if func(obj) == True:
            obj.status_last_changed_at = datetime.datetime.now()
            obj.save(update_fields=['status_last_changed_at'])
    return wrapped

class Reservation(models.Model):
    objects = models.Manager()

    STATUS_UPCOMING = "Upcoming reservation"
    STATUS_GUEST_IS_HERE = "Guest is here"
    STATUS_GUEST_HAS_LEFT = "Guest has left"
    STATUS_GUEST_MISSED = "Guest missed reservation"

    firstname = models.CharField(max_length=15)
    lastname = models.CharField(max_length=15)
    phoneno = models.IntegerField()
    datetime = models.DateTimeField()
    guestcount = models.SmallIntegerField()
    hotelname = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default=STATUS_UPCOMING)
    status_last_changed_at = models.DateTimeField(auto_now_add=True)
    occasion = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('datetime', 'hotelname')

    rate_limit_for_state_change_seconds = 60

    @staticmethod
    def validate(args):
        ''' Returns: (bool is_valid, str err) '''
        try:
            if 'datetime' in args:
                date = dateutil.parser.parse(str(args['datetime']))
                if date < datetime.datetime.now():
                    return False, "You can't reserve a time in the past!"
        except Exception as e:
            return False, "You must enter a valid date/time."

        if 'guestcount' in args:
            try:
                gc = int(args['guestcount'])
            except Exception as e:
                return False, "You must enter an integer for the number of guests."
        
        if 'phoneno' in args:
            try:
                if len(str(args['phoneno'])) != 11:
                    raise Exception()
                ph = int(args['phoneno'])
            except Exception as e:
                return False, "You must enter a valid phone number."
                
        return True, None

    @rate_limit
    def change_state_upcoming(self):
        if self.status == self.STATUS_UPCOMING:
            return False
        self.status = self.STATUS_UPCOMING
        self.save(update_fields=['status'])
        return True

    @rate_limit
    def change_state_guest_left(self):
        if self.status == self.STATUS_GUEST_HAS_LEFT:
            return False
        self.status = self.STATUS_GUEST_HAS_LEFT
        self.save(update_fields=['status'])
        return True
    
    @rate_limit
    def change_state_guest_arrived(self):
        if self.status == self.STATUS_GUEST_IS_HERE:
            return False
        self.status = self.STATUS_GUEST_IS_HERE
        self.save(update_fields=['status'])
        return True

    @rate_limit
    def change_state_guest_missed(self):
        if self.status == self.STATUS_GUEST_MISSED:
            return False
        self.status = self.STATUS_GUEST_MISSED
        self.save(update_fields=['status'])
        return True
