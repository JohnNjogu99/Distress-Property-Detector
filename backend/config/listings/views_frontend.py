from django.shortcuts import render
from .models import Property

def property_list_view(request):
    properties = Property.objects.all().order_by('-distress_score')

    search = request.GET.get('search')
    location = request.GET.get('location')

    if search:
        properties = properties.filter(title__icontains=search) | properties.filter(description__icontains=search)
    if location:
        properties = properties.filter(location=location)

    return render(request, 'properties/property_list.html', {
        'properties': properties
    })
