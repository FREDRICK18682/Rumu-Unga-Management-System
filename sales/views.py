from django.shortcuts import render

# Create your views here.
def sale_home(request):
    return render(request, 'sales/sales.html')