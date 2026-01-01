from django.shortcuts import render
def home_view(request): 
    return render(request, "home.html")

def home(request):
    return render(request, 'base.html')

def login_view(request):
    return render(request, 'auth/login.html')

def register_view(request):
    return render(request, 'auth/register.html')

def property_list(request):
    return render(request, 'properties/property_list.html')

def property_detail(request, id):
    return render(request, 'properties/property_detail.html', {'id': id})

def favorites(request):
    return render(request, 'properties/favorites.html')
