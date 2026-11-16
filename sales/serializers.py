from rest_framework import serializers
from .models import PaidBalesRecords, RecordsOfUnpaidBales

class PaidBalesRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaidBalesRecords
        fields="__all__"


class RecordsOfUnpaidBalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordsOfUnpaidBales
        fields="__all__"