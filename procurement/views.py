from django.shortcuts import render
from rest_framework import generics
from django.shortcuts import render

from .models import MaizeProcurement, PackagingProcurement
from .serializers import (MaizeProcurementSerializer, PackagingProcurementSerializer)
# Create your views here.

class MaizeProcurementAPIView(generics.ListCreateAPIView):
    queryset = MaizeProcurement.objects.all().order_by('date_bought')
    serializer_class = MaizeProcurementSerializer
class PackagingProcurementAPIView(generics.ListCreateAPIView):
    queryset = PackagingProcurement.objects.all().order_by('date_bought')
    serializer_class = PackagingProcurementSerializer

def procurement_view(request):
    return render(request, 'procurement/procurement.html')