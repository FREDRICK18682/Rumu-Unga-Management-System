from django.shortcuts import render
from rest_framework import  generics
from .models import PaidBalesRecords, RecordsOfUnpaidBales
from .serializers import PaidBalesRecordsSerializer, RecordsOfUnpaidBalesSerializer

# Create your views here.
def sale_home(request):
    return render(request, 'sales/sales.html')

class PaidBalesRecordsAPIView(generics.ListCreateAPIView):
    queryset= PaidBalesRecords.object.all()
    serializer_class = PaidBalesRecordsSerializer

class RecordsOfUnpaidBalesAPIView(generics.ListCreateAPIView):
    queryset = RecordsOfUnpaidBales.objects.all()
    serializer_class = PaidBalesRecordsSerializer