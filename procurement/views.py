from django.shortcuts import render
from rest_framework import generics
from django.shortcuts import render

from .models import MaizeProcurement, PackagingProcurement
from .serializers import (MaizeProcurementSerializer, PackagingProcurementSerializer)
from django.http import JsonResponse
from django.db.models import Sum
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
