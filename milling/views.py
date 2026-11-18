from django.shortcuts import render

# Create your views here.
def  milling_view(request):
    return render(request, 'milling/milling.html')