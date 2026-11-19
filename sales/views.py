from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaidBalesRecords, RecordsOfUnpaidBales
from .serializers import (
    PaidBalesRecordsSerializer,
    RecordsOfUnpaidBalesSerializer,
    DailySalesSummerySerializer,
)
from inventory.services import get_available_bales, reduce_stock


def sale_home(request):
    return render(request, 'sales/sales.html')


def _validate_and_reduce_stock(bales_needed):
    available = get_available_bales()
    if available <= 0:
        raise ValidationError({"number_of_bales": "No bales left in store."})
    if bales_needed > available:
        raise ValidationError(
            {"number_of_bales": f"Only {available} bales available in store."}
        )
    if not reduce_stock(bales_needed):
        raise ValidationError({"number_of_bales": "Could not reduce bale stock. Try again."})


class PaidBalesRecordsAPIView(generics.ListCreateAPIView):
    queryset = PaidBalesRecords.objects.all()
    serializer_class = PaidBalesRecordsSerializer

    def perform_create(self, serializer):
        bales_needed = int(serializer.validated_data.get("number_of_bales", 0))
        _validate_and_reduce_stock(bales_needed)
        serializer.save()


class RecordsOfUnpaidBalesAPIView(generics.ListCreateAPIView):
    queryset = RecordsOfUnpaidBales.objects.all()
    serializer_class = RecordsOfUnpaidBalesSerializer

    def perform_create(self, serializer):
        bales_needed = int(serializer.validated_data.get("number_of_bales", 0))
        _validate_and_reduce_stock(bales_needed)
        serializer.save()


class DailySalesSummeryAPiView(APIView):
    def get(self, request):
        selected_date = request.query_params.get('date')

        if not selected_date:
            selected_date = str(timezone.localdate())

        paid_summary = PaidBalesRecords.objects.filter(date_bought=selected_date).aggregate(
            total_bales=Sum('number_of_bales'),
            total_money=Sum('money_collected')
        )

        unpaid_summary = RecordsOfUnpaidBales.objects.filter(date_bought=selected_date).aggregate(
            total_bales=Sum('number_of_bales'),
            total_cost=Sum('total_value')
        )

        paid_bales = paid_summary['total_bales'] or 0
        paid_money = paid_summary['total_money'] or 0.00

        unpaid_bales = unpaid_summary['total_bales'] or 0
        unpaid_cost = unpaid_summary['total_cost'] or 0.00

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