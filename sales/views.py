from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.services import get_available_bales, reduce_stock
from .models import PaidBalesRecords, RecordsOfUnpaidBales
from .serializers import (
    PaidBalesRecordsSerializer,
    RecordsOfUnpaidBalesSerializer,
)

BALE_PRICE = Decimal("1500.00")
VALID_BALE_SIZES = ("1KG", "2KG")


def sale_home(request):
    return render(request, 'sales/sales.html')


def _validate_and_reduce_stock(bales_needed):
    if bales_needed <= 0:
        raise ValidationError({"number_of_bales": "Number of bales must be greater than 0."})

    available = get_available_bales()
    if available <= 0:
        raise ValidationError({"number_of_bales": "No bales left in store."})
    if bales_needed > available:
        raise ValidationError(
            {"number_of_bales": f"Only {available} bales available in store."}
        )
    if not reduce_stock(bales_needed):
        raise ValidationError({"number_of_bales": "Could not reduce bale stock. Try again."})


def _calculate_bale_total(bales_needed):
    return (Decimal(bales_needed) * BALE_PRICE).quantize(Decimal("0.01"))


def _extract_bale_size(data):
    raw_size = (
        data.get("bale_size")
        or data.get("unga_bale_size")
        or data.get("bale_type")
        or ""
    )
    normalized = str(raw_size).strip().upper().replace(" ", "")
    if normalized in ("1KG", "1KGS"):
        return "1KG"
    if normalized in ("2KG", "2KGS"):
        return "2KG"
    raise ValidationError(
        {"bale_size": "Select a valid unga bale size ('1KG' or '2KG')."}
    )


class PaidBalesRecordsAPIView(generics.ListCreateAPIView):
    queryset = PaidBalesRecords.objects.all()
    serializer_class = PaidBalesRecordsSerializer

    def perform_create(self, serializer):
        bales_needed = int(serializer.validated_data.get("number_of_bales", 0))
        _validate_and_reduce_stock(bales_needed)
        calculated_money = _calculate_bale_total(bales_needed)
        serializer.save(money_collected=calculated_money)


class RecordsOfUnpaidBalesAPIView(generics.ListCreateAPIView):
    queryset = RecordsOfUnpaidBales.objects.all()
    serializer_class = RecordsOfUnpaidBalesSerializer

    def perform_create(self, serializer):
        bales_needed = int(serializer.validated_data.get("number_of_bales", 0))
        _validate_and_reduce_stock(bales_needed)
        calculated_value = _calculate_bale_total(bales_needed)
        serializer.save(total_value=calculated_value)


class DailySalesSummeryAPiView(APIView):
    def get(self, request):
        raw_date = request.query_params.get('date')
        if raw_date:
            parsed = parse_date(raw_date)
            if parsed is None:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            selected_date = parsed
        else:
            selected_date = timezone.localdate()

        paid_summary = PaidBalesRecords.objects.filter(date_bought=selected_date).aggregate(
            total_bales=Sum('number_of_bales'),
            total_money=Sum('money_collected')
        )

        unpaid_summary = RecordsOfUnpaidBales.objects.filter(date_bought=selected_date).aggregate(
            total_bales=Sum('number_of_bales'),
            total_cost=Sum('total_value')
        )

        paid_bales = paid_summary['total_bales'] or 0
        paid_money = paid_summary['total_money'] or Decimal("0.00")

        unpaid_bales = unpaid_summary['total_bales'] or 0
        unpaid_cost = unpaid_summary['total_cost'] or Decimal("0.00")

        raw_data = {
            'date': str(selected_date),
            "paid_sales": {
                "bales_sold": paid_bales,
                "money_collected": str(paid_money)
            },
            "unpaid_sales": {
                "bales_unpaid": unpaid_bales,
                "total_value": str(unpaid_cost)
            }
        }

        return Response(raw_data, status=status.HTTP_200_OK)


class SendBalesToInventoryAPIView(APIView):
    def post(self, request):
        raw_bales = request.data.get("number_of_bales")
        if raw_bales is None:
            raw_bales = request.query_params.get("number_of_bales")

        try:
            bales_needed = int(raw_bales)
        except (TypeError, ValueError):
            raise ValidationError({"number_of_bales": "Enter a valid whole number of bales."})

        if bales_needed <= 0:
            raise ValidationError({"number_of_bales": "Number of bales must be greater than 0."})

        bale_size = _extract_bale_size(request.data)

        available = get_available_bales()
        if available <= 0:
            raise ValidationError({"number_of_bales": "No bales left in store."})
        if bales_needed > available:
            raise ValidationError(
                {"number_of_bales": f"Only {available} bales available in store."}
            )

        if not reduce_stock(bales_needed):
            return Response(
                {"error": "Could not reduce bale stock in inventory. Try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            paper_deduction = consume_papers_for_bales(
                number_of_bales=bales_needed,
                bale_type=bale_size,
                date_used=request.data.get("date_bought"),
            )
        except ValueError as exc:
            raise ValidationError({"bale_size": str(exc)})

        remaining_bales = get_available_bales()

        return Response(
            {
                "message": "Bales and packaging papers updated in inventory/procurement successfully.",
                "bales_sent": bales_needed,
                "bale_size": bale_size,
                "remaining_bales": remaining_bales,
                "paper_deduction": paper_deduction,
            },
            status=status.HTTP_200_OK,
        )