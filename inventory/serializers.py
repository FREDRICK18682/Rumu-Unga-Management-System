from rest_framework import serializers
from .models import UngaBale, CompanyMachinery

class UngaInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UngaBale
        fields = '__all__'

class CompanyMachinerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMachinery
        fields = '__all__'

