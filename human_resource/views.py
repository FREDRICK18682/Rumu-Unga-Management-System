from django.shortcuts import render

# Create your views here.
def humanresource_view(request):
    return render(request, 'human_resource/humanresource.html')