# -*- coding: utf-8 -*-
# pylint: disable=E1101
from __future__ import unicode_literals

from django.test import TestCase, Client
from .models import Reservation
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

class ReservationTests(TestCase):

    def setup(self):
        self.client = Client()
        self.assertEqual(Reservation.objects.count(), 0)

    def _create_reservation(self, data=default_data):
        return self.client.get('/create', data=data)

    def _modify_reservation(self, id, **kwargs):
        args = ["{}={}".format(k, kwargs[k]) for k in kwargs]
        kwargs_str = "&".join(args)
        return self.client.get('/{}/change?{}'.format(id, kwargs_str))

    def _get_reservation(self, id):
        return self.client.get('/{}'.format(id))

    def _get_reservation_status(self, id):
        return self.client.get('/{}/status'.format(id))

    def _get_reservation_status_string(self, id):
        return self.client.get('/{}/status'.format(id)).json()['status']

    def _delete_reservation(self, id):
        return self.client.get('/{}/delete'.format(id))

    def _change_status(self, id, status):
        return self.client.get('/{}/state/{}'.format(id, status))

    def test_object_creation(self):
        res = self._create_reservation()
        self.assertEqual(res.json()['status'], 'Upcoming reservation')
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Reservation.objects.first().firstname, "John")

    def test_object_creation_returns_your_reservation(self):
        res = self._create_reservation()
        self.assertEqual(res.json()['firstname'], 'John')
        self.assertEqual(res.json()['lastname'], 'Smith')

    def test_object_json_retrieval_by_get_request_shows_status(self):
        self._create_reservation()
        res = self._get_reservation(1)
        assert res.json()['id'] == 1
        assert res.json()['status'] == 'Upcoming reservation'

    def test_object_status_retrieval_shows_only_status(self):
        self._create_reservation()
        res = self._get_reservation_status(1)
        assert 'id' not in res.json().keys()
        assert res.json()['status'] == 'Upcoming reservation'

    def test_object_modification_by_get_request(self):
        res = self._create_reservation()
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(res.json()['firstname'], "John")
        res = self._modify_reservation(1, firstname='Fleet', guestcount=16)
        self.assertEqual(res.json()['firstname'], "Fleet")
        self.assertEqual(res.json()['guestcount'], '16')

    def test_object_deletion(self):
        self.assertEqual(Reservation.objects.count(), 0)
        res = self._create_reservation()
        self.assertEqual(Reservation.objects.count(), 1)
        self._delete_reservation(res.json()['id'])
        self.assertEqual(Reservation.objects.count(), 0)

    def test_all_fields_required_upon_reservation_creation(self):
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
        })
        assert res.json() == {
            'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."}
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'hotelname': 'The Ritz',
        })
        assert res.json() == {
            'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."}
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert res.json() == {
            'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."}
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert res.json() == {
            'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."}
        res = self._create_reservation(data={
            'firstname': 'John',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert res.json() == {
            'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."}
        res = self._create_reservation(data={
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert res.json() == {
            'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."}
        self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert Reservation.objects.count() == 1

    def test_phone_number_validated_upon_reservation_creation(self):
        data = default_data.copy()
        data['phoneno'] = '227144084408'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid phone number."}
        data['phoneno'] = 'afafaf'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid phone number."}
        data['phoneno'] = 123456789
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid phone number."}
        data['phoneno'] = 12345678901
        res = self._create_reservation(data=data)
        assert res.json()['status'] == 'Upcoming reservation'

    def test_datetime_validated_upon_reservation_creation(self):
        data = default_data.copy()
        data['datetime'] = '2018-08-08 24:12:12'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid date/time."}
        data['datetime'] = '2018-08-08 12:60:12'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid date/time."}
        data['datetime'] = '2018-08-08 12:12:60'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid date/time."}
        data['datetime'] = '2018-08-32 12:12:12'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid date/time."}
        data['datetime'] = '2018-02-29 12:12:12'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid date/time."}
        data['datetime'] = '2018-13-08 12:12:12'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter a valid date/time."}
        data['datetime'] = '2018-08-08 11:12:12'
        res = self._create_reservation(data=data)
        assert res.json()['status'] == 'Upcoming reservation'


    def test_guestcount_validated_upon_reservation_modification(self):
        data = default_data.copy()
        data['guestcount'] = 'a'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter an integer for the number of guests."}
        data['guestcount'] = '30:30'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter an integer for the number of guests."}
        data['guestcount'] = '30-30'
        res = self._create_reservation(data=data)
        assert res.json() == {
            'status': '-1', 'exception': "You must enter an integer for the number of guests."}
        data['guestcount'] = '30'
        res = self._create_reservation(data=data)
        assert res.json()['status'] == 'Upcoming reservation'


    def test_new_reservation_date_is_not_in_past(self):
        assert Reservation.objects.count() == 0
        data = default_data.copy()
        data['datetime'] = datetime.datetime.now() - datetime.timedelta(seconds=1)
        res = self._create_reservation(data)
        assert res.json() == {
            'status': '-1', 'exception': "You can't reserve a time in the past!"
        }
        assert Reservation.objects.count() == 0


    def test_modified_reservation_date_is_not_in_past(self):
        assert Reservation.objects.count() == 0
        res = self._create_reservation()
        assert Reservation.objects.count() == 1
        res = self._modify_reservation(1, datetime=datetime.datetime.now() - datetime.timedelta(seconds=1))
        assert res.json() == {
            'status': '-1', 'exception': "You can't reserve a time in the past!"
        }


    def test_save_new_reservation_with_conflicting_time_fails_gracefully_and_changes_nothing(self):
        dt = datetime.datetime.now() + datetime.timedelta(minutes=1)
        assert not Reservation.objects.count()
        sample_data = {
            'datetime': dt,
            'lastname': 'AA',
            'firstname': 'A',
            'guestcount': '5',
            'phoneno': '28282828282',
            'hotelname': 'The Mutton Glutton',
        }
        response = self._create_reservation(data=sample_data)
        assert Reservation.objects.count() == 1
        assert response.json()['firstname'] == 'A'
        response = self._create_reservation(data=sample_data)
        assert response.json() == {
            'status': '-1', 'exception': "This hotel is booked at {}.".format(dt)}
        assert Reservation.objects.count() == 1

    def test_modify_reservation_to_conflicting_time_does_not_change_either(self):
        dt_1 = datetime.datetime.now() + datetime.timedelta(minutes=1)
        dt_2 = datetime.datetime.now() + datetime.timedelta(minutes=1)
        assert not Reservation.objects.count()
        sample_data = {
            'datetime': dt_1,
            'lastname': 'AA',
            'firstname': 'A',
            'guestcount': '5',
            'phoneno': '28282828282',
            'hotelname': 'The Mutton Glutton',
        }
        res = self._create_reservation(data=sample_data)
        assert Reservation.objects.count() == 1
        assert res.json()['firstname'] == 'A'
        sample_data['datetime'] = dt_2
        sample_data['firstname'] = 'B'
        res2 = self._create_reservation(data=sample_data)
        assert Reservation.objects.count() == 2
        assert res2.json()['firstname'] == 'B'
        response = self._modify_reservation(res2.json()['id'], datetime=dt_1)
        assert response.json() == {
            'status': '-1', 'exception': "This hotel is booked at {}.".format(dt_1)}
        assert Reservation.objects.count() == 2
        assert Reservation.objects.first().datetime != Reservation.objects.last().datetime

    def test_status_lastchanged_field_set_to_now_upon_new_reservation(self):
        res = self._create_reservation()
        assert res.json()['status_last_changed_at'][:20] == \
            str(datetime.datetime.now()).replace(' ', 'T')[:20]

    def test_cannot_modify_reservation_state_without_proper_api_call(self):
        res = self._create_reservation()
        self.assertEqual(res.json()['status'], 'Upcoming reservation')
        res = self._modify_reservation(1, status=1)
        self.assertEqual(res.json()['status'], 'Upcoming reservation')
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=1)):
            res = self._change_status(1, 1)
            self.assertEqual(res.json()['status'], 'Guest is here')
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=2)):
            res = self._change_status(1, 2)
            self.assertEqual(res.json()['status'], 'Guest has left')

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
        assert res.json()['status'] == 'Upcoming reservation'
        data = default_data.copy()
        data['hotelname'] = 'Another hotel'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(seconds=30)):
            # Can't change reservation's status yet
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            res = self._change_status(1, 1)
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            # Create second reservation -- Can't change its status yet
            res2 = self._create_reservation(data)
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
            res2 = self._change_status(2, 1)
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=1)):
            # We can change the first reservation's status now.
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            res = self._change_status(1, 1)
            assert self._get_reservation_status_string(1) == 'Guest is here'
            # However, only 30 seconds have passed for the second, so we can't change it.
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
            res2 = self._change_status(2, 1)
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=1, seconds=30)):
            # We can't change the first reservation's status now.
            assert self._get_reservation_status_string(1) == 'Guest is here'
            res = self._change_status(1, 2)
            assert self._get_reservation_status_string(1) == 'Guest is here'
            # But we can change the second one.
            assert self._get_reservation_status_string(2) == 'Upcoming reservation'
            res2 = self._change_status(2, 1)
            assert self._get_reservation_status_string(2) == 'Guest is here'
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=2)):
            # We can change the first one again.
            assert self._get_reservation_status_string(1) == 'Guest is here'
            res = self._change_status(1, 2)
            assert self._get_reservation_status_string(1) == 'Guest has left'
            # But not the second.
            assert self._get_reservation_status_string(2) == 'Guest is here'
            res2 = self._change_status(2, 1)
            assert self._get_reservation_status_string(2) == 'Guest is here'

    def test_update_state_to_same_value_does_not_reset_rate_limit(self):
        res = self._create_reservation()
        assert res.json()['status'] == 'Upcoming reservation'
        old_last_changed = res.json()['status_last_changed_at']
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=1)):
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            self._change_status(1, 0)
            assert self._get_reservation_status_string(1) == 'Upcoming reservation'
            assert str(Reservation.objects.first().status_last_changed_at)[:20] == old_last_changed.replace('T',' ')[:20]
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=2)):
            res = self._change_status(1, 1)
            assert self._get_reservation_status_string(1) == 'Guest is here'
            new_last_changed = res.json()['status_last_changed_at']
            assert new_last_changed != old_last_changed
            old_last_changed = new_last_changed
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=3)):
            assert self._get_reservation_status_string(1) == 'Guest is here'
            self._change_status(1, 1)
            assert self._get_reservation_status_string(1) == 'Guest is here'
            assert str(Reservation.objects.first().status_last_changed_at)[:20] == old_last_changed.replace('T',' ')[:20]
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=4)):
            res = self._change_status(1, 2)
            assert self._get_reservation_status_string(1) == 'Guest has left'
            new_last_changed = res.json()['status_last_changed_at']
            assert new_last_changed != old_last_changed
            old_last_changed = new_last_changed
        with freezegun.freeze_time(datetime.datetime.now() + datetime.timedelta(minutes=5)):
            assert self._get_reservation_status_string(1) == 'Guest has left'
            self._change_status(1, 2)
            assert self._get_reservation_status_string(1) == 'Guest has left'
            assert str(Reservation.objects.first().status_last_changed_at)[:20] == old_last_changed.replace('T',' ')[:20]
