from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import UngaBale, CompanyMachinery
from .serializers import (UngaInventorySerializer, CompanyMachinerySerializer)
from django.db.models import Sum
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods

# Create your views here.
def inventory_view(request):
    return render(request, 'inventory/inventory.html')


class UngaBalesInventoryAPIView(generics.ListCreateAPIView):
    queryset = UngaBale.objects.all()
    serializer_class = UngaInventorySerializer


class CompanyMachineryInventoryAPIView(generics.ListCreateAPIView):
    queryset = CompanyMachinery.objects.all()
    serializer_class = CompanyMachinerySerializer

#An API to sum the to number of bales 

def  set_bales_stock(request):
    total_bales = UngaBale.objects.aggregate(Sum('number_of_bales'))['number_of_bales__sum'] or 0

    return JsonResponse({'bales_stock': total_bales})

#an api too display the machines owned by the company
def get_machinary_list(request):
    machines = CompanyMachinery.objects.all()
    machinary_list = [
        {
            'id': m.id,  
            'machinery_name': m.machinery_name,
            'status': m.status
        }
        for m in machines
    ]
    return JsonResponse({'machinary': machinary_list})

# An APi to update the company machinery recodrs
@require_http_methods(["PUT", "PATCH"])
def update_companymachinery(request, pk):
    try:
        machine = get_object_or_404(CompanyMachinery, pk=pk)
        
        data = json.loads(request.body)
        
        if 'machinery_name' in data:
            machine.machinery_name = data['machinery_name'].strip()
        if 'status' in data:
            machine.status = data['status']
            
        machine.save()
        
        return JsonResponse({
            'message': 'Machinery updated successfully',
            'id': machine.id,
            'machinery_name': machine.machinery_name,
            'status': machine.status
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)