from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from . import models

class ExistingReservationSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=15)
    lastname = serializers.CharField(max_length=15)
    phoneno = serializers.IntegerField()
    datetime = serializers.DateTimeField()
    guestcount = serializers.IntegerField()
    hotelname = serializers.CharField(max_length=30)

class ReservationSerializer(ExistingReservationSerializer):
    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=models.Reservation.objects.all(),
                fields=('hotelname', 'datetime')
            )
        ]

class ChangeStatusSerializer(serializers.Serializer):
    class Meta:
        pass

class ReservationCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = ('id','status','firstname','lastname','phoneno','datetime','guestcount','hotelname','status_last_changed_at')
        extra_kwargs = {'status': {'read_only': True}}
