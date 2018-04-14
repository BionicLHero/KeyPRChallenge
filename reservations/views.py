# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import Reservation
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from . import serializers
import datetime, dateutil
import json


def rate_limit(func):
    def wrapped(obj, request, reservation_id):
        res = Reservation.objects.get(id=reservation_id)
        cutoff = res.status_last_changed_at + \
            datetime.timedelta(minutes=1)
        if (datetime.datetime.now() < cutoff):
            return Response({'message': 'You can only change status once a minute. Last changed at: {0}'.format(
                                         res.status_last_changed_at)})
        res.status_last_changed_at = datetime.datetime.now()
        res.save(update_fields=['status_last_changed_at'])
        return func(obj, request, reservation_id)
    return wrapped


class StatusChangeView(APIView):
    serializer_class = serializers.ChangeStatusSerializer
    def get(self, request, reservation_id, format=None):
        return Response({'message': 'Success',
                         'status': Reservation.objects.get(id=reservation_id).status})

    @rate_limit
    def post(self, request, reservation_id):
        res = Reservation.objects.get(id=reservation_id)
        res.change_status()
        res.refresh_from_db()
        return ReservationResponse(Reservation.objects.get(id=reservation_id))


def ReservationResponse(reservation):
    args2 = reservation.__dict__.copy()
    del args2['_state']
    return Response(args2)


class ReservationModelViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReservationCreationSerializer
    queryset = Reservation.objects.all()

    def list(self, request):
        response = {}
        for reservation in Reservation.objects.all():
            response[reservation.id] = {
                'firstname': reservation.firstname,
                'lastname': reservation.lastname,
                'phoneno': reservation.phoneno,
                'datetime': reservation.datetime,
                'guestcount': reservation.guestcount,
                'hotelname': reservation.hotelname,
                'status': reservation.status,
                'status_last_changed_at': reservation.status_last_changed_at
            }
        return Response(response)

    def create(self, request):
        data = request.data.copy()
        data['status_last_changed_at'] = datetime.datetime.now()
        serializer = serializers.ReservationSerializer(data = data)
        if serializer.is_valid():
            if dateutil.parser.parse(str(data['datetime'])) < datetime.datetime.now():
                return Response({'datetime': ["You can't reserve a time in the past!"]}, status=status.HTTP_400_BAD_REQUEST)
            res = Reservation.objects.create(**serializer.data)
            return ReservationResponse(res)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        return ReservationResponse(Reservation.objects.get(id=pk))

    def update(self, request, pk=None):
        return self.partial_update(request, pk)

    def partial_update(self, request, pk=None):
        res = Reservation.objects.get(id=pk)
        res_dict = res.__dict__
        change_date_or_location = False
        Serializer = serializers.ExistingReservationSerializer
        for key, value in request.data.iteritems():
            if value == '': continue
            res_dict[key] = value
            if key in ['datetime','hotelname']:
                change_date_or_location = True
        if change_date_or_location:
            Serializer = serializers.ReservationSerializer
        del res_dict['_state']
        del res_dict['status']
        serializer = Serializer(data = res_dict)
        if serializer.is_valid():
            if dateutil.parser.parse(str(res_dict['datetime'])) < datetime.datetime.now():
                return Response({'datetime': ["You can't reserve a time in the past!"]}, status=status.HTTP_400_BAD_REQUEST)
            Reservation.objects.filter(id=pk).update(**res_dict)
            return ReservationResponse(Reservation.objects.get(id=pk))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        Reservation.objects.filter(id=pk).delete()
        return Response({'http_method': 'DELETE'})
