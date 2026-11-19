from rest_framework import serializers
from .models import LocalMilling, SchoolMillRecords

class LocalMIllingSerializer(serializers.ModelSerializer):
    class Meta:
        model= LocalMilling
        fields = '__all__'


class SchoolMillRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolMillRecords
        fields = '__all__'

        