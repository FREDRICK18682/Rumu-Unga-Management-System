from django.shortcuts import render
from rest_framework import generics
from .models import UngaBale, CompanyMachinery
from .serializers import (UngaInventorySerializer, CompanyMachinerySerializer)

# Create your views here.
def inventory_view(request):
    return render(request, 'inventory/inventory.html')


class UngaBalesInventoryAPIView(generics.ListCreateAPIView):
    queryset = UngaBale.objects.all()
    serializer_class = UngaInventorySerializer


class CompanyMachineryInventoryAPIView(generics.ListCreateAPIView):
    queryset = CompanyMachinery.objects.all()
    serializer_class = CompanyMachinerySerializer