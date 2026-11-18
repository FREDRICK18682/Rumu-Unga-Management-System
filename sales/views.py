from django.shortcuts import render
from rest_framework import  generics
from django.utils import timezone
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework import status
from .models import PaidBalesRecords, RecordsOfUnpaidBales
from .serializers import PaidBalesRecordsSerializer, RecordsOfUnpaidBalesSerializer, DailySalesSummerySerializer
from inventory.services import reduce_stock
# Create your views here.
def sale_home(request):
    return render(request, 'sales/sales.html')

class PaidBalesRecordsAPIView(generics.ListCreateAPIView):
    queryset= PaidBalesRecords.objects.all()
    serializer_class = PaidBalesRecordsSerializer

    #The function to handel the reducing of bales stock in store
    def perform_create(self, serializer):
        sale=serializer.save()
        reduce_stock(sale.number_of_bales)

class RecordsOfUnpaidBalesAPIView(generics.ListCreateAPIView):
    queryset = RecordsOfUnpaidBales.objects.all()
    serializer_class = RecordsOfUnpaidBalesSerializer
    
    # the function yto hndel reducing of bales in store
    def perform_create(self, serializer):
        credit_sale = serializer.save()
        reduce_stock(credit_sale.number_of_bales)

#Creating an API to Feach record from the database based on the date 
class DailySalesSummeryAPiView(APIView):
    def get(self, request):
        selected_date = request.query_params.get('date')

        if not selected_date:
            selected_date = str(timezone.localdate())
        
        # Sums up the paid sales separately for the selected date
        paid_summary = PaidBalesRecords.objects.filter(date_bought=selected_date).aggregate(
            total_bales=Sum('number_of_bales'),
            total_money=Sum('money_collected')
        )

        # Sums up the unpaid sales separately for the selected date 
        unpaid_summary = RecordsOfUnpaidBales.objects.filter(date_bought=selected_date).aggregate(
            total_bales=Sum('number_of_bales'), 
            total_cost=Sum('total_value')
        )
        
        paid_bales = paid_summary['total_bales'] or 0
        paid_money = paid_summary['total_money'] or 0.00

        unpaid_bales = unpaid_summary['total_bales'] or 0
        unpaid_cost = unpaid_summary['total_cost'] or 0.00

        # This dictionary is already valid JSON structure
        
        raw_data = {
            'date': selected_date,
            "paid_sales": {
                "bales_sold": paid_bales,
                "money_collected": paid_money
            },
            "unpaid_sales": {
                "bales_unpaid": unpaid_bales,
                "total_value": unpaid_cost
            }
        }
        
        return Response(raw_data, status=status.HTTP_200_OK)