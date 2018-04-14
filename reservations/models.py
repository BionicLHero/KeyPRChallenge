# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
import pytz
import dateutil.parser


class Reservation(models.Model):
    objects = models.Manager()

    STATUS_UPCOMING = "Upcoming reservation"
    STATUS_GUEST_IS_HERE = "Guest is here"
    STATUS_GUEST_HAS_LEFT = "Guest has left"
    STATUSES = [STATUS_UPCOMING, STATUS_GUEST_IS_HERE, STATUS_GUEST_HAS_LEFT]

    REQUIRED_FIELDS = ['firstname','lastname','phoneno','datetime','guestcount']

    firstname = models.CharField(max_length=15)
    lastname = models.CharField(max_length=15)
    phoneno = models.IntegerField(validators = [MinValueValidator(1111111111), MaxValueValidator(99999999999)])
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
