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

class ReservationViewSet(viewsets.ViewSet):
    serializer_class = serializers.ReservationSerializer
    def list(self, request):
        return Response({'message': 'List all reservations',
                         'reservations': 'reservations'})

    def create(self, request):
        serializer = serializers.ReservationSerializer(data = request.data)
        if serializer.is_valid():
            name = serializer.data.get('firstname')
            return Response({'message': 'Reservation made for {0}'.format(name)})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        return Response({'http_method': 'GET'})

    def update(self, request, pk=None):
        return Response({'http_method': 'PUT'})

    def partial_update(self, request, pk=None):
        return Response({'http_method': 'PATCH'})

    def destroy(self, request, pk=None):
        return Response({'http_method': 'DELETE'})


class ReservationModelViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReservationCreationSerializer
    queryset = Reservation.objects.all()

# def index(request):
#     all_reservations = Reservation.objects.all()
#     response = {}
#     for i in Reservation.objects.all():
#         response[i.pk] = _clean_res_dict(i)
#     return JsonResponse(response)
#
#
# def _clean_res_dict(res):
#     res_dict = res.__dict__.copy()
#     del res_dict['_state']
#     return res_dict
#
#
# def ReservationJsonResponse(res):
#     return JsonResponse(_clean_res_dict(res))
#
#
# def retrieve(request, reservation_id):
#     return ReservationJsonResponse(Reservation.objects.get(id=reservation_id))
#
#
# def retrieve_status(request, reservation_id):
#     res = Reservation.objects.get(id=reservation_id)
#     return JsonResponse({'status': res.status})
#
#
# def modify(request, reservation_id):
#     res = Reservation.objects.get(id=reservation_id)
#     keys_to_update = []
#     new_reservation = _clean_res_dict(res)
#     for i in request.GET.keys():
#         if i in settings.FIELDS_TO_IGNORE + ['status']:
#             continue
#         new_reservation[i] = request.GET[i]
#         keys_to_update.append(i)
#     # is_valid, err = Reservation.validate(new_reservation)
#     # if not is_valid:
#     #     return JsonResponse({'status': '-1', 'exception': err})
#     if ('hotelname' in keys_to_update or 'datetime' in keys_to_update) \
#         and Reservation.objects.filter(hotelname=new_reservation['hotelname'],
#                                     datetime=new_reservation['datetime']).count() > 0:
#             return JsonResponse({'status': '-1', 'exception': "This hotel is booked at {}.".format(new_reservation['datetime'])})
#     for i in keys_to_update:
#         setattr(res, i, new_reservation[i])
#     res.save(update_fields=keys_to_update)
#     return ReservationJsonResponse(res)
#
#
# def delete(request, reservation_id):
#     res = Reservation.objects.filter(id=reservation_id).delete()
#     if res[0] == 1:
#         return JsonResponse({'status': '0', 'message': 'Reservation deleted.'})
#     elif res[0] == 0:
#         return JsonResponse({'status': '-1', 'exception': 'Reservation does not exist.'})
#
#
# def create(request):
#     Reservation.objects.create_reservation(**request.GET.dict())
# #     new_reservation = {}
# #     request_dict = request.GET.dict()
# #     for i in request_dict.keys():
# #         if i in settings.FIELDS_TO_IGNORE:
# #             continue
# #         new_reservation[i] = request_dict[i]
# #     if any(n not in new_reservation.keys() for n in ['firstname', 'lastname', 'datetime', 'hotelname', 'guestcount', 'phoneno']):
# #         return JsonResponse({'status': '-1', 'exception': "Insufficient information entered. You need to supply a first/last name, date and time, the hotel name, the number of guests, and a phone number."})
# #     # is_valid, err = Reservation.validate(new_reservation)
# #     # if not is_valid:
# #     #     return JsonResponse({'status': '-1', 'exception': err})
# #     if Reservation.objects.filter(hotelname=new_reservation['hotelname'],
# #                                   datetime=new_reservation['datetime']).count() > 0:
# #         return JsonResponse({'status': '-1', 'exception': "This hotel is booked at {}.".format(new_reservation['datetime'])})
# #     Reservation.objects.create(**new_reservation)
# #     return ReservationJsonResponse(Reservation.objects.get(**new_reservation))
#
#
# def state_change(request, reservation_id, state):
#     res = Reservation.objects.get(id=reservation_id)
#     check = res.change_state(int(state))
#     if check == False:
#         return JsonResponse({'status': '-1', 'exception': "You can only change status once a minute. Last changed: {}".format(res.status_last_changed_at)})
#     return ReservationJsonResponse(res)
