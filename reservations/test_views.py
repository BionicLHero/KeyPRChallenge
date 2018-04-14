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

    def _delete_reservation(self, id):
        req = APIRequestFactory().delete('')
        view = ReservationModelViewSet.as_view({'delete': 'destroy'})
        res = view(req, pk=id)
        res.render()
        return res

    def _change_status(self, id):
        return self.client.post('/{}/status-change'.format(id), follow=True)

    def test_object_creation(self):
        self._create_reservation()
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Reservation.objects.first().firstname, "John")

    def test_object_creation_returns_your_reservation(self):
        res = self._create_reservation()
        self.assertEqual(res.data['firstname'], 'John')
        self.assertEqual(res.data['lastname'], 'Smith')

    def test_object_json_retrieval_by_get_request_shows_status(self):
        pk = self._create_reservation()
        res = self._get_reservation(pk.data['id'])
        assert res.data['id'] == pk.data['id']
        assert res.data['status'] == 'Upcoming reservation'

    def test_object_modification_by_get_request(self):
        res = self._create_reservation()
        assert Reservation.objects.count() == 1
        assert Reservation.objects.first().firstname == "John"
        res = self.client.get('/1', follow=True)
        res = self._modify_reservation(1, firstname='Fleet', guestcount=16)
        assert Reservation.objects.first().firstname == "Fleet"
        assert Reservation.objects.first().guestcount == 16

    def test_object_deletion(self):
        self.assertEqual(Reservation.objects.count(), 0)
        res = self._create_reservation()
        self.assertEqual(Reservation.objects.count(), 1)
        res = self._delete_reservation(1)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_all_fields_required_upon_reservation_creation(self):
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
        })
        assert not Reservation.objects.count()
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'hotelname': 'The Ritz',
        })
        assert not Reservation.objects.count()
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert not Reservation.objects.count()
        res = self._create_reservation(data={
            'firstname': 'John',
            'lastname': 'Smith',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert not Reservation.objects.count()
        res = self._create_reservation(data={
            'firstname': 'John',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert not Reservation.objects.count()
        res = self._create_reservation(data={
            'lastname': 'Smith',
            'phoneno': '17144084408',
            'datetime': '2018-08-08 11:12:12',
            'guestcount': 2,
            'hotelname': 'The Ritz',
        })
        assert not Reservation.objects.count()
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
        assert res.data['phoneno'][0] == "Ensure this value is less than or equal to 99999999999."
        data['phoneno'] = 'afafaf'
        res = self._create_reservation(data=data)
        assert res.data['phoneno'][0] == "A valid integer is required."
        data['phoneno'] = 123456789
        res = self._create_reservation(data=data)
        assert res.data['phoneno'][0] == "Ensure this value is greater than or equal to 1111111111."
        data['phoneno'] = 12345678901
        res = self._create_reservation(data=data)
        assert res.data['status'] == 'Upcoming reservation'

    def test_datetime_validated_upon_reservation_creation(self):
        data = default_data.copy()
        data['datetime'] = '2018-08-08 24:12:12'
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 0
        data['datetime'] = '2018-08-08 12:60:12'
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 0
        data['datetime'] = '2018-08-08 12:12:60'
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 0
        data['datetime'] = '2018-08-32 12:12:12'
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 0
        data['datetime'] = '2018-02-29 12:12:12'
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 0
        data['datetime'] = '2018-13-08 12:12:12'
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 0
        data['datetime'] = '2018-08-08 11:12:12'
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 1

    def test_guestcount_validated_upon_reservation_modification(self):
        data = default_data.copy()
        data['guestcount'] = 1
        res = self._create_reservation(data=data)
        assert Reservation.objects.count() == 1
        res = self._modify_reservation(1, guestcount='30:30')
        assert Reservation.objects.first().guestcount == 1
        res = self._modify_reservation(1, guestcount='30-30')
        assert Reservation.objects.first().guestcount == 1
        res = self._modify_reservation(1, guestcount='30')
        assert Reservation.objects.first().guestcount == 30

    def test_new_reservation_date_is_not_in_past(self):
        assert Reservation.objects.count() == 0
        data = default_data.copy()
        data['datetime'] = datetime.datetime.now() - datetime.timedelta(seconds=1)
        res = self._create_reservation(data)
        assert res.data['datetime'] == ["You can't reserve a time in the past!"]
        assert Reservation.objects.count() == 0

    def test_modified_reservation_date_is_not_in_past(self):
        assert Reservation.objects.count() == 0
        res = self._create_reservation()
        assert Reservation.objects.count() == 1
        res = self._modify_reservation(1, datetime=datetime.datetime.now() - datetime.timedelta(seconds=1))
        assert res.data['datetime'] == ["You can't reserve a time in the past!"]

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
        assert response.data['firstname'] == 'A'
        response = self._create_reservation(data=sample_data)
        assert response.data == {u'non_field_errors': [u'The fields hotelname, datetime must make a unique set.']}
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
        assert res.data['firstname'] == 'A'
        sample_data['datetime'] = dt_2
        sample_data['firstname'] = 'B'
        res2 = self._create_reservation(data=sample_data)
        assert Reservation.objects.count() == 2
        assert res2.data['firstname'] == 'B'
        response = self._modify_reservation(res2.data['id'], datetime=dt_1)
        assert response.data == {u'non_field_errors': [u'The fields hotelname, datetime must make a unique set.']}
        assert Reservation.objects.count() == 2
        assert Reservation.objects.first().datetime != Reservation.objects.last().datetime
