from rest_framework import serializers
from .models import MaizeProcurement, PackagingProcurement

class MaizeProcurementSerializer(serializers.ModelSerializer):
    class Meta:
        model= MaizeProcurement
        fields = '__all__'
        

# to hadle the form for the packaging papers and bags
class PackagingProcurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackagingProcurement
        fields = '__all__'
        