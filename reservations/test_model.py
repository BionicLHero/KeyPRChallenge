# -*- coding: utf-8 -*-
# pylint: disable=E1101
from __future__ import unicode_literals

from django.test import TestCase
from .models import Reservation
from rest_framework.test import APIClient, APIRequestFactory
from .views import ReservationModelViewSet
import datetime
import freezegun

default_data = {
    'firstname': 'John',
    'lastname': 'Smith',
    'phoneno': '17144084408',
    'datetime': '2020-08-08 11:12:12',
    'guestcount': 2,
    'hotelname': 'The Ritz',
}

class ReservationViewTests(TestCase):

    def setup(self):
        self.client = APIClient()
        self.assertEqual(Reservation.objects.count(), 0)

    def _create_reservation(self, data=default_data):
        return self.client.post('/', data=data, follow=True)

    def _modify_reservation(self, id, **kwargs):
        req = APIRequestFactory().patch('/', kwargs)
        view = ReservationModelViewSet.as_view({'patch': 'partial_update'})
        res = view(req, pk=id)
        res.render()
        return res

    def _get_reservation(self, id):
        return self.client.get('/{}'.format(id), follow=True)

    def _get_reservation_status_string(self, id):
        return self._get_reservation(id).data['status']

    def _change_status(self, id):
        return self.client.post('/{}/status-change'.format(id), follow=True)

    def test_status_lastchanged_field_set_to_now_upon_new_reservation(self):
        res = self._create_reservation()
        assert str(Reservation.objects.first().status_last_changed_at)[:20] == \
            str(datetime.datetime.now())[:20]

    def test_cannot_modify_reservation_state_without_proper_api_call(self):
        res = self._create_reservation()
        self.assertEqual(res.data['status'], 'Upcoming reservation')
        res = self._modify_reservation(1, status=1)
        self.assertEqual(res.data['status'], 'Upcoming reservation')
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=1)):
            res = self._change_status(1)
            self.assertEqual(res.data['status'], 'Guest is here')
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=2)):
            res = self._change_status(1)
            self.assertEqual(res.data['status'], 'Guest has left')

    def test_two_people_can_have_reservations_with_same_time_but_different_hotels(self):
        assert Reservation.objects.count() == 0
        data = default_data.copy()
        self._create_reservation(data)
        assert Reservation.objects.count() == 1
        data['hotelname'] = 'The Haggard Flagon'
        self._create_reservation(data)
        assert Reservation.objects.count() == 2

    def test_state_only_changes_once_per_minute_per_reservation(self):
        res = self._create_reservation()
        assert self._get_reservation_status_string(1) == 'Upcoming reservation'
        data = default_data.copy()
        data['hotelname'] = 'Another hotel'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(seconds=30)):
            # Can't change reservation's status yet
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            res = self._change_status(1)
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            # Create second reservation -- Can't change its status yet
            res2 = self._create_reservation(data)
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
            res2 = self._change_status(2)
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=1)):
            # We can change the first reservation's status now.
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            res = self._change_status(1)
            assert self._get_reservation_status_string(1) == 'Guest is here'
            # However, only 30 seconds have passed for the second, so we can't change it.
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
            res2 = self._change_status(2)
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=1, seconds=30)):
            # We can't change the first reservation's status now.
            assert self._get_reservation_status_string(1) == 'Guest is here'
            res = self._change_status(1)
            assert self._get_reservation_status_string(1) == 'Guest is here'
            # But we can change the second one.
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
            res2 = self._change_status(2)
            assert self._get_reservation_status_string(2) == 'Guest is here'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=2)):
            # We can change the first one again.
            assert self._get_reservation_status_string(1) == 'Guest is here'
            res = self._change_status(1)
            assert self._get_reservation_status_string(1) == 'Guest has left'
            # But not the second.
            assert self._get_reservation_status_string(2) == 'Guest is here'
            res2 = self._change_status(2)
            assert self._get_reservation_status_string(2) == 'Guest is here'
