from django.shortcuts import render
from rest_framework import generics
from django.shortcuts import render

from .models import MaizeProcurement, PackagingProcurement
from .serializers import (MaizeProcurementSerializer, PackagingProcurementSerializer)
from django.http import JsonResponse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
# Create your views here.

class MaizeProcurementAPIView(generics.ListCreateAPIView):
    queryset = MaizeProcurement.objects.all().order_by('date_bought')
    serializer_class = MaizeProcurementSerializer

class PackagingProcurementAPIView(generics.ListCreateAPIView):
    queryset = PackagingProcurement.objects.all().order_by('date_bought')
    serializer_class = PackagingProcurementSerializer

def procurement_view(request):
    return render(request, 'procurement/procurement.html')

# An API to get the total number of maize bags, packaging bags and papers and load it to the user interface
def get_stock_summary(request):
    # sum up the total number of maize bags purchased
    total_maize = MaizeProcurement.objects.aggregate(Sum(
        'number_of_bags'))['number_of_bags__sum'] or 0
    
    # sum up the total number of packaging bags and papers purchased 
    pkg_totals = PackagingProcurement.objects.aggregate(
        Sum('number_of_papers'),
        Sum('number_of_bags')
    )
    total_papers = pkg_totals['number_of_papers__sum'] or 0
    total_bags = pkg_totals['number_of_bags__sum'] or 0
    
    return JsonResponse({
        'maize_stock': total_maize,
        'papers_stock': total_papers,
        'bags_stock': total_bags
    })

@csrf_exempt
def update_stock_summary(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        item_type = data.get('item_type')
        new_quantity = int(data.get('quantity', 0))
        new_cost = float(data.get('cost', 0))

        today = timezone.now().date()

        if item_type == 'maize':
            # For maize, clear past rows or adjust so the total equals new_quantity strictly
            today_record, created = MaizeProcurement.objects.get_or_create(
                date_bought=today,
                defaults={'number_of_bags': 0, 'cost': 0.0}
            )
            other_total = MaizeProcurement.objects.exclude(pk=today_record.pk).aggregate(Sum('number_of_bags'))['number_of_bags__sum'] or 0
            required_today = new_quantity - other_total
            
            if required_today < 0:
                MaizeProcurement.objects.exclude(pk=today_record.pk).delete()
                required_today = new_quantity

            today_record.number_of_bags = required_today
            today_record.cost = new_cost
            today_record.save()

        elif item_type in ['papers', 'bags']:
            today_record, created = PackagingProcurement.objects.get_or_create(
                date_bought=today,
                defaults={
                    'number_of_papers': 0,
                    'cost_of_papers': 0.0,
                    'number_of_bags': 0,
                    'cost_of_bags': 0.0
                }
            )
            
            if item_type == 'papers':
                other_total = PackagingProcurement.objects.exclude(pk=today_record.pk).aggregate(Sum('number_of_papers'))['number_of_papers__sum'] or 0
                required_today = new_quantity - other_total
                
                if required_today < 0:
                    PackagingProcurement.objects.exclude(pk=today_record.pk).delete()
                    required_today = new_quantity
                    
                today_record.number_of_papers = required_today
                today_record.cost_of_papers = new_cost
            else:
                other_total = PackagingProcurement.objects.exclude(pk=today_record.pk).aggregate(Sum('number_of_bags'))['number_of_bags__sum'] or 0
                required_today = new_quantity - other_total
                
                if required_today < 0:
                    PackagingProcurement.objects.exclude(pk=today_record.pk).delete()
                    required_today = new_quantity
                    
                today_record.number_of_bags = required_today
                today_record.cost_of_bags = new_cost
                
            today_record.save()

        return JsonResponse({
            'status': 'success',
            'message': 'stock and cost updated successfully'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)