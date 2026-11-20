from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MaizeProcurement, PackagingProcurement
from .serializers import MaizeProcurementSerializer, PackagingProcurementSerializer

PAPERS_PER_BALE = {
    "1KG": 24,
    "2KG": 12,
}


class MaizeProcurementAPIView(generics.ListCreateAPIView):
    queryset = MaizeProcurement.objects.all().order_by("date_bought")
    serializer_class = MaizeProcurementSerializer


class PackagingProcurementAPIView(generics.ListCreateAPIView):
    queryset = PackagingProcurement.objects.all().order_by("date_bought")
    serializer_class = PackagingProcurementSerializer


def procurement_view(request):
    return render(request, "procurement/procurement.html")


def get_stock_summary(request):
    total_maize = (
        MaizeProcurement.objects.aggregate(Sum("number_of_bags"))["number_of_bags__sum"]
        or 0
    )

    pkg_totals = PackagingProcurement.objects.aggregate(
        Sum("number_of_papers"),
        Sum("number_of_bags"),
    )
    total_papers = pkg_totals["number_of_papers__sum"] or 0
    total_bags = pkg_totals["number_of_bags__sum"] or 0

    return JsonResponse({
        "maize_stock": total_maize,
        "papers_stock": total_papers,
        "bags_stock": total_bags,
    })


class UpdateStockAPIView(APIView):
    def post(self, request):
        item_type = request.data.get("item_type")
        quantity = request.data.get("quantity")
        cost = request.data.get("cost", "0.00")
        raw_paper_type = (request.data.get("type_of_papers") or "").strip().upper()

        if item_type not in ("maize", "papers", "bags"):
            return Response(
                {"message": "Invalid item_type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            qty_val = int(quantity)
            cost_val = Decimal(str(cost))
        except (TypeError, ValueError, InvalidOperation):
            return Response(
                {"message": "Invalid quantity or cost."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if qty_val < 0 or cost_val < 0:
            return Response(
                {"message": "Quantity and cost must be non-negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if item_type == "papers" and raw_paper_type not in ("1KG", "2KG"):
            return Response(
                {"message": "Please select a valid type of papers (1KG or 2KG)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()

        with transaction.atomic():
            if item_type == "maize":
                today_maize = (
                    MaizeProcurement.objects.filter(date_bought=today)
                    .order_by("-id")
                    .first()
                )
                if today_maize is None:
                    MaizeProcurement.objects.create(
                        date_bought=today,
                        number_of_bags=qty_val,
                        cost=cost_val,
                    )
                else:
                    today_maize.number_of_bags = qty_val
                    today_maize.cost = cost_val
                    today_maize.save()

            elif item_type == "papers":
                today_paper = (
                    PackagingProcurement.objects.filter(
                        date_bought=today,
                        type_of_papers__iexact=raw_paper_type,
                    )
                    .order_by("-id")
                    .first()
                )
                if today_paper is None:
                    PackagingProcurement.objects.create(
                        date_bought=today,
                        type_of_papers=raw_paper_type,
                        number_of_papers=qty_val,
                        cost_of_papers=cost_val,
                        number_of_bags=0,
                        cost_of_bags=Decimal("0.00"),
                    )
                else:
                    today_paper.type_of_papers = raw_paper_type
                    today_paper.number_of_papers = qty_val
                    today_paper.cost_of_papers = cost_val
                    today_paper.save()

            elif item_type == "bags":
                today_bag = (
                    PackagingProcurement.objects.filter(date_bought=today)
                    .order_by("-id")
                    .first()
                )
                if today_bag is None:
                    PackagingProcurement.objects.create(
                        date_bought=today,
                        number_of_papers=0,
                        cost_of_papers=Decimal("0.00"),
                        number_of_bags=qty_val,
                        cost_of_bags=cost_val,
                    )
                else:
                    today_bag.number_of_bags = qty_val
                    today_bag.cost_of_bags = cost_val
                    today_bag.save()

        return Response({"message": "Stock updated successfully."}, status=status.HTTP_200_OK)


class PapersByTypeSummaryAPIView(APIView):
    def get(self, request):
        queryset = PackagingProcurement.objects.exclude(
            type_of_papers__isnull=True
        ).exclude(type_of_papers="")

        paper_type = request.query_params.get("type")
        if paper_type:
            queryset = queryset.filter(type_of_papers__iexact=paper_type.strip())

        grouped = (
            queryset.values("type_of_papers")
            .annotate(total_papers=Sum("number_of_papers"))
            .order_by("type_of_papers")
        )

        totals_by_type = {}
        by_type = []

        for row in grouped:
            clean_type = (row["type_of_papers"] or "").strip().upper()
            total = row["total_papers"] or 0
            if not clean_type:
                continue
            totals_by_type[clean_type] = totals_by_type.get(clean_type, 0) + total
            by_type.append({
                "type_of_papers": clean_type,
                "total_papers": total,
            })

        data = {
            "by_type": by_type,
            "papers_1kg": totals_by_type.get("1KG", 0),
            "papers_2kg": totals_by_type.get("2KG", 0),
        }

        return Response(data, status=status.HTTP_200_OK)


def get_paper_stock_by_type(paper_type: str) -> int:
    normalized = (paper_type or "").strip().upper()
    total = (
        PackagingProcurement.objects.filter(type_of_papers__iexact=normalized)
        .aggregate(total=Sum("number_of_papers"))["total"]
        or 0
    )
    return int(total)

#API to reducs the packaging papers base on type of bale
def consume_papers_for_bales(number_of_bales: int, bale_type: str, date_used=None) -> dict:
    bales_count = int(number_of_bales)
    if bales_count <= 0:
        raise ValueError("Number of bales must be greater than 0.")

    normalized_type = (bale_type or "").strip().upper()
    if normalized_type not in PAPERS_PER_BALE:
        raise ValueError("Bale type must be either '1KG' or '2KG'.")

    papers_used = bales_count * PAPERS_PER_BALE[normalized_type]

    with transaction.atomic():
        rows = list(
            PackagingProcurement.objects.select_for_update()
            .filter(type_of_papers__iexact=normalized_type, number_of_papers__gt=0)
            .order_by("date_bought", "id")
        )
        available_stock = sum(r.number_of_papers for r in rows)

        if available_stock < papers_used:
            raise ValueError(
                f"Insufficient {normalized_type} papers in stock. "
                f"Need {papers_used}, available {available_stock}."
            )

        remaining_to_deduct = papers_used
        for row in rows:
            if remaining_to_deduct <= 0:
                break
            if row.number_of_papers >= remaining_to_deduct:
                row.number_of_papers -= remaining_to_deduct
                row.save(update_fields=["number_of_papers"])
                remaining_to_deduct = 0
            else:
                remaining_to_deduct -= row.number_of_papers
                row.number_of_papers = 0
                row.save(update_fields=["number_of_papers"])

        new_stock = available_stock - papers_used

    return {
        "bale_type": normalized_type,
        "number_of_bales": bales_count,
        "papers_used": papers_used,
        "remaining_stock": new_stock,
    }

# an APi to reduces the packaging bags 
def consume_bags_for_bales(number_of_bales: int) -> dict:
    bales_count = int(number_of_bales)
    if bales_count <= 0:
        raise ValueError("Number of bales must be greater than 0.")

    bags_used = bales_count  # 1 packaging bag per bale for both 1KG and 2KG

    with transaction.atomic():
        rows = list(
            PackagingProcurement.objects.select_for_update()
            .filter(number_of_bags__gt=0)
            .order_by("date_bought", "id")
        )
        available_stock = sum(r.number_of_bags for r in rows)

        if available_stock < bags_used:
            raise ValueError(
                f"Insufficient packaging bags in stock. "
                f"Need {bags_used}, available {available_stock}."
            )

        remaining_to_deduct = bags_used
        for row in rows:
            if remaining_to_deduct <= 0:
                break
            if row.number_of_bags >= remaining_to_deduct:
                row.number_of_bags -= remaining_to_deduct
                row.save(update_fields=["number_of_bags"])
                remaining_to_deduct = 0
            else:
                remaining_to_deduct -= row.number_of_bags
                row.number_of_bags = 0
                row.save(update_fields=["number_of_bags"])

        new_stock = available_stock - bags_used

    return {
        "number_of_bales": bales_count,
        "bags_used": bags_used,
        "remaining_stock": new_stock,
    }