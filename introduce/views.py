from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'introduce/../templates/home/introduce.html')
