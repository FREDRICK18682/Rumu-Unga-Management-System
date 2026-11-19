import re
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LocalMilling, SchoolMillRecords
from .serializers import LocalMIllingSerializer, SchoolMillRecordsSerializer

GRADE_RATES = {
    "Grade 1": Decimal("8.00"),
    "Grade 2": Decimal("10.00"),
}
SCHOOL_BAG_PRICE = Decimal("5720.00")


def extract_kgs(value):
    if not value:
        return Decimal("0.00")
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    return Decimal(match.group(0)) if match else Decimal("0.00")


def milling_view(request):
    return render(request, "milling/milling.html")


class LocalMillingAPIView(generics.ListCreateAPIView):
    queryset = LocalMilling.objects.all()
    serializer_class = LocalMIllingSerializer

    def perform_create(self, serializer):
        kgs_raw = serializer.validated_data.get("kgs")
        grade = serializer.validated_data.get("unga_grade")

        kg_amount = extract_kgs(kgs_raw)
        if kg_amount <= Decimal("0.00"):
            raise ValidationError({"kgs": "Enter a valid positive weight in kgs."})

        rate = GRADE_RATES.get(grade)
        if rate is None:
            raise ValidationError({"unga_grade": "Invalid grade. Choose 'Grade 1' or 'Grade 2'."})

        calculated_cost = (kg_amount * rate).quantize(Decimal("0.01"))
        serializer.save(total_cost=calculated_cost)


class SchoolMillRecordsAPIView(generics.ListCreateAPIView):
    queryset = SchoolMillRecords.objects.all()
    serializer_class = SchoolMillRecordsSerializer

    def perform_create(self, serializer):
        bags = serializer.validated_data.get("number_of_bags")
        if bags is None or int(bags) <= 0:
            raise ValidationError({"number_of_bags": "Number of bags must be greater than 0."})

        calculated_value = (Decimal(int(bags)) * SCHOOL_BAG_PRICE).quantize(Decimal("0.01"))
        serializer.save(total_value=calculated_value)


class DailyMillingSummaryAPIView(APIView):
    def get(self, request):
        raw_date = request.query_params.get("date")
        selected_date = parse_date(raw_date) if raw_date else timezone.localdate()

        if raw_date and selected_date is None:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        local_qs = LocalMilling.objects.filter(date_milled=selected_date).order_by("-id")
        school_qs = SchoolMillRecords.objects.filter(date_milled=selected_date).order_by("-id")

        local_records = []
        total_kgs = Decimal("0.00")

        for row in local_qs:
            extracted = extract_kgs(row.kgs)
            total_kgs += extracted
            local_records.append(
                {
                    "id": row.id,
                    "source": "Local Milling",
                    "kgs": row.kgs,
                    "kgs_value": str(extracted),
                    "unga_grade": row.unga_grade,
                    "amount": str(row.total_cost),
                    "date_milled": str(row.date_milled),
                }
            )

        school_records = [
            {
                "id": row.id,
                "source": "School Mill",
                "name_of_school": row.name_of_school,
                "number_of_bags": row.number_of_bags,
                "amount": str(row.total_value),
                "date_milled": str(row.date_milled),
            }
            for row in school_qs
        ]

        local_money = local_qs.aggregate(total=Sum("total_cost"))["total"] or Decimal("0.00")
        school_money = school_qs.aggregate(total=Sum("total_value"))["total"] or Decimal("0.00")
        total_money_collected = local_money + school_money

        return Response(
            {
                "date": str(selected_date),
                "summary": {
                    "total_kgs": str(total_kgs),
                    "local_money_collected": str(local_money),
                    "school_money_collected": str(school_money),
                    "total_money_collected": str(total_money_collected),
                },
                "local_records": local_records,
                "school_records": school_records,
            },
            status=status.HTTP_200_OK,
        )