from rest_framework import serializers

from . import models

class ReservationSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=15)
    lastname = serializers.CharField(max_length=15)
    phoneno = serializers.IntegerField()
    datetime = serializers.DateTimeField()
    guestcount = serializers.IntegerField()
    hotelname = serializers.CharField(max_length=30)
    # status = serializers.CharField(max_length=30, default=models.Reservation.STATUS_UPCOMING)
    # status_last_changed_at = serializers.DateTimeField()

class ReservationCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = ('id','firstname','lastname','phoneno','datetime','guestcount','hotelname')

    def create(self, validated_data):
        reservation = models.Reservation(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phoneno=validated_data['phoneno'],
            datetime=validated_data['datetime'],
            guestcount=validated_data['guestcount'],
            hotelname=validated_data['hotelname']
        )
        reservation.save()
        return reservation
