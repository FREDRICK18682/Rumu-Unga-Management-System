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
#serilaizer for the APi to display the record for a given date
class DailySalesSummerySerializer(serializers.Serializer):
    data = serializers.DateField()
    paid_sales = PaidBalesRecordsSerializer()
    unpaid_sales = RecordsOfUnpaidBalesSerializer()