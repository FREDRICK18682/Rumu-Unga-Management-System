import json
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from procurement.views import consume_bags_for_bales, consume_papers_for_bales
from .models import CompanyMachinery, UngaBale
from .serializers import CompanyMachinerySerializer, UngaInventorySerializer

PAPERS_PER_BALE_TYPE = {
    "1KG": 24,
    "2KG": 12,
}


def inventory_view(request):
    return render(request, 'inventory/inventory.html')


class UngaBalesInventoryAPIView(generics.ListCreateAPIView):
    queryset = UngaBale.objects.all()
    serializer_class = UngaInventorySerializer


class CompanyMachineryInventoryAPIView(generics.ListCreateAPIView):
    queryset = CompanyMachinery.objects.all()
    serializer_class = CompanyMachinerySerializer


def _get_bale_type_field_name():
    field_names = {f.name for f in UngaBale._meta.fields}
    for candidate in ("packets_kg", "bale_type", "bale_size"):
        if candidate in field_names:
            return candidate
    return None


def _classify_bale_type(raw_value):
    cleaned = str(raw_value or "").strip().upper().replace(" ", "")
    if cleaned in ("1KG", "1KGS"):
        return "1KG"
    if cleaned in ("2KG", "2KGS"):
        return "2KG"
    return None


# An API to sum 1KG and 2KG bales separately from the store
def set_bales_stock(request):
    bale_type_field = _get_bale_type_field_name()
    bales_1kg = 0
    bales_2kg = 0
    total_bales = 0

    for bale in UngaBale.objects.all():
        count = int(bale.number_of_bales or 0)
        total_bales += count
        raw_type = getattr(bale, bale_type_field, "") if bale_type_field else ""
        bale_kind = _classify_bale_type(raw_type)
        if bale_kind == "1KG":
            bales_1kg += count
        elif bale_kind == "2KG":
            bales_2kg += count

    return JsonResponse({
        'bales_1kg': bales_1kg,
        'bales_2kg': bales_2kg,
        'bales_stock': total_bales,
    })


# An API to display the machines owned by the company
def get_machinary_list(request):
    machines = CompanyMachinery.objects.all()
    machinary_list = [
        {
            'id': m.id,
            'machinery_name': m.machinery_name,
            'status': m.status,
        }
        for m in machines
    ]
    return JsonResponse({'machinary': machinary_list})


# An API to update the company machinery records
@require_http_methods(["PUT", "PATCH"])
def update_companymachinery(request, pk):
    try:
        machine = get_object_or_404(CompanyMachinery, pk=pk)
        data = json.loads(request.body)

        if 'machinery_name' in data and data['machinery_name'] is not None:
            machine.machinery_name = str(data['machinery_name']).strip()
        if 'status' in data and data['status'] is not None:
            machine.status = str(data['status']).strip()

        machine.save()

        return JsonResponse({
            'message': 'Machinery updated successfully',
            'id': machine.id,
            'machinery_name': machine.machinery_name,
            'status': machine.status,
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def _normalize_bale_type(data):
    raw_type = (
        data.get("bale_type")
        or data.get("bale_size")
        or data.get("packets_kg")
        or ""
    )
    cleaned = str(raw_type).strip().upper().replace(" ", "")
    if cleaned in ("1KG", "1KGS"):
        return "1KG"
    if cleaned in ("2KG", "2KGS"):
        return "2KG"
    raise ValidationError(
        {"bale_type": "Invalid bale type. Must be '1KG' or '2KG'."}
    )


class ProcessBalePapersAPIView(APIView):
    def post(self, request):
        raw_bales = request.data.get("number_of_bales")
        try:
            number_of_bales = int(raw_bales)
        except (TypeError, ValueError):
            raise ValidationError(
                {"number_of_bales": "Enter a valid whole number of bales."}
            )

        if number_of_bales <= 0:
            raise ValidationError(
                {"number_of_bales": "Number of bales must be greater than 0."}
            )

        bale_type = _normalize_bale_type(request.data)
        expected_papers_used = number_of_bales * PAPERS_PER_BALE_TYPE[bale_type]

        try:
            paper_result = consume_papers_for_bales(
                number_of_bales=number_of_bales,
                bale_type=bale_type,
                date_used=request.data.get("date_bought"),
            )
            bag_result = consume_bags_for_bales(number_of_bales=number_of_bales)
        except ValueError as exc:
            raise ValidationError({"stock": str(exc)})

        return Response(
            {
                "message": f"{bale_type} bale paper and bag stock updated successfully.",
                "number_of_bales": number_of_bales,
                "bale_type": bale_type,
                "papers_per_bale": PAPERS_PER_BALE_TYPE[bale_type],
                "papers_used": expected_papers_used,
                "remaining_paper_stock": paper_result["remaining_stock"],
                "bags_used": bag_result["bags_used"],
                "remaining_bag_stock": bag_result["remaining_stock"],
                "paper_deduction": paper_result,
                "bag_deduction": bag_result,
            },
            status=status.HTTP_200_OK,
        )