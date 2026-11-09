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

#An API to get the total number o maize bags, packaging bags and papers and load it to the userinterface
def get_stock_summary(request):
    #sum up the total number of maize bages purchased
    total_maize = MaizeProcurement.objects.aggregate(Sum(
        'number_of_bags')) ['number_of_bags__sum'] or 0
    #sum up the totalk number of packaging bags and papers purchased 
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
            current_total = MaizeProcurement.objects.aggregate(Sum('number_of_bags'))['number_of_bags__sum'] or 0
            diff_bags = new_quantity - current_total
            if diff_bags != 0 or new_cost != 0:
                MaizeProcurement.objects.create(
                    number_of_bags=diff_bags,
                    cost=new_cost,
                    date_bought=today
                )
        elif item_type in ['papers', 'bags']:
            kwargs = {
                'number_of_papers': 0,
                'cost_of_papers': 0,
                'number_of_bags': 0,
                'cost_of_bags': 0,
                'date_bought': today
            }
            if item_type == 'papers':
                current_papers = PackagingProcurement.objects.aggregate(Sum('number_of_papers'))['number_of_papers__sum'] or 0
                kwargs['number_of_papers'] = new_quantity - current_papers
                kwargs['cost_of_papers'] = new_cost
            else:
                current_bags = PackagingProcurement.objects.aggregate(Sum('number_of_bags'))['number_of_bags__sum'] or 0
                kwargs['number_of_bags'] = new_quantity - current_bags
                kwargs['cost_of_bags'] = new_cost
            
            PackagingProcurement.objects.create(**kwargs)

        return JsonResponse({
            'status': 'success',
            'message': 'stock and cost updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)