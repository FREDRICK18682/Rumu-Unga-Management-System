from django.shortcuts import render
from .models import LocalMilling, SchoolMillRecords
from .serializers import LocalMIllingSerializer, SchoolMillRecordsSerializer
from rest_framework import generics

# Create your views here.
def  milling_view(request):
    return render(request, 'milling/milling.html')

class LocalMillingAPIView(generics.ListCreateAPIView):
    queryset = LocalMilling.objects.all()
    serializer_class = LocalMIllingSerializer

class SchoolMillRecordsAPIView(generics.ListCreateAPIView):
    queryset=SchoolMillRecords.objects.all()
    serializer_class = SchoolMillRecordsSerializer