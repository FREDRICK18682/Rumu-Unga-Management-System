from rest_framework import serializers
from .models import LocalMilling, SchoolMillRecords


class LocalMIllingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalMilling
        fields = "__all__"
        read_only_fields = ["total_cost"]


class SchoolMillRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolMillRecords
        fields = "__all__"
        read_only_fields = ["total_value"]