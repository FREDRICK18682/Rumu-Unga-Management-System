from django.shortcuts import render
from rest_framework import  generics
from .models import PaidBalesRecords, RecordsOfUnpaidBales
from .serializers import PaidBalesRecordsSerializer, RecordsOfUnpaidBalesSerializer

# Create your views here.
def sale_home(request):
    return render(request, 'sales/sales.html')