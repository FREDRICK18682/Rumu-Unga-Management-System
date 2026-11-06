from django.shortcuts import render
from rest_framework import generics
from .models import MaizeProcurement, PackagingProcurement
from serializers import (MaizeProcurementSerializer, PackagingProcurementSerializer)
# Create your views here.

class MaizeProcurementAPIView(generics.ListCreateAPIView):
    queryset = MaizeProcurement.objects.all().order_by('-date_bought')
    serializer_class = MaizeProcurementSerializer
class PackagingProcurementAPIView(generics.ListCreateAPIView):
    queryset = PackagingProcurement.objects.all().order_by('_date_bought')
    serializer_class = PackagingProcurementSerializer